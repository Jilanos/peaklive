"""Synthetic follow-up audit; no private captures or application edits.

Run: QT_QPA_PLATFORM=offscreen uv run --python 3.13 python
     logics/analysis/trace_load_followup_probe.py --frames 20000 --signals 0 1 8 16
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QApplication

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis.benchmark import CaptureProfile, synthetic_dbc, write_synthetic_capture
from peaklive.analysis.profiling import PROFILER
from peaklive.domain import CanFrame
from peaklive.services.profiles import ProfileStore
from peaklive.services.replay_worker import ReplayWorker
from peaklive.ui import MainWindow


def measure(root: Path, frames: int, selected: int, shown: bool = False) -> dict:
    capture = write_synthetic_capture(root / "synthetic.asc", CaptureProfile("audit", frames))
    dbc = root / "synthetic.dbc"
    dbc.write_text(synthetic_dbc(), encoding="utf-8")
    window = MainWindow(ProfileStore(root / f"settings-{selected}"), FakeCanAdapter)
    window._load_dbc_path(dbc)
    window._selected_signal_names = set(window._catalog.signal_names()[:selected])
    window._sync_graphs()
    if shown:
        window.resize(1280, 720)
        window.show()
    QCoreApplication.processEvents()
    history_elapsed = 0.0
    history_calls = 0
    original = window._history.append_many

    def timed_append(samples):
        nonlocal history_elapsed, history_calls
        start = perf_counter()
        try:
            return original(samples)
        finally:
            history_elapsed += perf_counter() - start
            history_calls += 1

    window._history.append_many = timed_append
    PROFILER.reset()
    PROFILER.enabled = True
    errors = []
    start = perf_counter()
    window._open_trace(capture)
    worker = window._replay_worker
    worker.replay_failed.connect(errors.append)
    ticks = []
    while window._replay_worker is not None and perf_counter() - start < 180:
        tick = perf_counter()
        QCoreApplication.processEvents()
        ticks.append(perf_counter() - tick)
    wall = perf_counter() - start
    profile = PROFILER.profile()
    PROFILER.enabled = False
    connection = window._history._connection
    counts = {
        name: connection.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        for name in ("samples", "summary", "events")
    }
    # Cost of synchronous metadata queries still issued on historical refresh.
    metadata_start = perf_counter()
    for _ in range(10):
        window._history.bounds()
        window._history.data_revision()
    metadata_ms = (perf_counter() - metadata_start) * 100
    result = {
        "frames": frames,
        "selected": selected,
        "shown": shown,
        "succeeded": worker.succeeded,
        "pending_batches": worker.pending_batch_count,
        "errors": errors,
        "wall_s": round(wall, 4),
        "max_event_pass_ms": round(max(ticks, default=0) * 1000, 3),
        "history_s": round(history_elapsed, 4),
        "history_calls": history_calls,
        "profile_s": {key: round(value, 4) for key, value in profile.totals.items()},
        "profile_frames": profile.frames,
        "sqlite_counts": counts,
        "sqlite_bytes": window._history.path.stat().st_size,
        "source_bytes": capture.stat().st_size,
        "metadata_pair_mean_ms": round(metadata_ms, 3),
    }
    window.close()
    QCoreApplication.processEvents()
    return result


def fault_probes(root: Path) -> None:
    path = root / "mixed.asc"
    path.write_text("0.000 1 123 Rx d 1 01\n0.001 1 ErrorFrame\n0.002 1 123 Rx d 1 02\n")
    worker = ReplayWorker(path)
    order = []
    worker.frames_received.connect(
        lambda frames: (
            order.extend(("frame", frame.timestamp) for frame in frames),
            worker.batch_rendered(),
        )
    )
    worker.event_received.connect(lambda event: order.append(("event", event.timestamp)))
    worker.run()
    print(json.dumps({"mixed_source_delivery": order}), flush=True)
    path.write_text("".join(f"{i * .001:.3f} 1 ErrorFrame\n" for i in range(10_000)))
    worker = ReplayWorker(path)
    events = []
    worker.event_received.connect(events.append, Qt.ConnectionType.DirectConnection)
    worker.start()
    worker.wait(5000)
    print(json.dumps({"event_only_without_ack": {
        "events": len(events), "pending": worker.pending_batch_count,
        "succeeded": worker.succeeded,
    }}), flush=True)
    window = MainWindow(ProfileStore(root / "fault-settings"), FakeCanAdapter)
    dbc = root / "fault.dbc"
    dbc.write_text(synthetic_dbc(), encoding="utf-8")
    window._load_dbc_path(dbc)

    class Permit:
        acked = 0

        def batch_rendered(self):
            self.acked += 1

    permit = Permit()
    window._history._connection.execute("PRAGMA query_only=ON")
    window._pending_replay_batches = [
        (window._replay_generation, permit, [CanFrame(0, 0x300, bytes(8))])
    ]
    try:
        window._drain_replay_batch()
    except sqlite3.OperationalError as error:
        print(json.dumps({"sqlite_failure": {
            "error": str(error), "acked": permit.acked,
            "trace_rows": len(window._trace), "cached_frames": len(window._frames),
            "queued_batches": len(window._pending_replay_batches),
            "timer_active": window._replay_presentation_timer.isActive(),
        }}), flush=True)
    finally:
        window._history._connection.execute("PRAGMA query_only=OFF")
        window.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames", type=int, default=20_000)
    parser.add_argument("--signals", type=int, nargs="+", default=[0, 1, 8, 16])
    parser.add_argument("--shown", action="store_true")
    parser.add_argument("--faults", action="store_true")
    args = parser.parse_args()
    app = QApplication.instance() or QApplication([])
    with TemporaryDirectory(prefix="peaklive-audit-") as directory:
        if args.faults:
            fault_probes(Path(directory))
        else:
            for count in args.signals:
                result = measure(Path(directory), args.frames, count, args.shown)
                print(json.dumps(result), flush=True)
    app.processEvents()


if __name__ == "__main__":
    main()
