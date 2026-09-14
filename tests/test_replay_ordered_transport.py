"""item_131: frames and valid bus events share one ordered, bounded transport.

Before this fix, `ReplayWorker` emitted `frames_received` and `event_received`
as two independent, differently-bounded channels: a bus event bypassed the
four-permit `frames_received` semaphore entirely and could reach the GUI
ahead of frames that preceded it in the source file. These tests reproduce
the audit's exact counterexample (frame(0.000), event(0.001), frame(0.002))
and the 10000-event flood, and prove both are now bounded/ordered by the
single `records_received` transport.
"""

from __future__ import annotations

from peaklive.domain import BusEvent, CanFrame
from peaklive.services.replay_worker import BATCH_SIZE, MAX_PENDING_BATCHES, ReplayWorker


def test_a_mixed_frame_event_frame_capture_is_observed_in_source_order(qtbot, tmp_path):
    trace = tmp_path / "mixed.asc"
    trace.write_text(
        "0.000 1 123 Rx d 1 01\n0.001 1 ErrorFrame\n0.002 1 123 Rx d 1 02\n",
        encoding="utf-8",
    )
    worker = ReplayWorker(trace)
    order: list[tuple[str, float]] = []

    def on_records(records: list) -> None:
        for record in records:
            if isinstance(record, BusEvent):
                order.append(("event", record.timestamp))
            else:
                order.append(("frame", record.timestamp))
        worker.batch_rendered()

    worker.records_received.connect(on_records)

    with qtbot.waitSignal(worker.replay_completed, timeout=5_000):
        worker.start()
    worker.wait()

    assert order == [("frame", 0.0), ("event", 0.001), ("frame", 0.002)]


def test_10000_valid_events_cannot_bypass_transport_capacity_without_acknowledgement(
    qtbot, tmp_path
):
    trace = tmp_path / "event_flood.asc"
    trace.write_text(
        "".join(f"{index * 0.001:.3f} 1 ErrorFrame\n" for index in range(10_000)),
        encoding="utf-8",
    )
    worker = ReplayWorker(trace)
    seen_events: list[BusEvent] = []
    worker.records_received.connect(
        lambda records: seen_events.extend(r for r in records if isinstance(r, BusEvent))
    )

    worker.start()
    # No acknowledgement is ever sent: the worker must stall behind its bounded
    # permits rather than deliver all 10000 events unbounded.
    qtbot.wait(500)

    assert worker.isRunning()
    assert worker.pending_batch_count <= MAX_PENDING_BATCHES
    assert len(seen_events) <= MAX_PENDING_BATCHES * BATCH_SIZE

    worker.request_stop()
    worker.wait(5_000)


def test_event_only_and_mixed_loads_retain_exact_counts_after_drain(qtbot, tmp_path):
    lines = []
    for index in range(600):
        if index % 3 == 0:
            lines.append(f"{index * 0.001:.3f} 1 ErrorFrame")
        else:
            lines.append(f"{index * 0.001:.3f} 1 123 Rx d 1 01")
    trace = tmp_path / "mixed_bulk.asc"
    trace.write_text("\n".join(lines) + "\n", encoding="utf-8")
    worker = ReplayWorker(trace)
    frames: list[CanFrame] = []
    events: list[BusEvent] = []

    def on_records(records: list) -> None:
        for record in records:
            if isinstance(record, BusEvent):
                events.append(record)
            else:
                frames.append(record)
        worker.batch_rendered()

    worker.records_received.connect(on_records)

    with qtbot.waitSignal(worker.replay_completed, timeout=10_000):
        worker.start()
    worker.wait()

    assert worker.succeeded
    assert worker.pending_batch_count == 0
    expected_events = sum(1 for index in range(600) if index % 3 == 0)
    expected_frames = 600 - expected_events
    assert len(events) == expected_events
    assert len(frames) == expected_frames
