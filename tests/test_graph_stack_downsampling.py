"""A sparse historical envelope must survive rendering (item_122).

``HistoricalSignalStore.overview`` already reduces samples to a pixel-aware
budget. pyqtgraph's own automatic peak reducer, left enabled on every curve,
could re-reduce that already-sparse result and erase it entirely: a factor
larger than the surviving point count yields zero display groups. See
logics/analysis/dense_overview_diagnosis.md, "sparse_summary_wide_view".
"""

from __future__ import annotations

import pytest

from peaklive.analysis import SeriesStore
from peaklive.analysis.history import HistoricalSignalStore
from peaklive.ui.panels.graph_stack import RAW_PREVIEW, GraphStackPanel


@pytest.fixture
def panel(qtbot) -> GraphStackPanel:
    widget = GraphStackPanel()
    qtbot.addWidget(widget)
    widget.resize(1000, 400)
    return widget


def test_a_sparse_historical_envelope_is_not_erased_by_secondary_reduction(qtbot, tmp_path, panel):
    store = SeriesStore()
    history = HistoricalSignalStore(tmp_path / "history.sqlite3")
    history.append_many(
        [
            (RAW_PREVIEW, 944.97, 0, None),
            (RAW_PREVIEW, 944.98, 10, None),
            (RAW_PREVIEW, 944.99, -10, None),
        ]
    )
    panel._history = history
    panel.sync(store, {RAW_PREVIEW})
    # Reproduce the diagnosed 0..945 s wide view over three points clustered
    # at the very end: a real operator viewport, not a range that happens to
    # match the data span exactly.
    panel.anchor_plot.getViewBox().setXRange(0, 945, padding=0)
    panel._window_chosen = True

    panel.refresh_data()
    qtbot.waitUntil(lambda: panel._history_worker is None, timeout=5_000)

    curve = panel.curves[RAW_PREVIEW]
    x, _y = curve.getData()
    assert len(x) == 3


def test_live_samples_keep_automatic_downsampling_enabled(panel):
    store = SeriesStore()
    store.append(RAW_PREVIEW, 0.0, 1.0)
    panel.sync(store, {RAW_PREVIEW})

    curve = panel.curves[RAW_PREVIEW]
    assert curve.opts["autoDownsample"] is True
