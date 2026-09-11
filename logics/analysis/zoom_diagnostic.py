"""Read-only capture census and isolated historical-query/Qt scheduling probe.

Run with the project Python and a local ASC path; no payload is printed.
Temporary databases are removed by TemporaryDirectory. This is a diagnostic,
not an end-to-end benchmark of the packaged executable or a DBC decode test.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sqlite3
import tempfile
from collections import Counter
from pathlib import Path
from time import perf_counter

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from peaklive.analysis.history import HistoricalSignalStore
from peaklive.analysis.replay import iter_trace
from peaklive.domain import CanFrame


def timed(fn, repeats=3):
    durations = []
    result = None
    for _ in range(repeats):
        start = perf_counter()
        result = fn()
        durations.append(round((perf_counter() - start) * 1000, 3))
    return result, durations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("capture", type=Path)
    args = parser.parse_args()
    counts = Counter()
    events = Counter()
    first, last = float("inf"), float("-inf")
    for record in iter_trace(args.capture):
        if isinstance(record, CanFrame):
            counts[record.arbitration_id] += 1
            first, last = min(first, record.timestamp), max(last, record.timestamp)
        else:
            events[record.kind] += 1
    print(
        json.dumps(
            {
                "capture_bytes": args.capture.stat().st_size,
                "frames": sum(counts.values()),
                "identifiers": len(counts),
                "start": first,
                "end": last,
                "events": events,
                "top_signal_frame_counts": [n for _, n in counts.most_common(8)],
                "python": platform.python_version(),
                "sqlite": sqlite3.sqlite_version,
            }
        ),
        flush=True,
    )
    selected = counts.most_common(1)[0][0]
    with tempfile.TemporaryDirectory(prefix="peaklive-zoom-probe-") as temporary:
        with HistoricalSignalStore(Path(temporary) / "probe.sqlite3") as history:
            batch = []
            for record in iter_trace(args.capture):
                if (
                    isinstance(record, CanFrame)
                    and record.arbitration_id == selected
                    and record.data
                ):
                    batch.append(("raw_probe", record.timestamp, record.data[0], None))
                    if len(batch) >= 4096:
                        history.append_many(batch)
                        batch.clear()
            history.append_many(batch)
            bounds = history.signal_bounds("raw_probe")
            points, overview_ms = timed(
                lambda: history.overview("raw_probe", *bounds, max_points=4000)
            )
            _, bounds_ms = timed(history.bounds)
            _, exact_ms = timed(lambda: history.exact("raw_probe", bounds[0], bounds[0] + 1))
            print(
                json.dumps(
                    {
                        "probe": "most_frequent_id_raw_byte_zero_not_DBC",
                        "overview_ms": overview_ms,
                        "bounds_ms": bounds_ms,
                        "one_second_exact_ms": exact_ms,
                        "returned_points": len(points),
                        "source_bounds": bounds,
                        "returned_bounds": [points[0][0], points[-1][0]],
                        "timestamps_sorted": all(
                            a[0] <= b[0] for a, b in zip(points, points[1:], strict=False)
                        ),
                        "bounds_query_plan": history._connection.execute(
                            "EXPLAIN QUERY PLAN SELECT MIN(timestamp), MAX(timestamp) FROM samples"
                        ).fetchall(),
                    }
                ),
                flush=True,
            )
            history.append_many(
                ("adversarial", float(i), (0, 10, -10, 1)[i % 4], None) for i in range(400)
            )
            p = history.overview("adversarial", 0, 399, max_points=100)
            print(
                json.dumps(
                    {
                        "adversarial_points": len(p),
                        "last_timestamp": p[-1][0],
                        "expected_last_timestamp": 399,
                        "timestamps_sorted": all(
                            a[0] <= b[0] for a, b in zip(p, p[1:], strict=False)
                        ),
                    }
                ),
                flush=True,
            )
    from PySide6.QtCore import QEventLoop, QTimer
    from PySide6.QtWidgets import QApplication

    from peaklive.ui.panels.graph_stack import GraphStackPanel

    app = QApplication.instance() or QApplication([])
    panel = GraphStackPanel()
    calls = []
    panel.refresh_data = lambda: calls.append(perf_counter())
    for _ in range(30):
        panel.request_view_refresh()
    loop = QEventLoop()
    QTimer.singleShot(250, loop.quit)
    loop.exec()
    print(json.dumps({"refresh_requests": 30, "refresh_callbacks": len(calls)}), flush=True)
    panel.close()
    app.processEvents()


if __name__ == "__main__":
    main()
