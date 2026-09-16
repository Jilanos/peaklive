"""item_139 - a responsive, honest acquisition wind-down.

Stop used to settle the whole live presentation queue inside the worker's
`finished` slot. Every queued slice cost a full curve repaint and could block
for the historical writer's entire backpressure budget, with no paint and no
input processed for the duration: the freeze the operator reported. These
tests measure the GUI heartbeat across a Stop on a saturated bus whose
persistence is deliberately slow, and pin the contract that a wind-down never
reports success before the history it accepted is durably written.
"""

from __future__ import annotations

from time import monotonic, sleep

from PySide6.QtCore import QTimer

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis.history import HistoricalSignalStore
from peaklive.domain import CanFrame
from peaklive.services.lifecycle import AcquisitionPhase
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow

#: The heartbeat interval the AC is measured at, and the gap it allows.
HEARTBEAT_MS = 50
MAX_HEARTBEAT_GAP_S = 0.250
#: The AC's click-to-feedback budget.
MAX_FEEDBACK_S = 0.200

LANES = 4
BASE_ID = 0x300

BENCH_DBC = 'VERSION ""\nNS_ :\nBS_:\nBU_: ECU\n' + "".join(
    f"BO_ {BASE_ID + index} Msg{index:02d}: 8 ECU\n"
    ' SG_ Value : 0|16@1+ (0.1,0) [0|6000] "unit" ECU\n'
    for index in range(LANES)
)


class BurstAdapter(FakeCanAdapter):
    """A saturated bus substitute; no physical CAN adapter is required."""

    def receive(self, timeout: float) -> CanFrame | None:
        if not self.connected:
            return None
        sequence = next(self._sequence)
        return CanFrame(
            timestamp=monotonic(),
            arbitration_id=BASE_ID + sequence % LANES,
            data=sequence.to_bytes(8, "little"),
            channel=self._profile.channel if self._profile else "channel-1",
        )


class Heartbeat:
    """Records UI-thread timer ticks, so 'still responsive' is a measurement."""

    def __init__(self) -> None:
        self.marks = [monotonic()]
        self._timer = QTimer()
        self._timer.setInterval(HEARTBEAT_MS)
        self._timer.timeout.connect(lambda: self.marks.append(monotonic()))
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def max_gap(self, since: float) -> float:
        marks = [mark for mark in self.marks if mark >= since] + [monotonic()]
        return max(b - a for a, b in zip(marks, marks[1:], strict=False))


def _slow_history_writes(monkeypatch, seconds: float) -> None:
    """Make each persisted batch cost what a dense capture costs on a slow disk."""
    original = HistoricalSignalStore.append_many

    def slow_append(self, batch):  # type: ignore[no-untyped-def]
        sleep(seconds)
        return original(self, batch)

    monkeypatch.setattr(HistoricalSignalStore, "append_many", slow_append)


def _bench_window(qtbot, tmp_path, adapter=None) -> MainWindow:
    adapter = adapter or BurstAdapter()
    tmp_path.mkdir(parents=True, exist_ok=True)
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=lambda: adapter)
    window.selected_profile.recording.enabled = False
    qtbot.addWidget(window)
    path = tmp_path / "bench.dbc"
    path.write_text(BENCH_DBC, encoding="utf-8")
    window._load_dbc_path(path)
    for index in range(LANES):
        window._signal_shown_changed(f"Msg{index:02d}.Value", True)
    return window


def _run_then_stop(qtbot, window, *, seconds: float = 1.5):
    """Saturate the bus, then Stop, returning the click time and the heartbeat."""
    heartbeat = Heartbeat()
    window._start_acquisition()
    qtbot.waitUntil(lambda: window._lifecycle.phase is AcquisitionPhase.RUNNING, timeout=5_000)
    qtbot.wait(int(seconds * 1000))
    clicked = monotonic()
    window._stop_acquisition()
    return clicked, heartbeat


def _wait_for_wind_down(qtbot, window, timeout_ms: int = 120_000) -> None:
    qtbot.waitUntil(
        lambda: window._worker is None and window._finalizing_generation is None,
        timeout=timeout_ms,
    )


# --------------------------------------------------------------------------
# AC2 - feedback, a visible saving indicator, and an event loop that keeps running
# --------------------------------------------------------------------------


def test_stopping_a_saturated_acquisition_never_blocks_the_event_loop(
    qtbot, tmp_path, monkeypatch
):
    _slow_history_writes(monkeypatch, 0.08)
    window = _bench_window(qtbot, tmp_path)

    clicked, heartbeat = _run_then_stop(qtbot, window)
    feedback = monotonic()
    assert window._lifecycle.phase is not AcquisitionPhase.RUNNING
    assert feedback - clicked < MAX_FEEDBACK_S

    _wait_for_wind_down(qtbot, window)
    gap = heartbeat.max_gap(clicked)
    heartbeat.stop()

    assert gap <= MAX_HEARTBEAT_GAP_S, f"GUI stalled for {gap * 1000:.0f} ms during stop"


def test_the_wind_down_shows_a_saving_indicator_and_removes_it_only_when_done(
    qtbot, tmp_path, monkeypatch
):
    _slow_history_writes(monkeypatch, 0.08)
    window = _bench_window(qtbot, tmp_path)
    window.show()
    qtbot.waitExposed(window)

    clicked, heartbeat = _run_then_stop(qtbot, window)
    qtbot.waitUntil(lambda: window.progress.isVisible(), timeout=3_000)
    assert monotonic() - clicked < 3.0
    assert window.progress.format()

    _wait_for_wind_down(qtbot, window)
    heartbeat.stop()

    assert not window.progress.isVisible()


