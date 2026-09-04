"""item_069 coverage: bounded plot rendering and coalesced measurement recompute.

Every retained series can hold up to 20,000 points and a live signal can
carry the graph-refresh timer at 20Hz; neither should cost proportionally
more than the viewport can show or the operator can read. Displayed points
are bounded by pyqtgraph's own clip/downsample policy, and A/B statistics
recompute at most once per documented cadence, never once per tick.
"""

from __future__ import annotations

import pytest

from peaklive.analysis import SeriesStore
from peaklive.ui.panels.graph_stack import RAW_PREVIEW, GraphStackPanel


@pytest.fixture
def panel(qtbot) -> GraphStackPanel:
    widget = GraphStackPanel()
    qtbot.addWidget(widget)
    return widget


def _filled(panel: GraphStackPanel, samples: list[tuple[float, float]]) -> SeriesStore:
    store = SeriesStore()
    for timestamp, value in samples:
        store.append(RAW_PREVIEW, timestamp, value)
    panel.sync(store, {RAW_PREVIEW})
    return store


# ---- AC1: displayed points are bounded by viewport policy ------------------


def test_every_curve_enables_clip_to_view_and_peak_downsampling(panel):
    panel.begin_session(live=False)
    _filled(panel, [(index * 0.001, index) for index in range(1_000)])

    curves = list(panel._curves.values())
    assert curves
    for curve in curves:
        assert curve.opts["clipToView"] is True
        assert curve.opts["autoDownsample"] is True
        assert curve.opts["downsampleMethod"] == "peak"


def test_eight_signals_each_get_the_same_viewport_policy(qtbot, tmp_path):
    panel = GraphStackPanel()
    qtbot.addWidget(panel)
    panel.begin_session(live=False)
    store = SeriesStore()
    names = {f"Bus.Signal{index}" for index in range(8)}
    for name in names:
        for t in range(100):
            store.append(name, float(t), float(t))
    panel.sync(store, names)

    assert len(panel._curves) == 8
    for curve in panel._curves.values():
        assert curve.opts["clipToView"] is True
        assert curve.opts["autoDownsample"] is True


# ---- AC2: measurement calculations run no more than their documented ------
# ---- cadence and preserve final values -------------------------------------


def test_a_burst_of_refresh_data_calls_recomputes_measurements_once(panel):
    panel.begin_session(live=True)
    store = _filled(panel, [(index * 0.1, index) for index in range(20)])
    panel.cursor_a = 0.0
    panel.cursor_b = 1.0
    refreshes: list = []
    original = panel.refresh_measurements
    panel.refresh_measurements = lambda: (refreshes.append(True), original())[1]  # type: ignore[method-assign]

    for tick in range(30):
        store.append(RAW_PREVIEW, 2.0 + tick * 0.05, tick)
        panel.refresh_data()

    assert refreshes == []
    panel._flush_measurements()
    assert refreshes == [True]


def test_the_measurement_timer_stops_itself_once_nothing_is_dirty(panel):
    panel.begin_session(live=True)
    _filled(panel, [(index * 0.1, index) for index in range(10)])
    panel.cursor_a = 0.0
    panel.cursor_b = 1.0
    panel.refresh_data()
    assert panel._measurement_refresh_timer.isActive()

    panel._flush_measurements()
    # A second tick with nothing new to show must not keep polling forever.
    panel._flush_measurements()

    assert not panel._measurement_refresh_timer.isActive()


def _table_text(panel: GraphStackPanel) -> list[list[str]]:
    table = panel.measurement.table
    return [
        [
            table.item(row, column).text() if table.item(row, column) else ""
            for column in range(table.columnCount())
        ]
        for row in range(table.rowCount())
    ]


def test_coalesced_recompute_still_reports_the_correct_final_values(panel):
    panel.begin_session(live=True)
    _filled(panel, [(0.0, 2.0), (1.0, 4.0), (2.0, 4.0), (3.0, 4.0), (4.0, 6.0)])
    panel.cursor_a = 0.0
    panel.cursor_b = 4.0

    # Many redundant requests, coalesced to one recompute...
    for _ in range(5):
        panel.refresh_data()
    panel._flush_measurements()
    coalesced = _table_text(panel)

    # ...must report exactly what an uncoalesced, direct call would.
    panel.refresh_measurements()
    direct = _table_text(panel)

    assert coalesced == direct
    assert coalesced != []


def test_eight_signals_with_separated_cursors_measure_after_one_coalesced_flush(qtbot):
    panel = GraphStackPanel()
    qtbot.addWidget(panel)
    panel.begin_session(live=True)
    store = SeriesStore()
    names = [f"Bus.Signal{index}" for index in range(8)]
    for name_index, name in enumerate(names):
        for t in range(20):
            store.append(name, float(t), float(t + name_index))
    panel.sync(store, set(names))
    panel.cursor_a = 2.0
    panel.cursor_b = 15.0
    assert panel.cursor_a != panel.cursor_b

    refreshes: list = []
    original = panel.refresh_measurements
    panel.refresh_measurements = lambda: (refreshes.append(True), original())[1]  # type: ignore[method-assign]
    for _ in range(10):
        panel.refresh_data()

    assert refreshes == []
    panel._flush_measurements()
    assert refreshes == [True]
    assert panel.measurement.table.rowCount() == 8
