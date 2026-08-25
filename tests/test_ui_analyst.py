"""Acceptance coverage for the analyst workspace slices (req_002).

Everything runs headless with fake adapters, DBC fixtures, and in-memory
sessions. No assertion here depends on connected hardware.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractButton,
    QCheckBox,
    QComboBox,
    QLineEdit,
    QSpinBox,
)

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis import DECODE_DECODED, DECODE_UNKNOWN
from peaklive.domain import BusEvent, CanFrame
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow
from peaklive.ui.dialogs.export import SCOPE_ALL, SCOPE_CURSORS, SCOPE_WINDOW
from peaklive.ui.main_window import SIGNAL_KEY_ROLE

VEHICLE_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 291 VehicleStatus: 8 ECU
 SG_ Speed : 0|16@1+ (0.1,0) [0|250] "km/h" ECU
'''

DOOR_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 292 BodyStatus: 8 ECU
 SG_ DoorState : 0|2@1+ (1,0) [0|3] "" ECU
'''


def _window(qtbot, tmp_path, *, show: bool = False) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    if show:
        window.show()
    return window


def _dbc(tmp_path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _speed_frame(timestamp: float, raw: int) -> CanFrame:
    return CanFrame(timestamp, 291, raw.to_bytes(2, "little") + b"\x00" * 6)


def _signal_item(window: MainWindow, key: str):
    for item in window.signal_explorer.findItems(
        "", Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive, 0
    ):
        if item.data(0, SIGNAL_KEY_ROLE) == key:
            return item
    raise AssertionError(f"Signal item not found: {key}")


# --------------------------------------------------------------------------
# item_016 - selection-driven frame inspector
# --------------------------------------------------------------------------


def test_inspector_describes_the_selected_frame(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    window._render_frames([_speed_frame(1.0, 1234)])

    window.trace_table.setCurrentCell(0, 0)
    text = window.inspector.text()

    assert "FRAME" in text
    assert "0x123" in text
    assert "1.000000 s" in text
    assert "D2 04" in text
    assert "[0] 0xD2 (210)" in text
    assert "VehicleStatus" in text
    assert DECODE_DECODED in text
    assert "Speed = 123.4 km/h" in text


def test_inspector_describes_a_selected_event_row(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._render_acquisition_event(BusEvent(2.0, "error_frame", "PCAN error frame 0x4"))

    window.trace_table.setCurrentCell(0, 0)
    text = window.inspector.text()

    assert "EVENT" in text
    assert "error_frame" in text
    assert "PCAN error frame 0x4" in text


def test_inspector_explains_an_undecodable_frame(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._render_frames([CanFrame(1.0, 0x7FF, b"\xaa")])

    window.trace_table.setCurrentCell(0, 0)
    text = window.inspector.text()

    assert DECODE_UNKNOWN in text
    assert "AA" in text
    assert "no enabled DBC defines this arbitration ID" in text


def test_inspector_ignores_incoming_frames_while_a_row_is_selected(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    window._render_frames([_speed_frame(1.0, 1000)])
    window.trace_table.setCurrentCell(0, 0)
    before = window.inspector.text()

    window._render_frames([_speed_frame(index / 10, 2000) for index in range(20)])

    assert window.inspector.text() == before


def test_inspector_clears_when_the_selected_record_ages_out(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._trace = window._trace.__class__(capacity=3)
    window.trace_panel.set_buffer(window._trace)
    window._render_frames([CanFrame(0.0, 0x100, b"\x01")])
    window.trace_table.setCurrentCell(0, 0)
    assert "0x100" in window.inspector.text()

    window._render_frames([CanFrame(float(i), 0x200 + i, b"\x02") for i in range(1, 6)])
    window.trace_panel.refresh()

    assert "Select a trace row" in window.inspector.text()


# --------------------------------------------------------------------------
# item_017 - stable cursors and graph navigation
# --------------------------------------------------------------------------


def test_cursors_keep_their_position_across_incoming_batches(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    window._render_frames([_speed_frame(0.0, 100)])
    window.graph_panel.place_cursor("a", 0.25)
    window.graph_panel.place_cursor("b", 0.75)

    for index in range(1, 11):
        window._render_frames([_speed_frame(float(index), 100 + index)])

    assert window.graph_panel.cursor_a == 0.25
    assert window.graph_panel.cursor_b == 0.75
    plot = next(iter(window._plot_widgets.values()))
    assert plot._peaklive_cursor_a.value() == pytest.approx(0.25)
    assert plot._peaklive_cursor_b.value() == pytest.approx(0.75)


def test_cursor_positions_persist_across_a_restart_and_a_view_switch(qtbot, tmp_path):
    store = ProfileStore(tmp_path / "settings")
    window = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window._render_frames([CanFrame(0.0, 0x100, b"\x05")])
    window.graph_panel.place_cursor("a", 0.4)
    window.graph_panel.place_cursor("b", 1.6)

    window.workspace_mode_selector.setCurrentIndex(
        window.workspace_mode_selector.findData("trace")
    )
    window.workspace_mode_selector.setCurrentIndex(
        window.workspace_mode_selector.findData("combo")
    )
    assert window.graph_panel.cursor_a == 0.4

    restored = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(restored)
    assert restored.graph_panel.cursor_a == 0.4
    assert restored.graph_panel.cursor_b == 1.6


def test_stacked_plots_share_one_time_axis(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    window._load_dbc_path(_dbc(tmp_path, "door.dbc", DOOR_DBC))
    _signal_item(window, "BodyStatus.DoorState").setCheckState(1, Qt.CheckState.Checked)
    window._render_frames([_speed_frame(float(i), 100 * i) for i in range(5)])

    plots = list(window._plot_widgets.values())
    assert len(plots) == 2
    plots[0].getViewBox().setXRange(1.0, 2.0, padding=0)

    assert plots[1].getViewBox().viewRange()[0] == pytest.approx([1.0, 2.0], abs=1e-6)


def test_graph_navigation_controls_change_the_window_and_report_the_zoom(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._render_frames([CanFrame(float(i), 0x100, bytes([i])) for i in range(20)])
    graph = window.graph_panel
    graph.fit()
    full = graph.visible_window()
    assert full is not None

    graph.zoom(0.5)
    zoomed = graph.visible_window()
    assert zoomed is not None
    assert (zoomed[1] - zoomed[0]) < (full[1] - full[0])
    assert "×" in graph.window_label.text()
    # Zooming leaves follow-live so the operator's window is not yanked back.
    assert not graph.follow_live

    graph.fit()
    refit = graph.visible_window()
    assert refit is not None
    assert (refit[1] - refit[0]) == pytest.approx(full[1] - full[0], rel=1e-6)

    graph.grid_checkbox.setChecked(False)
    assert not graph._grid


def test_follow_live_tracks_new_samples_and_yields_to_navigation(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    graph = window.graph_panel
    window._render_frames([CanFrame(float(i), 0x100, bytes([i % 250])) for i in range(50)])
    assert graph.follow_live

    graph.zoom(0.25)
    assert not graph.follow_live
    held = graph.visible_window()

    window._render_frames([CanFrame(60.0, 0x100, b"\x01")])
    assert graph.visible_window() == pytest.approx(held, abs=1e-6)


# --------------------------------------------------------------------------
# item_018 - range measurement table
# --------------------------------------------------------------------------


def _measure_row(window: MainWindow, signal_name: str) -> list[str]:
    table = window.measure_table
    for row in range(table.rowCount()):
        item = table.item(row, 0)
        if item is not None and item.text() == signal_name:
            return [
                table.item(row, column).text() if table.item(row, column) else ""
                for column in range(table.columnCount())
            ]
    raise AssertionError(f"Measurement row not found: {signal_name}")


def test_measurement_table_reports_cursor_values_and_range_statistics(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    # Speed values 2, 4, 4, 4, 6 km/h at t = 0..4 s.
    for index, raw in enumerate((20, 40, 40, 40, 60)):
        window._render_frames([_speed_frame(float(index), raw)])
    window.graph_panel.place_cursor("a", 0.0)
    window.graph_panel.place_cursor("b", 4.0)

    row = _measure_row(window, "VehicleStatus.Speed")

    assert row[1] == "2"
    assert row[2] == "6"
    assert row[3] == "4"
    assert row[4] == "5"
    assert row[5] == "2"
    assert row[6] == "6"
    assert row[7] == "4"
    assert row[8].startswith("1.2649")
    assert row[9].startswith("4.1952")


def test_measurement_table_states_that_a_range_needs_both_cursors(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._render_frames([CanFrame(0.0, 0x100, b"\x01")])
    window.graph_panel.restore_cursors(None, None)
    window.graph_panel.refresh_measurements()

    assert "Place both cursors" in window.graph_panel.measurement.range_label.text()


def test_measurement_table_reports_an_empty_range_rather_than_zero(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._render_frames([CanFrame(0.0, 0x100, b"\x01")])
    window.graph_panel.place_cursor("a", 50.0)
    window.graph_panel.place_cursor("b", 60.0)

    row = _measure_row(window, "Raw byte 0")

    assert row[4] == "0"
    assert "no sample in range" in row[5]


def test_measurement_table_shows_a_distribution_for_enumerated_signals(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path, "door.dbc", DOOR_DBC))
    series = window._series.ensure("BodyStatus.DoorState")
    for timestamp, value in ((0.0, "Closed"), (1.0, "Open"), (2.0, "Closed")):
        series.append(timestamp, value)
    window.graph_panel.place_cursor("a", 0.0)
    window.graph_panel.place_cursor("b", 2.0)

    row = _measure_row(window, "BodyStatus.DoorState")

    assert row[4] == "3"
    assert "Closedx2" in row[5]
    assert "Openx1" in row[5]


# --------------------------------------------------------------------------
# item_019 - display-only trace filtering with chips
# --------------------------------------------------------------------------


def _seed_mixed_trace(window: MainWindow, tmp_path) -> None:
    window._load_dbc_path(_dbc(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    window._render_frames([_speed_frame(1.0, 500), CanFrame(2.0, 0x456, b"\xff")])
    window._render_acquisition_event(BusEvent(3.0, "error_frame", "ErrorFrame"))


def test_each_trace_filter_narrows_the_display_only(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    _seed_mixed_trace(window, tmp_path)
    panel = window.trace_panel
    assert panel.table.rowCount() == 3

    panel.id_filter.setText("0x123")
    assert panel.table.rowCount() == 1
    assert len(window._trace) == 3
    panel.id_filter.clear()

    panel.message_filter.setText("vehicle")
    assert panel.table.rowCount() == 1
    panel.message_filter.clear()

    panel.signal_filter.setText("speed")
    assert panel.table.rowCount() == 1
    panel.signal_filter.clear()

    panel.status_filter.setCurrentIndex(panel.status_filter.findData(DECODE_UNKNOWN))
    assert panel.table.rowCount() == 1
    panel.status_filter.setCurrentIndex(0)

    panel.event_filter.setText("error")
    assert panel.table.rowCount() == 1
    panel.event_filter.clear()

    panel.time_start_filter.setText("2.5")
    assert panel.table.rowCount() == 1
    panel.time_start_filter.clear()

    panel.show_events.setChecked(False)
    assert panel.table.rowCount() == 2
    panel.show_events.setChecked(True)
    panel.show_frames.setChecked(False)
    assert panel.table.rowCount() == 1


def test_active_filters_appear_as_removable_chips(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)
    _seed_mixed_trace(window, tmp_path)
    panel = window.trace_panel

    panel.id_filter.setText("0x123")
    panel.show_events.setChecked(False)
    chips = panel.chips.findChildren(QAbstractButton)
    assert len(chips) == 2
    assert panel.chips.isVisible()

    id_chip = next(chip for chip in chips if chip.property("filterField") == "arbitration_id")
    id_chip.click()
    assert panel.id_filter.text() == ""
    assert len(panel.chips.findChildren(QAbstractButton)) == 1

    panel.clear_filters_button.click()
    assert panel.chips.findChildren(QAbstractButton) == []
    assert panel.table.rowCount() == 3


def test_a_filter_matching_nothing_is_distinct_from_an_empty_trace(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    panel = window.trace_panel
    assert "No frame received yet" in panel.note.text()

    _seed_mixed_trace(window, tmp_path)
    panel.id_filter.setText("0x7FF")

    assert panel.table.rowCount() == 0
    assert "No row matches the active filters" in panel.note.text()
    assert panel.note.level == "warning"


def test_trace_filters_persist_across_a_restart(qtbot, tmp_path):
    store = ProfileStore(tmp_path / "settings")
    window = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window.trace_panel.id_filter.setText("0x2A")
    window.trace_panel.show_events.setChecked(False)

    restored = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(restored)

    assert restored.trace_panel.id_filter.text() == "0x2A"
    assert not restored.trace_panel.show_events.isChecked()
    assert restored.trace_panel.settings.arbitration_id == "0x2A"


def test_secondary_filters_are_progressively_disclosed(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)
    panel = window.trace_panel
    assert not panel.secondary.isVisible()

    panel.more_filters_button.click()
    assert panel.secondary.isVisible()
    assert panel.more_filters_button.text() == "Fewer filters"

    panel.more_filters_button.click()
    assert not panel.secondary.isVisible()


# --------------------------------------------------------------------------
# item_020 - configurable, bounded trace columns
# --------------------------------------------------------------------------


def test_column_visibility_order_width_and_format_take_effect(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._render_frames([CanFrame(1.0, 0x123, b"\x01\x02")])
    dialog = window._open_columns_dialog()
    qtbot.addWidget(dialog)

    dialog.findChild(QCheckBox, "columnVisible_channel").setChecked(False)
    assert window.trace_table.columnCount() == 7

    dialog.findChild(QSpinBox, "columnWidth_id").setValue(140)
    assert window.trace_table.columnWidth(1) == 140

    data_format = dialog.findChild(QComboBox, "columnFormat_data")
    data_format.setCurrentIndex(data_format.findData("bin"))
    assert window.trace_table.item(0, 3).text() == "00000001 00000010"

    data_format.setCurrentIndex(data_format.findData("dec"))
    assert window.trace_table.item(0, 3).text() == "1 2"

    keys_before = [column.key for column in window.selected_profile.trace_columns]
    dialog.findChild(QAbstractButton, "columnDown_time").click()
    keys_after = [column.key for column in window.selected_profile.trace_columns]
    assert keys_after[0] == keys_before[1]
    assert keys_after[1] == keys_before[0]


def test_column_configuration_persists_across_a_restart(qtbot, tmp_path):
    store = ProfileStore(tmp_path / "settings")
    window = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    column = next(c for c in window.selected_profile.trace_columns if c.key == "dlc")
    column.visible = False
    column.width = 44
    window._columns_changed()

    restored = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(restored)
    restored_column = next(
        c for c in restored.selected_profile.trace_columns if c.key == "dlc"
    )

    assert not restored_column.visible
    assert restored_column.width == 44
    assert restored.trace_table.columnCount() == 7


def test_sustained_ingestion_stays_bounded_without_per_row_removal(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._trace = window._trace.__class__(capacity=200)
    window.trace_panel.set_buffer(window._trace)

    removals = 0
    original = window.trace_table.removeRow

    def counted(row):
        nonlocal removals
        removals += 1
        original(row)

    window.trace_table.removeRow = counted  # type: ignore[method-assign]
    for batch in range(20):
        window._render_frames(
            [CanFrame(float(batch * 64 + i), 0x100, b"\x01") for i in range(64)]
        )

    assert len(window._trace) == 200
    assert window.trace_table.rowCount() == 200
    # The old workspace called removeRow once per aged-out row; this one never does.
    assert removals == 0


def test_the_operator_can_leave_the_live_tail_and_come_back(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)
    panel = window.trace_panel
    window._render_frames([CanFrame(float(i), 0x100, b"\x01") for i in range(300)])
    assert panel.follow_tail

    panel.table.verticalScrollBar().setValue(0)
    assert not panel.follow_tail
    assert panel.tail_note.isVisible()

    panel.follow_checkbox.setChecked(True)
    assert panel.follow_tail
    assert not panel.tail_note.isVisible()


# --------------------------------------------------------------------------
# item_021 - streamed export
# --------------------------------------------------------------------------


def _export_window(qtbot, tmp_path) -> MainWindow:
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    for index in range(10):
        window._render_frames([_speed_frame(float(index), 100 + index * 10)])
    return window


def test_export_dialog_defaults_to_the_shown_signals(qtbot, tmp_path):
    window = _export_window(qtbot, tmp_path)
    dialog = window._open_export_dialog()
    qtbot.addWidget(dialog)

    assert dialog.selected_signals == ["VehicleStatus.Speed"]


def test_export_writes_exactly_the_rows_in_each_scope(qtbot, tmp_path):
    window = _export_window(qtbot, tmp_path)
    window.graph_panel.place_cursor("a", 2.0)
    window.graph_panel.place_cursor("b", 5.0)
    window.graph_panel.set_follow_live(False)
    next(iter(window._plot_widgets.values())).getViewBox().setXRange(0.0, 3.0, padding=0)

    dialog = window._open_export_dialog()
    qtbot.addWidget(dialog)

    dialog.scope_selector.setCurrentIndex(dialog.scope_selector.findData(SCOPE_CURSORS))
    dialog.set_destination(tmp_path / "cursors.csv")
    assert dialog.run_export(blocking=True) == 4

    dialog.scope_selector.setCurrentIndex(dialog.scope_selector.findData(SCOPE_WINDOW))
    dialog.set_destination(tmp_path / "window.csv")
    assert dialog.run_export(blocking=True) == 4

    dialog.scope_selector.setCurrentIndex(dialog.scope_selector.findData(SCOPE_ALL))
    dialog.set_destination(tmp_path / "all.csv")
    assert dialog.run_export(blocking=True) == 10

    header, *rows = (tmp_path / "all.csv").read_text(encoding="utf-8").strip().splitlines()
    assert header == "timestamp,message,signal,value,unit"
    assert rows[0].startswith("0.0,VehicleStatus,Speed,10.0,km/h")


def test_export_produces_matching_csv_and_parquet_row_counts(qtbot, tmp_path):
    import pyarrow.parquet as pq

    window = _export_window(qtbot, tmp_path)
    dialog = window._open_export_dialog()
    qtbot.addWidget(dialog)
    dialog.scope_selector.setCurrentIndex(dialog.scope_selector.findData(SCOPE_ALL))

    dialog.set_destination(tmp_path / "out.csv")
    csv_rows = dialog.run_export(blocking=True)
    dialog.format_selector.setCurrentIndex(dialog.format_selector.findData("parquet"))
    dialog.set_destination(tmp_path / "out.parquet")
    parquet_rows = dialog.run_export(blocking=True)

    assert csv_rows == parquet_rows == 10
    assert pq.read_table(tmp_path / "out.parquet").num_rows == 10


def test_a_cancelled_export_leaves_no_file_and_says_so(qtbot, tmp_path):
    window = _export_window(qtbot, tmp_path)
    dialog = window._open_export_dialog()
    qtbot.addWidget(dialog)
    dialog.scope_selector.setCurrentIndex(dialog.scope_selector.findData(SCOPE_ALL))
    destination = tmp_path / "cancelled.csv"
    dialog.set_destination(destination)

    # Cancel before the stream starts: the flag is checked on the first row.
    from peaklive.analysis import export_rows
    from peaklive.services.export_worker import ExportWorker

    worker = ExportWorker(
        destination, export_rows(window._series, ["VehicleStatus.Speed"]), "csv"
    )
    worker.request_stop()
    assert worker.execute() == -1
    assert not destination.exists()

    dialog._cancelled()
    assert "cancelled" in dialog.note.text()
    assert dialog.note.level == "warning"


def test_export_reports_validation_and_write_failures_inline(qtbot, tmp_path):
    window = _export_window(qtbot, tmp_path)
    dialog = window._open_export_dialog()
    qtbot.addWidget(dialog)

    dialog.signal_list.clearSelection()
    assert dialog.run_export(blocking=True) == -1
    assert "at least one signal" in dialog.note.text()

    dialog.signal_list.selectAll()
    assert dialog.run_export(blocking=True) == -1
    assert "Choose a destination" in dialog.note.text()

    dialog.set_destination(tmp_path / "missing-directory" / "out.csv")
    dialog.scope_selector.setCurrentIndex(dialog.scope_selector.findData(SCOPE_ALL))
    assert dialog.run_export(blocking=True) == -1
    assert "Export failed" in dialog.note.text()
    assert dialog.note.level == "error"


def test_export_refuses_a_cursor_scope_without_both_cursors(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    dialog = window._open_export_dialog()
    qtbot.addWidget(dialog)
    dialog.scope_selector.setCurrentIndex(dialog.scope_selector.findData(SCOPE_CURSORS))
    dialog.set_destination(tmp_path / "nope.csv")

    assert dialog.run_export(blocking=True) == -1
    assert "Place both cursors" in dialog.note.text()


# --------------------------------------------------------------------------
# item_022 - session diagnostic report
# --------------------------------------------------------------------------


def test_report_summarizes_volumes_dbcs_coverage_and_anomalies(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    window._render_frames([_speed_frame(1.0, 100), _speed_frame(2.0, 200)])
    window._render_frames([CanFrame(3.0, 0x456, b"\xff")])
    window._render_acquisition_event(BusEvent(4.0, "error_frame", "ErrorFrame"))
    window._refresh_report()

    text = window.report_view.toPlainText()

    assert "Frames: 3" in text
    assert "Events: 1" in text
    assert "1.000000s to 4.000000s" in text
    assert "Decode coverage: 66.7%" in text
    assert "vehicle.dbc" in text
    assert "0x123  2" in text
    assert "Bus error frames: 1" in text
    assert "Unknown arbitration IDs: 1" in text


def test_report_is_reachable_from_the_view_selector_and_exports(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)
    window._render_frames([CanFrame(1.0, 0x100, b"\x01")])

    window.workspace_mode_selector.setCurrentIndex(
        window.workspace_mode_selector.findData("report")
    )
    assert window.report_panel.isVisible()
    assert not window.trace_panel.isVisible()

    window.report_panel.refresh_button.click()
    destination = tmp_path / "report.txt"
    destination.write_text(window.report_panel.text, encoding="utf-8")

    assert destination.read_text(encoding="utf-8") == window.report_panel.text


def test_report_states_an_empty_session(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._refresh_report()

    assert "no sample captured" in window.report_view.toPlainText()
    assert not window.report_panel.export_button.isEnabled()


# --------------------------------------------------------------------------
# item_023 - bus state, error, and loading feedback
# --------------------------------------------------------------------------


def test_bus_state_follows_the_acquisition_lifecycle(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    assert window.bus_state == "idle"

    window._start_acquisition()
    assert window.bus_state == "connecting"
    qtbot.waitUntil(lambda: window.trace_table.rowCount() > 0)
    assert window.bus_state == "running"

    window._stop_acquisition()
    qtbot.waitUntil(lambda: window.start_button.isEnabled())
    assert window.bus_state == "stopped"


def test_bus_state_reflects_error_and_bus_off_events(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    window._render_acquisition_event(BusEvent(1.0, "error_frame", "ErrorFrame"))
    assert window.bus_state == "bus_error"

    window._render_acquisition_event(BusEvent(2.0, "bus_off", "Bus off"))
    assert window.bus_state == "bus_off"

    window._render_acquisition_event(BusEvent(3.0, "reconnecting", "Reconnecting"))
    assert window.bus_state == "reconnecting"

    window._acquisition_failed("adapter refused the bitrate")
    assert window.bus_state == "bus_error"


def test_a_dbc_load_failure_stays_visible_in_the_library_panel(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)
    broken = tmp_path / "broken.dbc"
    broken.write_text("this is not a DBC file", encoding="utf-8")

    window._load_dbc_path(broken)
    assert "Cannot load broken.dbc" in window.dbc_panel.note.text()
    assert window.dbc_panel.note.level == "error"

    # Further traffic must not clear the diagnosis.
    window._render_frames([CanFrame(1.0, 0x100, b"\x01")])
    assert "Cannot load broken.dbc" in window.dbc_panel.note.text()


def test_a_recording_warning_stays_visible_in_the_shell(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)

    window._render_acquisition_event(
        BusEvent(1.0, "recording_warning", "Recording disk space is low: 1.0 GiB free")
    )

    assert "disk space is low" in window.session_note.text()
    assert window.session_note.level == "warning"
    window._render_frames([CanFrame(2.0, 0x100, b"\x01")])
    assert "disk space is low" in window.session_note.text()


def test_replay_shows_progress_and_clears_it_when_done(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)
    trace = tmp_path / "capture.asc"
    trace.write_text(
        "date Mon Jan 01 00:00:00 2026\n"
        "base hex  timestamps absolute\n"
        "   0.100000 1  123             Rx   d 2 D2 04\n"
        "   0.200000 1  ErrorFrame\n",
        encoding="utf-8",
    )

    window._open_trace(trace)
    assert window.progress.isVisible()
    qtbot.waitUntil(lambda: not window.progress.isVisible(), timeout=5000)

    assert window.trace_table.rowCount() >= 1
    assert "capture.asc" in window.report_view.toPlainText()


def test_the_graph_states_that_it_has_no_data(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)

    assert window.graph_panel.note.isVisible()
    assert "No plot yet" in window.graph_panel.note.text()

    window._render_frames([CanFrame(1.0, 0x100, b"\x07")])
    assert not window.graph_panel.note.isVisible()


# --------------------------------------------------------------------------
# item_024 - keyboard, menus, layout persistence
# --------------------------------------------------------------------------


def test_the_menu_bar_exposes_the_workspace_actions(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    names = {
        action.objectName(): action.shortcut().toString()
        for menu in window.menuBar().actions()
        if menu.menu() is not None
        for action in menu.menu().actions()
    }

    assert names["menu_load_dbc"] == "Ctrl+D"
    assert names["menu_open_trace"] == "Ctrl+O"
    assert names["menu_export"] == "Ctrl+E"
    assert names["menu_start"] == "F5"
    assert names["menu_stop"] == "F6"
    assert names["menu_fullscreen"] == "F11"
    assert names["menu_fit"] == "Ctrl+0"
    assert names["menu_focus_filter"] == "Ctrl+F"
    assert "menu_about" in names


def test_cursor_and_panel_shortcuts_are_bound(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._render_frames([CanFrame(float(i), 0x100, b"\x01") for i in range(10)])

    assert window.cursor_a_action.shortcut().toString() == "Ctrl+1"
    assert window.cursor_b_action.shortcut().toString() == "Ctrl+2"
    assert window.collapse_action.shortcut().toString() == "Ctrl+B"

    window.graph_panel.restore_cursors(None, None)
    window.cursor_a_action.trigger()
    window.cursor_b_action.trigger()
    assert window.graph_panel.cursor_a is not None
    assert window.graph_panel.cursor_b is not None

    assert not window.signals_panel.is_collapsed
    window.collapse_action.trigger()
    assert window.signals_panel.is_collapsed


def test_every_actionable_control_carries_a_tooltip_and_an_accessible_name(qtbot, tmp_path):  # noqa: E501
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path, "vehicle.dbc", VEHICLE_DBC))

    widgets = [
        widget
        for kind in (QAbstractButton, QComboBox, QLineEdit)
        for widget in window.findChildren(kind)
    ]
    actionable = [
        widget
        for widget in widgets
        if widget.isEnabled()
        and widget.objectName()
        # Qt's own internal helpers (corner buttons, scroll-area handles).
        and not widget.objectName().startswith("qt_")
    ]
    assert len(actionable) > 15

    assert [w.objectName() for w in actionable if not w.toolTip()] == []
    assert [w.objectName() for w in actionable if not w.accessibleName()] == []


def test_the_trace_filter_shortcut_moves_focus_into_the_filter(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)
    qtbot.waitExposed(window)

    window._focus_trace_filter()

    assert window.focusWidget() is window.trace_panel.id_filter


def test_layout_geometry_and_collapse_state_persist_across_a_restart(qtbot, tmp_path):
    store = ProfileStore(tmp_path / "settings")
    window = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window.show()
    window.workspace.setSizes([200, 800, 320])
    window.center_divider.setSizes([300, 400, 0])
    window.inspector_panel.set_collapsed(True)
    window._persist_layout()

    # Qt rescales requested sizes to the real widget width, so what is stored
    # is the resulting geometry, and that is what has to come back.
    stored = store.load().selected.layout
    assert len(stored.splitter_sizes) == 3
    assert stored.splitter_sizes[0] < stored.splitter_sizes[1]
    assert stored.divider_sizes[2] == 0
    assert stored.collapsed_panels == ["inspector"]

    restored = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(restored)
    restored.show()

    assert restored.workspace.sizes() == stored.splitter_sizes
    assert restored.center_divider.sizes()[2] == 0
    assert restored.inspector_panel.is_collapsed
    assert not restored.signals_panel.is_collapsed


def test_fullscreen_can_be_entered_and_left(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)
    assert not window.isFullScreen()

    window._toggle_fullscreen()
    assert window.isFullScreen()
    assert window.selected_profile.layout.fullscreen

    window._toggle_fullscreen()
    assert not window.isFullScreen()
    assert not window.selected_profile.layout.fullscreen


@pytest.mark.parametrize("size", [(1024, 768), (1280, 720), (1600, 900)])
def test_the_layout_stays_usable_at_the_bench_viewports(qtbot, tmp_path, size):
    window = _window(qtbot, tmp_path, show=True)
    window._load_dbc_path(_dbc(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    window.resize(*size)
    qtbot.waitExposed(window)

    assert window.minimumWidth() <= size[0]
    assert window.minimumHeight() <= size[1]
    for widget in (
        window.acquisition_bar,
        window.signals_panel,
        window.trace_graph_panel,
        window.inspector_panel,
        window.trace_table,
        window.measure_table,
    ):
        assert widget.isVisible()
        assert widget.width() > 0
        assert widget.x() >= 0
        assert widget.x() + widget.width() <= window.width() + 1
