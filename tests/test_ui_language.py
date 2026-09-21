"""Choosing French or English at runtime, without disturbing the session.

These cases are the behavioural proof for the bilingual workflow: the menu
itself, two-way retranslation of built and deferred surfaces, and — the part
that matters most on a bench — that changing language touches no worker, no
captured frame and no piece of operator state.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QMenu

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis import ReportRenderer, SessionFacts
from peaklive.domain import CanFrame
from peaklive.i18n import LOCALE_AUTONYMS, current_locale, translate, translate_in
from peaklive.services.profiles import ProfileStore
from peaklive.services.ui_settings import UiSettingsStore
from peaklive.ui import MainWindow
from peaklive.ui.dialogs import ExportDialog, RecordingSettingsDialog

VEHICLE_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 291 VehicleStatus: 8 ECU
 SG_ Speed : 0|16@1+ (0.1,0) [0|250] "km/h" ECU
'''

SUPPORTED_VIEWPORTS = (QSize(1024, 768), QSize(1280, 720), QSize(1600, 900))


def _window(qtbot, tmp_path, *, show: bool = False) -> MainWindow:
    window = MainWindow(
        ProfileStore(tmp_path / "settings"),
        adapter_factory=FakeCanAdapter,
        ui_settings=UiSettingsStore(tmp_path / "settings"),
    )
    qtbot.addWidget(window)
    if show:
        window.show()
    return window


def _dbc(tmp_path: Path) -> Path:
    path = tmp_path / "vehicle.dbc"
    path.write_text(VEHICLE_DBC, encoding="utf-8")
    return path


def _speed_frame(timestamp: float, raw: int) -> CanFrame:
    return CanFrame(timestamp, 291, raw.to_bytes(2, "little") + b"\x00" * 6)


def _menu_titles(window: MainWindow) -> list[str]:
    return [action.text() for action in window.menuBar().actions()]


def _setup_menu(window: MainWindow) -> QMenu:
    titles = {translate_in("en", "menu.setup"), translate_in("fr", "menu.setup")}
    return next(
        action.menu()
        for action in window.menuBar().actions()
        if action.menu() is not None and action.text() in titles
    )


def _language_submenu(window: MainWindow) -> QMenu:
    return next(
        action.menu()
        for action in _setup_menu(window).actions()
        if action.menu() is not None and action.menu().objectName() == "menu_language"
    )


# ---- the language menu ----------------------------------------------------


def test_the_language_menu_offers_exactly_the_two_autonyms(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    submenu = _language_submenu(window)
    entries = submenu.actions()

    assert [action.text() for action in entries] == [
        LOCALE_AUTONYMS["en"],
        LOCALE_AUTONYMS["fr"],
    ]
    # The stored code, not the caption, is the entry's identity.
    assert [action.data() for action in entries] == ["en", "fr"]
    assert all(action.isCheckable() for action in entries)


def test_the_menu_marks_the_current_language_and_keeps_the_choices_exclusive(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    entries = {action.data(): action for action in _language_submenu(window).actions()}

    assert entries["en"].isChecked()
    assert not entries["fr"].isChecked()

    entries["fr"].trigger()

    assert entries["fr"].isChecked()
    assert not entries["en"].isChecked()
    assert current_locale() == "fr"


def test_the_persisted_language_is_live_before_the_first_window_is_built(qtbot, tmp_path):
    UiSettingsStore(tmp_path / "settings").save_locale("fr")

    window = _window(qtbot, tmp_path)

    assert current_locale() == "fr"
    assert window.windowTitle() == translate("app.title")
    assert "&Fichier" in _menu_titles(window)
    assert {action.data() for action in _language_submenu(window).actions()} == {"en", "fr"}
    assert next(
        action for action in _language_submenu(window).actions() if action.data() == "fr"
    ).isChecked()


def test_choosing_a_language_records_it_for_the_next_launch(qtbot, tmp_path):
    settings = UiSettingsStore(tmp_path / "settings")
    window = _window(qtbot, tmp_path)

    window._select_locale("fr")

    assert settings.load().locale == "fr"


def test_a_language_that_cannot_be_saved_still_applies_and_says_so(qtbot, tmp_path, monkeypatch):
    window = _window(qtbot, tmp_path)
    monkeypatch.setattr(
        window._ui_settings,
        "save_locale",
        lambda locale: (_ for _ in ()).throw(OSError("read-only volume")),
    )
    monkeypatch.setattr("peaklive.ui.locale_controller.QMessageBox.warning", lambda *a, **k: None)

    window._select_locale("fr")

    assert current_locale() == "fr"
    assert "&Fichier" in _menu_titles(window)
    assert window.session_note.isVisibleTo(window)
    assert "read-only volume" in window.session_note.text()
    assert window.session_note.level == "warning"


# ---- two-way retranslation ------------------------------------------------


def test_switching_language_retranslates_the_menus_and_returns_cleanly(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    english = _menu_titles(window)

    window._select_locale("fr")
    french = _menu_titles(window)
    window._select_locale("en")

    assert french == [
        "&Fichier",
        "&Enregistrement",
        "&Configuration",
        "&Affichage",
        "&DBC",
        "A&ide",
    ]
    assert english != french
    assert _menu_titles(window) == english


def test_switching_language_retranslates_panels_headers_and_descriptions(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    window._select_locale("fr")

    assert window.signals_panel.heading.text() == "SIGNAUX"
    assert window.inspector_panel.heading.text() == "INSPECTEUR"
    assert [
        window.explorer_panel.tree.headerItem().text(column) for column in range(3)
    ] == ["Signal", "Aff.", "Fav."]
    assert window.explorer_panel.search.placeholderText() == translate(
        "signals.search_placeholder"
    )
    assert window.acquisition_bar.start_button.toolTip() == translate(
        "acquisition.start_tooltip"
    )
    assert window.trace_panel.note.text() == translate("trace.empty")
    assert window.inspector.text() == translate("inspector.empty")


def test_switching_language_retranslates_an_action_shortcut_tooltip(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    window._select_locale("fr")
    action = next(
        item for item in window.findChildren(type(window.start_action))
        if item.objectName() == "menu_start"
    )

    assert action.text() == "&Démarrer l'acquisition"
    assert action.toolTip() == "&Démarrer l'acquisition (F5)"
    assert action.shortcut().toString() == "F5"


def test_a_panel_hidden_at_switch_time_reads_in_the_new_language_when_reopened(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window.signals_panel.set_hidden(True)

    window._select_locale("fr")
    window.signals_panel.set_hidden(False)

    assert window.signals_panel.heading.text() == "SIGNAUX"
    assert window.signals_panel.rail.text() == "SIGNAUX"


def test_a_collapsed_panel_describes_its_expand_control_in_the_new_language(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window.signals_panel.set_collapsed(True)

    window._select_locale("fr")

    expected = translate("panel.expand").format(panel="Signaux")
    assert window.signals_panel.toggle.accessibleName() == expected
    assert window.signals_panel.toggle.toolTip() == expected
    assert window.signals_panel.is_collapsed


def test_a_dialog_opened_after_the_switch_uses_the_new_language(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    window._select_locale("fr")
    dialog = window._open_recording_dialog()
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == translate("recording.title")
    assert dialog.close_button.text() == translate("recording.close")
    dialog.reject()


def test_an_open_dialog_retranslates_without_losing_the_operator_edits(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    dialog = window._open_recording_dialog()
    qtbot.addWidget(dialog)
    dialog.text_edit.setText("bench-run-4")
    dialog.template_edit.setText("{profile}-{iteration:03d}")

    window._select_locale("fr")

    assert isinstance(dialog, RecordingSettingsDialog)
    assert dialog.windowTitle() == translate("recording.title")
    assert dialog.browse_button.text() == translate("recording.browse")
    # The operator's own text is not translated and not cleared.
    assert dialog.text_edit.text() == "bench-run-4"
    assert dialog.template_edit.text() == "{profile}-{iteration:03d}"
    dialog.reject()


def test_the_export_dialog_retranslates_while_keeping_its_selection(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path))
    window._render_frames([_speed_frame(1.0, 1234)])
    dialog = window._open_export_dialog()
    qtbot.addWidget(dialog)
    assert isinstance(dialog, ExportDialog)
    dialog.set_destination(tmp_path / "out.csv")
    scope_before = dialog.scope
    signals_before = dialog.selected_signals

    window._select_locale("fr")

    assert dialog.windowTitle() == translate("export.title")
    assert dialog.run_button.text() == translate("export.run")
    assert dialog.scope == scope_before
    assert dialog.selected_signals == signals_before
    assert dialog.destination == tmp_path / "out.csv"
    dialog.reject()


# ---- state and session continuity -----------------------------------------


def test_switching_language_never_mutates_the_measurement_setup(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    profile = window.selected_profile
    before = profile.to_dict()

    window._select_locale("fr")
    window._select_locale("en")

    assert window.selected_profile.to_dict() == before


def test_switching_language_keeps_every_selector_on_its_stored_value(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    bar = window.acquisition_bar
    bitrate = bar.bitrate_selector.currentData()
    mode = bar.controller_mode_selector.currentData()
    workspace_mode = window.workspace_mode_selector.currentData()

    window._select_locale("fr")

    assert bar.bitrate_selector.currentData() == bitrate
    assert bar.controller_mode_selector.currentData() == mode
    assert window.workspace_mode_selector.currentData() == workspace_mode
    # The captions did change, by item data rather than by rebuilding.
    assert window.workspace_mode_selector.currentText() == translate("workspace.mode_combo")


def test_switching_language_preserves_filters_selection_and_shown_signals(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path))
    window._render_frames([_speed_frame(float(index), 1000 + index) for index in range(8)])
    signal = next(iter(window._catalog.signal_references())).signal_key
    window._signal_shown_changed(signal, True)
    window._signal_favorite_changed(signal, True)
    window.trace_panel.filter_bar.id_filter.setText("0x123")
    window.trace_panel.filter_bar._read_filters()
    window.trace_table.setCurrentCell(2, 0)
    selected_row = window.trace_table.currentRow()
    rows_before = window.trace_table.rowCount()

    window._select_locale("fr")
    window._select_locale("en")

    assert window._selected_signal_names == {signal}
    assert window._favorite_signal_names == {signal}
    assert window.trace_panel.filter_bar.id_filter.text() == "0x123"
    assert window.trace_panel.settings.arbitration_id == "0x123"
    assert window.trace_table.currentRow() == selected_row
    assert window.trace_table.rowCount() == rows_before


def test_switching_language_keeps_the_cursors_and_the_measured_range(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path))
    window._render_frames([_speed_frame(float(index), 1000 + index) for index in range(10)])
    window.graph_panel.cursor_a = 2.0
    window.graph_panel.cursor_b = 6.0
    window.graph_panel._apply_cursor_lines()
    window_before = window.graph_panel.visible_window()

    window._select_locale("fr")

    assert window.graph_panel.cursor_a == 2.0
    assert window.graph_panel.cursor_b == 6.0
    assert window.graph_panel.visible_window() == window_before
    assert "2.000s" in window.graph_panel.cursor_summary.text()


def test_switching_language_during_live_capture_touches_no_worker(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._start_acquisition()
    qtbot.waitUntil(lambda: window.trace_table.rowCount() > 0)
    worker = window._worker
    session = window._facts.source
    frames_before = window._facts.report().frame_count

    window._select_locale("fr")
    window._select_locale("en")

    assert window._worker is worker
    assert worker.isRunning()
    assert window._facts.source == session
    assert window._facts.report().frame_count >= frames_before
    assert window.bus_state == "running"
    window._stop_acquisition()
    qtbot.waitUntil(lambda: window.start_button.isEnabled())


def test_a_warning_already_on_screen_re_reads_in_the_new_language(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._start_acquisition()
    qtbot.waitUntil(lambda: window.trace_table.rowCount() > 0)
    window._open_trace(tmp_path / "unused.asc")
    assert window.session_note.text() == translate("trace.open_blocked_by_acquisition")

    window._select_locale("fr")

    assert window.session_note.text() == translate_in(
        "fr", "trace.open_blocked_by_acquisition"
    )
    window._stop_acquisition()
    qtbot.waitUntil(lambda: window.start_button.isEnabled())


def test_a_message_keeps_its_verbatim_driver_detail_in_both_languages(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    window._report_dbc_error(Path("bench.dbc"), "PCAN_ERROR_ILLHW 0x1400")
    english = window.session_note.text()
    window._select_locale("fr")
    french = window.session_note.text()

    assert english != french
    assert "PCAN_ERROR_ILLHW 0x1400" in english
    assert "PCAN_ERROR_ILLHW 0x1400" in french
    assert "bench.dbc" in french


# ---- data and format contracts --------------------------------------------


def test_switching_language_leaves_can_identities_and_values_untouched(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path))
    window._render_frames([_speed_frame(1.0, 1234)])
    window.trace_table.setCurrentCell(0, 0)
    english = window.inspector.text()

    window._select_locale("fr")
    french = window.inspector.text()

    for token in ("0x123", "VehicleStatus", "Speed", "km/h", "1.000000"):
        assert token in english, token
        assert token in french, token
    # The prose around those facts is what changed.
    assert french.splitlines()[0] == translate("inspector.frame_heading").upper()
    assert french != english


def test_the_session_report_states_the_same_facts_in_both_languages():
    facts = SessionFacts()
    facts.reset("bench.asc")
    for index in range(4):
        facts.record_frame(_speed_frame(float(index), 1000 + index), decoded=index % 2 == 0)

    report = facts.report()
    english = ReportRenderer(report).render()
    from peaklive.i18n import set_locale

    set_locale("fr")
    french = ReportRenderer(report).render()

    assert english != french
    assert translate_in("fr", "report.heading") in french
    # Identical facts: the source, the counts and the coverage are unchanged.
    for token in ("bench.asc", "0x123", "50.0%", "count=4"):
        assert token in english, token
        assert token in french, token
    assert len(english.splitlines()) == len(french.splitlines())


def test_a_report_on_screen_is_re_rendered_after_a_language_change(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path))
    window._render_frames([_speed_frame(1.0, 1234)])
    window._refresh_report()
    english = window.report_panel.text

    window._select_locale("fr")

    assert window.report_panel.text != english
    assert translate_in("fr", "report.heading") in window.report_panel.text
    assert window.report_panel.view.toPlainText() == window.report_panel.text


def test_an_exported_signal_file_is_identical_whatever_the_interface_language(
    qtbot, tmp_path
):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path))
    window._render_frames([_speed_frame(float(index), 1000 + index) for index in range(5)])
    english_file = tmp_path / "english.csv"
    dialog = window._open_export_dialog()
    qtbot.addWidget(dialog)
    dialog.set_destination(english_file)
    dialog.run_export(blocking=True)
    dialog.reject()

    window._select_locale("fr")
    french_file = tmp_path / "french.csv"
    dialog = window._open_export_dialog()
    qtbot.addWidget(dialog)
    dialog.set_destination(french_file)
    dialog.run_export(blocking=True)
    dialog.reject()

    assert english_file.read_text(encoding="utf-8") == french_file.read_text(encoding="utf-8")


def test_trace_filters_match_the_stored_decode_code_not_its_caption(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_dbc(tmp_path))
    window._render_frames([_speed_frame(1.0, 1234), CanFrame(2.0, 0x456, b"\xff")])
    filter_bar = window.trace_panel.filter_bar
    filter_bar.status_filter.setCurrentIndex(filter_bar.status_filter.findData("decoded"))
    filter_bar._read_filters()
    window.trace_panel.refresh()
    shown_before = window.trace_table.rowCount()

    window._select_locale("fr")

    assert shown_before == 1
    assert filter_bar.status_filter.currentData() == "decoded"
    assert filter_bar.status_filter.currentText() == translate("trace.decode_decoded")
    assert window.trace_panel.settings.decode_status == "decoded"
    assert window.trace_table.rowCount() == shown_before


def test_an_active_filter_chip_re_reads_without_altering_the_filter(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    filter_bar = window.trace_panel.filter_bar
    filter_bar.id_filter.setText("0x123")
    filter_bar._read_filters()
    english = filter_bar.chips_layout.itemAt(0).widget().accessibleName()

    window._select_locale("fr")
    french = filter_bar.chips_layout.itemAt(0).widget().accessibleName()

    assert english == "ID 0x123"
    assert french == "ID 0x123"
    assert filter_bar.settings.arbitration_id == "0x123"


# ---- layout ----------------------------------------------------------------


@pytest.mark.parametrize("size", SUPPORTED_VIEWPORTS, ids=lambda s: f"{s.width()}x{s.height()}")
@pytest.mark.parametrize("locale", ("en", "fr"))
def test_both_languages_stay_operable_at_every_supported_viewport(
    qtbot, tmp_path, size, locale
):
    window = _window(qtbot, tmp_path, show=True)
    window._select_locale(locale)
    window.resize(size)
    qtbot.waitExposed(window)

    header = window.workspace_header
    assert window.width() <= size.width()
    # Every registered command stays reachable: on the row, or in the overflow
    # menu the row folds it into, never simply gone.
    for widget in header._order:
        if widget is window.acquisition_bar.recover_button:
            # Hidden outside a timed-out shutdown by design, in both languages.
            continue
        assert widget.isVisibleTo(window) or widget.parent() is header._overflow_panel
    for panel in window._layout_panels:
        assert panel.heading.text() == panel.heading.text().upper()


def test_french_accents_survive_the_round_trip_to_the_widgets(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)

    window._select_locale("fr")

    captions = {label.text() for label, _ in window.acquisition_bar._captions}
    assert window.trace_panel.filter_bar.show_events.text() == "Événements"
    # Upper-casing a caption must keep its accents rather than strip them.
    assert "DÉBIT" in captions
    assert window.trace_panel.filter_bar.time_end_filter.placeholderText() == "À (s)"
