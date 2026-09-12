"""Viewport request scheduling correctness (item_123).

Two related defects in the historical viewport cache/generation bookkeeping:

1. A cache hit did not bump the request generation or cancel an in-flight
   worker, so an older worker still resolving a stale viewport could arrive
   later, pass the (unchanged) generation check, and overwrite the cache-hit
   display with data for a viewport the operator already navigated away from
   -- a cache-hit/in-flight "A/B/A" race.
2. The completion handler rebuilt its cache key from whatever the UI showed
   at completion time instead of the viewport the request was actually made
   for, so a result could be filed under the wrong key if the operator kept
   navigating while the query was in flight -- poisoning a later legitimate
   cache hit for the viewport it was really computed for.
"""

from __future__ import annotations

import pytest

from peaklive.analysis import SeriesStore
from peaklive.analysis.history import HistoricalSignalStore
from peaklive.i18n import translate
from peaklive.ui.panels.graph_history import viewport as compute_viewport
from peaklive.ui.panels.graph_stack import RAW_PREVIEW, GraphStackPanel


@pytest.fixture
def panel(qtbot) -> GraphStackPanel:
    widget = GraphStackPanel()
    qtbot.addWidget(widget)
    widget.resize(1000, 400)
    return widget


def _seeded_panel(panel: GraphStackPanel, tmp_path) -> HistoricalSignalStore:
    store = SeriesStore()
    history = HistoricalSignalStore(tmp_path / "history.sqlite3")
    history.append_many([(RAW_PREVIEW, float(t), float(t), None) for t in range(100)])
    panel._history = history
    panel.sync(store, {RAW_PREVIEW})
    return history


def test_a_cache_hit_cancels_a_still_running_worker_for_the_previous_viewport(
    qtbot, tmp_path, panel
):
    history = _seeded_panel(panel, tmp_path)
    # Prime the cache for viewport B by visiting it once and letting it settle.
    panel.anchor_plot.getViewBox().setXRange(50, 99, padding=0)
    panel._window_chosen = True
    panel.refresh_data()
    qtbot.waitUntil(lambda: panel._history_worker is None, timeout=5_000)

    # Navigate to viewport A: a fresh worker starts for it.
    panel.anchor_plot.getViewBox().setXRange(0, 49, padding=0)
    panel.refresh_data()
    worker_a = panel._history_worker
    assert worker_a is not None

    # Navigate back to viewport B before worker A has necessarily finished:
    # this must be served from cache and must obsolete worker A.
    panel.anchor_plot.getViewBox().setXRange(50, 99, padding=0)
    panel.refresh_data()

    assert worker_a._cancel.is_set()
    qtbot.waitUntil(lambda: panel._history_worker is None, timeout=5_000)
    # The display must still reflect viewport B, not a late viewport-A result.
    x, _y = panel.curves[RAW_PREVIEW].getData()
    assert len(x) and min(x) >= 50 and history is not None


def test_a_failed_viewport_read_shows_a_nonmodal_error_and_keeps_last_valid_data(
    qtbot, tmp_path, panel
):
    history = _seeded_panel(panel, tmp_path)
    panel.anchor_plot.getViewBox().setXRange(0, 99, padding=0)
    panel._window_chosen = True
    panel.refresh_data()
    qtbot.waitUntil(lambda: panel._history_worker is None, timeout=5_000)
    curve = panel.curves[RAW_PREVIEW]
    # xData/yData are the arrays actually passed to setData(); getData() can
    # return a view-clipped slice of them once setClipToView is active, which
    # is not what "did the underlying data change" should check.
    x_before = list(curve.xData)
    assert len(x_before) > 0
    assert panel.note.level != "error"

    # The source becomes unavailable: a background reader must fail cleanly
    # rather than raise into the GUI thread or silently show nothing.
    history.path.unlink()
    panel.anchor_plot.getViewBox().setXRange(10, 89, padding=0)
    panel.refresh_data()
    qtbot.waitUntil(lambda: panel._history_worker is None, timeout=5_000)

    assert panel.note.level == "error"
    assert panel.note.text() == translate("graph.history_error")
    # Last valid curve data must survive a failed read, not be blanked.
    assert list(curve.xData) == x_before


def test_a_subsequent_success_clears_a_previous_error_note(qtbot, tmp_path, panel):
    history = _seeded_panel(panel, tmp_path)
    panel.anchor_plot.getViewBox().setXRange(0, 99, padding=0)
    panel._window_chosen = True
    panel.refresh_data()
    qtbot.waitUntil(lambda: panel._history_worker is None, timeout=5_000)

    panel.note.show_message("stale error", "error")

    panel.anchor_plot.getViewBox().setXRange(10, 89, padding=0)
    panel.refresh_data()
    qtbot.waitUntil(lambda: panel._history_worker is None, timeout=5_000)

    assert panel.note.level != "error"
    assert history is not None


def test_a_completed_result_caches_under_the_viewport_it_was_requested_for(qtbot, tmp_path, panel):
    history = _seeded_panel(panel, tmp_path)
    panel.anchor_plot.getViewBox().setXRange(0, 49, padding=0)
    panel._window_chosen = True
    requested_extent, requested_visible = compute_viewport(
        history, panel.global_extent(), True, panel.visible_window()
    )

    panel.refresh_data()
    # Keep navigating before the (possibly still in-flight) worker completes:
    # the result must not be filed under this later viewport instead.
    panel.anchor_plot.getViewBox().setXRange(50, 99, padding=0)
    qtbot.waitUntil(lambda: panel._history_worker is None, timeout=5_000)

    cached_keys = list(panel._history_result_cache.keys())
    assert any(
        extent == requested_extent and visible == requested_visible
        for _path, _curves, extent, visible in cached_keys
    ), cached_keys
