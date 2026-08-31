"""Performance and responsiveness coverage for the trace loading path (req_009).

Every capture here is generated on the spot, so the suite carries no recorded
trace and runs identically on CI. Where a claim can be made about bounded work
rather than about wall time it is: a row count or a batch count is the same on
every machine, whereas a stopwatch is not.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QCoreApplication, QElapsedTimer

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis.benchmark import (
    CaptureProfile,
    synthetic_dbc,
    write_synthetic_capture,
)
from peaklive.analysis.profiling import (
    PROFILER,
    RESPONSIVENESS_BUDGET_S,
    RESPONSIVENESS_MEASUREMENT_TOLERANCE_S,
    STAGE_DECODE,
    STAGE_PARSE,
    STAGE_TRACE_PROJECTION,
    STAGES,
    StageProfiler,
)
from peaklive.domain import CanFrame
from peaklive.services.profiles import ProfileStore
from peaklive.services.replay_worker import MAX_PENDING_BATCHES, ReplayWorker
from peaklive.ui import MainWindow
from peaklive.ui.ingest_controller import MAX_ROWS_PER_FLUSH

#: Small enough to stay quick, large enough that coalescing has to engage.
AUDIT_PROFILE = CaptureProfile("audit", 4_000)


def _window(qtbot, tmp_path) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    return window


def _capture(tmp_path, profile: CaptureProfile = AUDIT_PROFILE) -> Path:
    return write_synthetic_capture(tmp_path / f"{profile.name}.asc", profile)


def _synthetic_frames(count: int) -> list[CanFrame]:
    return [CanFrame(index * 0.001, 0x300, index.to_bytes(2, "little") + b"\x00" * 6)
            for index in range(count)]


def _replay(window: MainWindow, capture: Path, qtbot) -> None:
    window._open_trace(capture)
    qtbot.waitUntil(lambda: window._replay_worker is None, timeout=120_000)


# --------------------------------------------------------------------------
# item_036 - AC1: stage-level evidence and a dominant-cost conclusion
# --------------------------------------------------------------------------


def test_a_disabled_profiler_measures_nothing_and_allocates_no_context():
    profiler = StageProfiler()

    first = profiler.stage(STAGE_DECODE)
    with profiler.stage(STAGE_DECODE):
        pass
    profiler.count_frames(10)

    # The same shared no-op is handed out every time, so instrumenting the hot
    # path costs one attribute read rather than an object per frame.
    assert first is profiler.stage(STAGE_PARSE)
    assert profiler.profile().totals == {}
    assert profiler.profile().dominant is None


def test_the_audit_attributes_a_representative_load_to_every_stage(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    dbc = tmp_path / "synthetic.dbc"
    dbc.write_text(synthetic_dbc(AUDIT_PROFILE.message_count), encoding="utf-8")
    window._load_dbc_path(dbc)
    PROFILER.reset()
    PROFILER.enabled = True
    try:
        _replay(window, _capture(tmp_path), qtbot)
        measured = PROFILER.profile()
    finally:
        PROFILER.enabled = False

    assert measured.frames == AUDIT_PROFILE.frames
    for stage in (STAGE_PARSE, STAGE_DECODE, STAGE_TRACE_PROJECTION):
        assert measured.totals.get(stage, 0.0) > 0, f"{stage} was never measured"
    assert measured.dominant in STAGES
    assert measured.overruns() == (), measured.render()


# --------------------------------------------------------------------------
# item_036 - AC2: bounded work, truthful progress, prompt cancellation
# --------------------------------------------------------------------------


def test_one_coalesced_flush_projects_a_bounded_number_of_trace_rows(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    batch = _synthetic_frames(MAX_ROWS_PER_FLUSH * 4)

    window._ingest_frames(batch, coalesce=True)

    # Ingestion is complete the moment the frames land; only the display waits.
    assert len(window._trace) == len(batch)
    assert window.trace_table.rowCount() == 0

    window._flush_presentation()
    assert window.trace_table.rowCount() == MAX_ROWS_PER_FLUSH

    # Settling re-renders the authoritative window from the bounded buffer.
    window._settle_presentation()
    assert window.trace_table.rowCount() == min(len(batch), window._trace.capacity)


def test_the_graphs_repaint_once_per_tick_rather_than_once_per_batch(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    repaints = []
    window.graph_panel.refresh_data = lambda: repaints.append(1)  # type: ignore[method-assign]

    for _ in range(20):
        window._ingest_frames(_synthetic_frames(64), coalesce=True)
        window._mark_graphs_dirty()

    assert repaints == []
    window._flush_presentation()
    # Trace projection owns the first tick; a dirty graph refresh is deferred
    # to the following one so a single event-loop turn stays interactive.
    assert repaints == []
    window._flush_presentation()
    assert len(repaints) == 1


def test_replay_progress_advances_with_the_consumed_source(qtbot, tmp_path):
    capture = _capture(tmp_path)
    worker = ReplayWorker(capture)
    reported: list[tuple[int, int]] = []
    worker.progressed.connect(lambda done, total: reported.append((done, total)))
    # Nothing acknowledges the batches here, so the worker must still land.
    worker.frames_received.connect(lambda _: None)

    with qtbot.waitSignal(worker.finished, timeout=120_000):
        worker.start()

    total = capture.stat().st_size
    assert reported[-1] == (total, total)
    assert [done for done, _ in reported] == sorted(done for done, _ in reported)
    # The old worker reported the file's own size, which is complete from the
    # first batch onwards; real progress has to start below the total.
    assert reported[0][0] < total


def test_a_stopped_replay_stops_within_a_bounded_number_of_batches(qtbot, tmp_path):
    capture = _capture(tmp_path, CaptureProfile("cancellable", 40_000))
    worker = ReplayWorker(capture)
    batches: list[int] = []

    def on_batch(frames):
        batches.append(len(frames))
        if len(batches) == 1:
            worker.request_stop()
        worker.batch_rendered()

    worker.frames_received.connect(on_batch)
    with qtbot.waitSignal(worker.finished, timeout=120_000):
        worker.start()

    # Stop is requested from the first batch, so only the batches already
    # dispatched into the queue may still arrive.
    assert len(batches) <= MAX_PENDING_BATCHES + 1


def test_the_event_loop_is_serviced_within_the_responsiveness_budget(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    capture = _capture(tmp_path, CaptureProfile("responsive", 40_000))
    # Settle one-time widget realization first: what is under test is how long
    # a user action waits behind ingestion, not how long the shell takes to
    # come up.
    QCoreApplication.processEvents()

    window._open_trace(capture)
    passes: list[float] = []
    tick = QElapsedTimer()
    while window._replay_worker is not None:
        tick.restart()
        QCoreApplication.processEvents()
        passes.append(tick.nsecsElapsed() / 1e9)

    slowest = max(passes)
    assert slowest <= RESPONSIVENESS_BUDGET_S + RESPONSIVENESS_MEASUREMENT_TOLERANCE_S, (
        f"slowest pass {slowest * 1000:.0f} ms"
    )


# --------------------------------------------------------------------------
# item_036 - AC7: retention stays bounded
# --------------------------------------------------------------------------


def test_a_large_load_leaves_every_retained_store_inside_its_bound(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    dbc = tmp_path / "synthetic.dbc"
    dbc.write_text(synthetic_dbc(AUDIT_PROFILE.message_count), encoding="utf-8")
    window._load_dbc_path(dbc)

    _replay(window, _capture(tmp_path, CaptureProfile("bounded", 60_000)), qtbot)

    assert len(window._trace) == window._trace.capacity
    assert len(window._frames) == min(60_000, window._frames.capacity)
    assert window.trace_table.rowCount() <= window._trace.capacity
    for name in window._series.names:
        series = window._series.series(name)
        assert len(series) <= series.capacity
