"""item_143 - replay never waits for historical writer capacity on the GUI thread.

`_drain_replay_batch` used to pop a batch and then call `HistoryWriter.submit`,
which blocks the caller while the writer's bounded queue is full. On a slow but
perfectly healthy disk that stalled the event loop for as long as the queue took
to drain, with no paint and no input processed: the replay half of the freeze the
operator reported. A mixed frame/event batch makes it worse, because one batch
submits once per frame group, so a single capacity check before the batch cannot
keep the later groups off the blocking path.

These tests measure the GUI heartbeat across a replay whose persistence is
deliberately slow, and pin the ordering, exactness and containment contracts that
deferring admission must not weaken.
"""

from __future__ import annotations

from time import monotonic, sleep

from PySide6.QtCore import QTimer

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis.benchmark import CaptureProfile, synthetic_dbc, write_synthetic_capture
from peaklive.analysis.history import HistoricalSignalStore
from peaklive.analysis.profiling import PROFILER, STAGE_QUEUE_WAIT
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow

#: The interval the AC is measured at, and the gap it allows.
HEARTBEAT_MS = 50
MAX_HEARTBEAT_GAP_S = 0.250

#: Twelve replay batches: enough to fill the writer's eight-batch queue and
#: keep it full while the slowed store works through the backlog.
PROFILE = CaptureProfile("backpressure", 3_072, message_count=3)

#: What one persisted batch costs on a deliberately slow disk. Twelve of these
#: against an eight-deep queue keep the queue full for most of the replay.
SLOW_WRITE_S = 0.12

#: All the time the GUI thread may spend inside `HistoryWriter.submit` across
#: the whole replay. Admission is checked before the call, so each `put` lands
#: in a queue with known room; a caller that waits for capacity instead pays
#: the writer's drain here and accumulates whole seconds.
MAX_TOTAL_QUEUE_WAIT_S = 0.05


class Heartbeat:
    """Records UI-thread timer ticks, so 'still responsive' is a measurement.

    Each tick also records whether replay was admitting batches at that
    moment. Only those intervals are this file's subject: settling a finished
    replay re-renders the whole trace window in one go, which is a documented
    cost of a different stage (`trace_projection`, which carries its own
    Windows budget) and not something admission decides.
    """

    def __init__(self, window: MainWindow) -> None:
        self._window = window
        self.marks: list[tuple[float, bool]] = [(monotonic(), False)]
        self._timer = QTimer()
        self._timer.setInterval(HEARTBEAT_MS)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self) -> None:
        admitting = bool(
            self._window._pending_replay_batches or self._window._replay_worker is not None
        )
        self.marks.append((monotonic(), admitting))

    def stop(self) -> None:
        self._timer.stop()

    def max_admitting_gap(self) -> float:
        """The longest interval that began while a batch was being admitted."""
        gaps = [
            later - earlier
            for (earlier, admitting), (later, _) in zip(self.marks, self.marks[1:], strict=False)
            if admitting
        ]
        return max(gaps, default=0.0)


def _slow_history_writes(monkeypatch, seconds: float) -> None:
    """Make each persisted batch cost what a dense capture costs on a slow disk."""
    original = HistoricalSignalStore.append_many

    def slow_append(self, batch):  # type: ignore[no-untyped-def]
        sleep(seconds)
        return original(self, batch)

    monkeypatch.setattr(HistoricalSignalStore, "append_many", slow_append)


def _window(qtbot, tmp_path) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    window.selected_profile.recording.enabled = False
    qtbot.addWidget(window)
    dbc = tmp_path / "synthetic.dbc"
    dbc.write_text(synthetic_dbc(PROFILE.message_count), encoding="utf-8")
    window._load_dbc_path(dbc)
    for index in range(PROFILE.message_count):
        window._signal_shown_changed(f"Synth{index}.Counter{index}", True)
    return window


def _replay(window, tmp_path, qtbot, timeout_ms: int = 120_000):
    capture = write_synthetic_capture(tmp_path / "capture.asc", PROFILE)
    window._open_trace(capture)
    qtbot.waitUntil(
        lambda: window._historical_view_ready or window._history_failed,
        timeout=timeout_ms,
    )


# --------------------------------------------------------------------------
# AC1 - a slow-but-progressing writer saturates the queue, not the event loop
# --------------------------------------------------------------------------


