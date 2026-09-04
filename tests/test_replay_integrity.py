"""item_063 coverage: bounded replay diagnostics, and no false success.

A malformed-line-per-line anomaly key, an unbounded single physical line, and
an uncaught worker exception could each previously grow memory/UI without
bound or make a failed replay announce "done". Every test here proves one of
those is now bounded or visibly rejected instead.
"""

from __future__ import annotations

from pathlib import Path

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis.replay import TraceCursor, iter_trace
from peaklive.domain import BusEvent
from peaklive.services import replay_worker as replay_worker_module
from peaklive.services.profiles import ProfileStore
from peaklive.services.replay_worker import IMPLAUSIBLE_INPUT_MIN_RECORDS, ReplayWorker
from peaklive.ui import MainWindow


def _window(qtbot, tmp_path) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    return window


# ---- iter_trace: stable anomaly codes, bounded line length ----------------


def test_many_distinct_malformed_lines_all_report_the_same_stable_message(tmp_path):
    trace = tmp_path / "garbage.asc"
    trace.write_text("\n".join(f"not a can record {i}" for i in range(2_000)) + "\n")

    anomalies = [
        record
        for record in iter_trace(trace)
        if isinstance(record, BusEvent) and record.kind == "replay_anomaly"
    ]

    assert len(anomalies) == 2_000
    assert {record.message for record in anomalies} == {"Unsupported record"}


def test_a_line_far_longer_than_any_real_record_is_read_in_bounded_slices(tmp_path):
    trace = tmp_path / "binary_like.asc"
    # No newline anywhere: a naive line iterator would buffer the whole file.
    trace.write_text("x" * (5 * 70_000))

    cursor = TraceCursor()
    records = list(iter_trace(trace, cursor))

    assert len(records) > 1
    assert all(len(chunk.message) < 70_000 for chunk in records)
    assert cursor.consumed == 5 * 70_000


# ---- ReplayWorker: bounded aggregation, implausible-input rejection -------


def _run_worker(worker: ReplayWorker, qtbot) -> tuple[list, list]:
    events: list = []
    failures: list = []
    worker.event_received.connect(events.append)
    worker.replay_failed.connect(failures.append)
    worker.frames_received.connect(lambda batch: worker.batch_rendered())
    # `isRunning()` reflects the OS thread, not whether Qt has delivered the
    # queued signals that thread emitted just before returning; waiting on
    # `finished` itself is what guarantees every prior emission was drained.
    with qtbot.waitSignal(worker.finished, timeout=5_000):
        worker.start()
    return events, failures


def test_worker_aggregates_thousands_of_shaped_anomalies_into_one_bounded_event(qtbot, tmp_path):
    lines = ["date Mon Jan 01 00:00:00 2026", "base hex  timestamps absolute"]
    # A mostly-garbage capture, but plausible enough (~91% anomalies) that the
    # implausible-input threshold does not short-circuit it: aggregation must
    # stay bounded on its own even when many anomalies really do get parsed.
    for index in range(5_000):
        lines.append(f"garbage line {index}")
        if index % 9 == 0:
            lines.append(f"   {index}.000000 1  123             Rx   d 2 D2 04")
    trace = tmp_path / "garbage.asc"
    trace.write_text("\n".join(lines) + "\n")
    worker = ReplayWorker(trace)

    events, failures = _run_worker(worker, qtbot)

    assert not failures
    anomaly_events = [event for event in events if event.kind == "replay_anomaly"]
    assert len(anomaly_events) == 1
    assert "5000 occurrences" in anomaly_events[0].message
    assert worker.succeeded


def test_binary_like_input_is_rejected_and_never_reports_replay_complete(qtbot, tmp_path):
    trace = tmp_path / "not_a_trace.asc"
    trace.write_bytes(bytes(range(256)) * (IMPLAUSIBLE_INPUT_MIN_RECORDS * 4))
    worker = ReplayWorker(trace)

    events, failures = _run_worker(worker, qtbot)

    assert failures
    assert "does not look like a supported trace" in failures[0]
    assert not worker.succeeded
    assert not any(
        event.kind == "replay_anomaly" and "occurrences" in event.message for event in events
    )


def test_a_mostly_valid_capture_with_a_few_bad_lines_is_never_rejected(qtbot, tmp_path):
    lines = ["date Mon Jan 01 00:00:00 2026", "base hex  timestamps absolute"]
    for index in range(600):
        lines.append(f"   {index}.000000 1  123             Rx   d 2 D2 04")
    lines.append("this line is malformed")
    trace = tmp_path / "mostly_valid.asc"
    trace.write_text("\n".join(lines) + "\n")
    worker = ReplayWorker(trace)

    events, failures = _run_worker(worker, qtbot)

    assert not failures
    assert worker.succeeded


def test_an_unexpected_parse_exception_is_caught_and_never_marks_success(
    qtbot, tmp_path, monkeypatch
):
    def _boom(path: Path, cursor=None):
        raise ValueError("synthetic parser bug")
        yield  # pragma: no cover - makes this a generator function

    monkeypatch.setattr(replay_worker_module, "iter_trace", _boom)
    trace = tmp_path / "capture.asc"
    trace.write_text("0.0 1 123 Rx d 0\n")
    worker = ReplayWorker(trace)

    events, failures = _run_worker(worker, qtbot)

    assert failures == ["synthetic parser bug"]
    assert not worker.succeeded


# ---- MainWindow: a failed replay never announces "done" -------------------


def test_a_rejected_trace_never_shows_replay_done(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    trace = tmp_path / "not_a_trace.asc"
    trace.write_bytes(bytes(range(256)) * (IMPLAUSIBLE_INPUT_MIN_RECORDS * 4))

    window._open_trace(trace)
    qtbot.waitUntil(lambda: window._replay_worker is None, timeout=5_000)

    assert not window.progress.isVisible()
    assert "complete" not in window.status.currentMessage().lower()
    assert window.acquisition_bar.bus_state == "bus_error"
