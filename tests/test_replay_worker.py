from PySide6.QtCore import QTimer

from peaklive.services.replay_worker import ReplayWorker


def test_replay_worker_streams_frames_and_retains_anomalies(qtbot, tmp_path):
    trace = tmp_path / "sample.asc"
    trace.write_text(
        "date 2026-01-01\n0.000000 1 123 Rx d 1 01\ninvalid record\n",
        encoding="utf-8",
    )
    worker = ReplayWorker(trace)
    frames: list = []
    events: list = []
    worker.frames_received.connect(frames.extend)
    worker.event_received.connect(events.append)

    worker.start()
    # `isRunning()` becomes false as the worker thread exits, but its queued
    # cross-thread notifications may be delivered on the next GUI event-loop
    # turn. Waiting for the observable contract avoids a Windows-only race.
    qtbot.waitUntil(lambda: len(frames) == 1 and len(events) == 1)
    worker.wait()

    assert len(frames) == 1
    assert events[0].kind == "replay_anomaly"


def test_replay_preserves_tx_remote_declared_dlc_and_extended_identity(qtbot, tmp_path):
    trace = tmp_path / "sample.asc"
    trace.write_text("0.000000 1 18FEF100x Tx r 8\n", encoding="utf-8")
    worker = ReplayWorker(trace)
    frames: list = []
    worker.frames_received.connect(frames.extend)

    worker.start()
    qtbot.waitUntil(lambda: len(frames) == 1)
    worker.wait()

    frame = frames[0]
    assert frame.direction == "tx"
    assert frame.direction_label == "TX"
    assert frame.is_remote_frame is True
    assert frame.is_extended_id is True
    assert frame.dlc == 8
    assert frame.data == b""


def test_replay_backpressure_timeout_is_not_reported_as_success(tmp_path, qtbot):
    trace = tmp_path / "large.asc"
    trace.write_text(
        "\n".join(f"{index / 1000:.6f} 1 123 Rx d 1 01" for index in range(2048)),
        encoding="utf-8",
    )
    worker = ReplayWorker(trace)
    failures: list[str] = []
    progress: list[tuple[int, int]] = []
    worker.replay_failed.connect(failures.append)
    worker.progressed.connect(lambda done, total: progress.append((done, total)))

    worker.start()
    qtbot.waitUntil(lambda: bool(failures), timeout=5_000)
    worker.wait()

    assert worker.succeeded is False
    assert "backpressure" in failures[-1].casefold()
    assert not progress or progress[-1][0] < progress[-1][1]


def test_replay_recovers_when_presentation_acknowledgement_is_slow(tmp_path, qtbot):
    trace = tmp_path / "slow-ui.asc"
    trace.write_text(
        "\n".join(f"{index / 1000:.6f} 1 123 Rx d 1 01" for index in range(2048)),
        encoding="utf-8",
    )
    worker = ReplayWorker(trace)
    failures: list[str] = []
    batches: list[list] = []
    worker.replay_failed.connect(failures.append)

    def acknowledge_later(batch: list) -> None:
        batches.append(batch)
        QTimer.singleShot(400, worker.batch_rendered)

    worker.frames_received.connect(acknowledge_later)

    with qtbot.waitSignal(worker.replay_completed, timeout=10_000):
        worker.start()
    worker.wait()

    assert failures == []
    assert worker.succeeded is True
    assert sum(len(batch) for batch in batches) == 2048
