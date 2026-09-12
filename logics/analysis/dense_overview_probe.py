"""Read-only source/render diagnosis; never prints capture payloads or identifiers.

Run with project Python; optionally pass --capture PRIVATE_ASC.
All SQLite stores are temporary. Values are synthetic, even with real timestamps.
This is not a DBC-level or packaged-executable reproduction.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from time import perf_counter

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pyqtgraph as pg
from PySide6.QtWidgets import QApplication

from peaklive.analysis.history import HistoricalSignalStore, historical_points
from peaklive.analysis.replay import iter_trace
from peaklive.domain import CanFrame


def emit(**data):
    print(json.dumps(data), flush=True)


def source_times(path):
    counts = Counter()
    frames = 0
    for record in iter_trace(path):
        if isinstance(record, CanFrame):
            counts[(record.channel, record.arbitration_id, record.is_extended_id)] += 1
            frames += 1
    key, count = counts.most_common(1)[0]
    timestamps = [
        record.timestamp
        for record in iter_trace(path)
        if isinstance(record, CanFrame)
        and (record.channel, record.arbitration_id, record.is_extended_id) == key
    ]
    emit(capture_bytes=path.stat().st_size, frames=frames, identifiers=len(counts),
         probe_samples=count, span=timestamps[-1] - timestamps[0])
    return timestamps


def render(points, span, width=1000, auto=True):
    plot = pg.PlotWidget()
    plot.resize(width, 240)
    plot.show()
    QApplication.processEvents()
    plot.setXRange(*span, padding=0)
    curve = plot.plot()
    curve.setClipToView(True)
    curve.setDownsampling(auto=auto, method="peak")
    curve.setData([p[0] for p in points], [p[1] for p in points])
    x, _ = curve.getData()
    result = dict(rendered_points=len(x), downsample_factor=curve._adsLastValue,
                  view_width_px=round(plot.getViewBox().width(), 1))
    plot.close()
    plot.deleteLater()
    QApplication.processEvents()
    return result


def run_case(times, tail):
    rows = [("probe", t, i % 17, None) for i, t in enumerate(times)]
    with HistoricalSignalStore() as history:
        if tail:
            history.append_many(rows[:-tail])
            history.append_many(rows[-tail:])
        else:
            history.append_many(rows)
        bounds = history.bounds()
        summary_rows = history._connection.execute("SELECT COUNT(*) FROM summary").fetchone()[0]
        for span in (60, 199, 500, 640, 650, 660, bounds[1] - bounds[0]):
            visible = (max(bounds[0], bounds[1] - span), bounds[1])
            start = perf_counter()
            points = historical_points(history, "probe", bounds, visible)
            emit(case="bulk_plus_tail", tail=tail, span=span, source_samples=len(rows),
                 summary_rows=summary_rows, returned_points=len(points),
                 returned_bounds=[points[0][0], points[-1][0]] if points else None,
                 query_ms=round((perf_counter() - start) * 1000, 2),
                 **render(points, visible))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", type=Path)
    args = parser.parse_args()
    app = QApplication.instance() or QApplication([])
    times = source_times(args.capture) if args.capture else [i / 100 for i in range(94_501)]
    for tail in (0, 1, 16):
        run_case(times, tail)
    for width in (500, 1000):
        for auto in (True, False):
            emit(case="sparse_summary_wide_view", width=width, auto=auto,
                 **render([(944.97, 0), (944.98, 10), (944.99, -10)], (0, 945), width, auto))
    with HistoricalSignalStore() as history:
        history.append_many([("probe", 0, 1, None), ("probe", 1, 2, None)])
        before = history.overview("probe", 0, 1)
        history.clear()
        emit(case="clear", exact_after=history.exact("probe", 0, 1),
             overview_before=before, overview_after=history.overview("probe", 0, 1))
    with HistoricalSignalStore() as history:
        history.append_many(
            ("current", i / 100, 100 if 100 <= i < 110 else
             180 if 500 <= i < 510 else 250, "A")
            for i in range(1000)
        )
        points = history.overview("current", 0, 9.99, max_points=4)
        emit(case="nonextreme_short_dip", source_dip_samples=10, dip_duration_ms=100,
             returned_points=points, preserves_180A=any(v == 180 for _, v in points))
    app.processEvents()


if __name__ == "__main__":
    main()
