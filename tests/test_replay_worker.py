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