def test_replaying_onto_slow_persistence_never_waits_for_writer_capacity(
    qtbot, tmp_path, monkeypatch
):
    """Measure the wait itself, not a symptom of it.

    `queue_wait` is the stage around `HistoryWriter.submit`, so it is exactly
    the time the GUI thread spends asking for room. Reading it directly keeps
    this regression independent of how loaded the machine running it is, which
    a wall-clock heartbeat on a saturated test host is not.
    """
    _slow_history_writes(monkeypatch, SLOW_WRITE_S)
    window = _window(qtbot, tmp_path)
    PROFILER.reset()
    PROFILER.enabled = True
    try:
        _replay(window, tmp_path, qtbot)
        waited = PROFILER.profile().totals.get(STAGE_QUEUE_WAIT, 0.0)
    finally:
        PROFILER.enabled = False

    assert not window._history_failed, window._history_failure_message
    assert waited <= MAX_TOTAL_QUEUE_WAIT_S, f"GUI thread waited {waited:.3f}s for queue room"


def test_replaying_onto_slow_persistence_never_blocks_the_event_loop(
    qtbot, tmp_path, monkeypatch
):
    _slow_history_writes(monkeypatch, SLOW_WRITE_S)
    window = _window(qtbot, tmp_path)
    heartbeat = Heartbeat(window)

    _replay(window, tmp_path, qtbot)
    gap = heartbeat.max_admitting_gap()
    heartbeat.stop()

    assert not window._history_failed, window._history_failure_message
    assert gap <= MAX_HEARTBEAT_GAP_S, f"event loop stalled for {gap:.3f}s while admitting"


# --------------------------------------------------------------------------
# AC2 - exact order, counts and permits survive deferred admission
# --------------------------------------------------------------------------


def test_a_deferred_batch_is_projected_exactly_once_and_in_source_order(
    qtbot, tmp_path, monkeypatch
):
    _slow_history_writes(monkeypatch, SLOW_WRITE_S)
    window = _window(qtbot, tmp_path)

    _replay(window, tmp_path, qtbot)

    assert not window._history_failed, window._history_failure_message
    assert window._facts.report().frame_count == PROFILE.frames
    # Resuming a half-consumed batch must not replay the groups already applied:
    # the retained tail carries one unbroken run of session sequence numbers.
    sequences = [record.frame_number for record in window._trace if record.is_frame]
    assert sequences == list(range(PROFILE.frames - len(sequences) + 1, PROFILE.frames + 1))
    assert not window._pending_replay_batches
    assert window._history_batches_submitted == window._history_batches_settled


def test_completion_waits_for_the_last_deferred_record_to_settle(
    qtbot, tmp_path, monkeypatch
):
    _slow_history_writes(monkeypatch, SLOW_WRITE_S)
    window = _window(qtbot, tmp_path)

    _replay(window, tmp_path, qtbot)

    assert window._historical_view_ready
    assert window._history_fully_drained()
    bounds = window._history.bounds()
    assert bounds is not None
    samples = window._history.exact("Synth1.Counter1", bounds[0], bounds[1], limit=PROFILE.frames)
    assert len(samples) == PROFILE.frames // PROFILE.message_count
    assert [timestamp for timestamp, _ in samples] == sorted(
        timestamp for timestamp, _ in samples
    )


# --------------------------------------------------------------------------
# AC3 - a writer that never drains is still contained, without a GUI wait
# --------------------------------------------------------------------------


def test_a_never_draining_writer_fails_the_replay_instead_of_stalling(
    qtbot, tmp_path, monkeypatch
):
    # Shorter than the replay worker's own 2 s permit-stall budget, so this
    # proves the history stall bound fires rather than the transport's.
    monkeypatch.setattr("peaklive.ui.replay_admission.QUEUE_STALL_TIMEOUT_S", 0.3)
    window = _window(qtbot, tmp_path)
    monkeypatch.setattr(type(window._history_writer), "has_room", lambda self: False)
    heartbeat = Heartbeat(window)

    _replay(window, tmp_path, qtbot, timeout_ms=30_000)
    gap = heartbeat.max_admitting_gap()
    heartbeat.stop()

    assert window._history_failed
    assert not window._historical_view_ready
    assert gap <= MAX_HEARTBEAT_GAP_S, f"event loop stalled for {gap:.3f}s while admitting"
    assert not window._pending_replay_batches
