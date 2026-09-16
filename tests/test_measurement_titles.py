"""item_140 - the A/B measurement table names signals the way an operator does.

The Signal column used to render `signal_label`, so every row carried a DBC
hash and arbitration ID the operator never asked for, while the graph lanes
beside it already showed the clean `Message.Signal` title. The provenance is
still what tells two identically-titled sources apart, so it moves to the
cell's tooltip rather than disappearing.
"""

from __future__ import annotations

from peaklive.analysis import SeriesStore
from peaklive.analysis.dbc import signal_key
from peaklive.analysis.statistics import range_statistics
from peaklive.ui.panels.measurement import MeasurementPanel

FIRST = signal_key("a1b2c3d4e5f6", 0x123, False, "PowerStatus", "Voltage")
SECOND = signal_key("99887766aabb", 0x456, False, "PowerStatus", "Voltage")


def _store() -> SeriesStore:
    store = SeriesStore()
    for index, name in enumerate((FIRST, SECOND)):
        for step in range(5):
            store.append(name, float(step), float(step + index * 100), "V")
    return store


def _panel(qtbot) -> MeasurementPanel:
    panel = MeasurementPanel()
    qtbot.addWidget(panel)
    return panel


def _cell(panel: MeasurementPanel, row: int, column: int) -> str:
    item = panel.table.item(row, column)
    return "" if item is None else item.text()


def test_a_qualified_signal_shows_its_message_and_signal_only(qtbot):
    panel = _panel(qtbot)

    panel.refresh(_store(), (FIRST,), 0.0, 4.0)

    assert _cell(panel, 0, 0) == "PowerStatus.Voltage"


def test_the_technical_provenance_stays_reachable_from_the_cell(qtbot):
    panel = _panel(qtbot)

    panel.refresh(_store(), (FIRST,), 0.0, 4.0)

    tooltip = panel.table.item(0, 0).toolTip()
    assert "a1b2c3d4" in tooltip
    assert "0x123" in tooltip


def test_two_sources_sharing_a_title_keep_distinct_rows_values_and_identity(qtbot):
    panel = _panel(qtbot)
    store = _store()

    panel.refresh(store, (FIRST, SECOND), 0.0, 4.0)

    titles = [_cell(panel, row, 0) for row in range(2)]
    tooltips = [panel.table.item(row, 0).toolTip() for row in range(2)]
    assert titles == ["PowerStatus.Voltage", "PowerStatus.Voltage"]
    assert tooltips[0] != tooltips[1]
    assert _cell(panel, 0, 1) != _cell(panel, 1, 1)


def test_a_plain_legacy_name_is_shown_unchanged(qtbot):
    panel = _panel(qtbot)
    store = SeriesStore()
    store.append("Raw byte 0", 0.0, 7.0)

    panel.refresh(store, ("Raw byte 0",), None, None)

    assert _cell(panel, 0, 0) == "Raw byte 0"


def test_the_clean_title_changes_no_measured_value(qtbot):
    panel = _panel(qtbot)
    store = _store()

    panel.refresh(store, (SECOND,), 0.0, 4.0)
    expected = range_statistics(store.series(SECOND), 0.0, 4.0)

    assert _cell(panel, 0, 1) == "100"
    assert _cell(panel, 0, 2) == "104"
    assert _cell(panel, 0, 3) == "4"
    assert _cell(panel, 0, 4) == str(expected.count)


def test_a_signal_without_samples_still_reads_as_its_clean_title(qtbot):
    panel = _panel(qtbot)

    panel.refresh(SeriesStore(), (FIRST,), 0.0, 4.0)

    assert _cell(panel, 0, 0) == "PowerStatus.Voltage"
    assert _cell(panel, 0, 1)