def test_a_stop_reports_success_only_once_every_accepted_batch_is_durable(
    qtbot, tmp_path, monkeypatch
):
    _slow_history_writes(monkeypatch, 0.08)
    window = _bench_window(qtbot, tmp_path)

    _, heartbeat = _run_then_stop(qtbot, window)
    _wait_for_wind_down(qtbot, window)
    heartbeat.stop()

    assert window._history_batches_submitted > 0
    assert window._history_batches_settled == window._history_batches_submitted
    assert not window._history_failed
    assert window._lifecycle.phase is AcquisitionPhase.STOPPED
    assert window.start_button.isEnabled()


def test_the_wind_down_is_gated_against_an_unsafe_restart(qtbot, tmp_path, monkeypatch):
    _slow_history_writes(monkeypatch, 0.08)
    window = _bench_window(qtbot, tmp_path)

    _, heartbeat = _run_then_stop(qtbot, window)
    qtbot.waitUntil(lambda: window._finalizing_generation is not None, timeout=10_000)
    generation = window._lifecycle.generation
    window._start_acquisition()

    assert window._lifecycle.generation == generation
    assert not window.start_button.isEnabled()

    _wait_for_wind_down(qtbot, window)
    heartbeat.stop()
    assert window.start_button.isEnabled()


# --------------------------------------------------------------------------
# AC1 - Follow live is not what decides how the wind-down behaves
# --------------------------------------------------------------------------


def test_every_follow_configuration_winds_down_within_the_same_budget(
    qtbot, tmp_path, monkeypatch
):
    _slow_history_writes(monkeypatch, 0.08)
    gaps = {}
    for index, (follow, mode) in enumerate(
        ((False, "full"), (True, "full"), (True, "trailing"))
    ):
        window = _bench_window(qtbot, tmp_path / f"follow-{index}")
        window.graph_panel.set_follow_live(follow)
        window.graph_panel.set_follow_live_mode(mode)

        clicked, heartbeat = _run_then_stop(qtbot, window, seconds=1.0)
        _wait_for_wind_down(qtbot, window)
        gaps[(follow, mode)] = heartbeat.max_gap(clicked)
        heartbeat.stop()
        window.close()

    assert max(gaps.values()) <= MAX_HEARTBEAT_GAP_S, gaps


# --------------------------------------------------------------------------
# AC3 - terminal state: settled data, a still viewport, no live-update loop
# --------------------------------------------------------------------------


def test_a_stopped_session_keeps_its_samples_and_stops_updating_them(qtbot, tmp_path):
    window = _bench_window(qtbot, tmp_path)

    _, heartbeat = _run_then_stop(qtbot, window, seconds=0.5)
    _wait_for_wind_down(qtbot, window)
    heartbeat.stop()

    settled = window._facts.report().frame_count
    assert settled > 0
    assert not window._presentation_queue_pending()
    window.graph_panel.set_follow_live(False)
    window.graph_panel.zoom(0.5)
    chosen = window.graph_panel.visible_window()
    qtbot.wait(200)

    assert window._facts.report().frame_count == settled
    assert window.graph_panel.visible_window() == chosen


def test_an_empty_acquisition_and_repeated_cycles_stay_restartable(qtbot, tmp_path):
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    window.selected_profile.recording.enabled = False
    qtbot.addWidget(window)

    for _ in range(3):
        window._start_acquisition()
        qtbot.waitUntil(
            lambda: window._lifecycle.phase is AcquisitionPhase.RUNNING, timeout=5_000
        )
        window._stop_acquisition()
        _wait_for_wind_down(qtbot, window, timeout_ms=15_000)
        assert window._lifecycle.phase is AcquisitionPhase.STOPPED
        assert window.start_button.isEnabled()
        assert not window.progress.isVisible()


# --------------------------------------------------------------------------
# AC3 - a writer that never drains is surfaced, not waited on forever
# --------------------------------------------------------------------------


def test_a_history_writer_that_never_drains_fails_the_wind_down_explicitly(
    qtbot, tmp_path, monkeypatch
):
    monkeypatch.setattr("peaklive.ui.ingest_controller.QUEUE_STALL_TIMEOUT_S", 0.2)
    window = _bench_window(qtbot, tmp_path)
    _, heartbeat = _run_then_stop(qtbot, window, seconds=0.3)

    writer = window._history_writer
    assert writer is not None
    monkeypatch.setattr(writer, "has_room", lambda: False)
    _wait_for_wind_down(qtbot, window, timeout_ms=20_000)
    heartbeat.stop()

    assert window._history_failed
    assert window.session_note.level == "error"
    assert window.start_button.isEnabled()


def test_a_blocking_stop_never_starves_a_queued_ui_callback(qtbot, tmp_path, monkeypatch):
    """A Stop must not push an ordinary UI callback behind the whole drain."""
    _slow_history_writes(monkeypatch, 0.08)
    window = _bench_window(qtbot, tmp_path)
    fired: list[float] = []

    clicked, heartbeat = _run_then_stop(qtbot, window)
    QTimer.singleShot(50, lambda: fired.append(monotonic()))
    qtbot.waitUntil(lambda: bool(fired), timeout=2_000)
    _wait_for_wind_down(qtbot, window)
    heartbeat.stop()

    assert fired[0] - clicked < MAX_FEEDBACK_S + 0.05
