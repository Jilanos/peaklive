"""Regression coverage pinning the delivered req_001 CanTraceDiag parity surface.

These behaviors were validated by the first parity wave. They are pinned here so
the workspace decomposition and the later analyst slices cannot silently drop
them. Every assertion runs headless against fake adapters and DBC fixtures.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolButton

from peaklive.adapters import FakeCanAdapter
from peaklive.domain import ControllerMode
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow
from peaklive.ui.main_window import SIGNAL_KEY_ROLE

VEHICLE_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 291 VehicleStatus: 8 ECU
 SG_ Speed : 0|16@1+ (0.1,0) [0|250] "km/h" ECU
'''

BODY_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 292 BodyStatus: 8 ECU
 SG_ DoorOpen : 0|1@1+ (1,0) [0|1] "" ECU
'''

# Same arbitration ID as VEHICLE_DBC with a different layout: a real conflict.
CONFLICTING_DBC = '''VERSION ""
NS_ :
BS_:
BU_: GATEWAY
BO_ 291 GatewayStatus: 8 GATEWAY
 SG_ Torque : 0|12@1+ (0.5,0) [0|2000] "Nm" GATEWAY
'''


def _window(qtbot, tmp_path):
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    return window


def _write(tmp_path, name: str, text: str):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _signal_item(window, key: str):
    for item in window.signal_explorer.findItems(
        "",
        Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive,
        0,
    ):
        if item.data(0, SIGNAL_KEY_ROLE) == key:
            return item
    raise AssertionError(f"Signal item not found: {key}")


def test_parity_multi_dbc_library_shows_state_and_supports_disable_and_remove(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    vehicle = _write(tmp_path, "vehicle.dbc", VEHICLE_DBC)
    body = _write(tmp_path, "body.dbc", BODY_DBC)

    window._load_dbc_path(vehicle)
    window._load_dbc_path(body)
    assert window.dbc_library.topLevelItemCount() == 2
    assert {str(vehicle), str(body)} == set(window.selected_profile.dbc_paths)

    # Enable, disable, and remove are prepared off the UI thread and committed
    # in one step, so each assertion waits for that commit rather than assuming
    # the mutation happened inside the click.
    window.dbc_library.topLevelItem(0).setCheckState(0, Qt.CheckState.Unchecked)
    qtbot.waitUntil(lambda: bool(window.selected_profile.trace_filters["disabled_dbc_hashes"]))

    window.dbc_library.topLevelItem(0).setCheckState(0, Qt.CheckState.Checked)
    qtbot.waitUntil(lambda: not window.selected_profile.trace_filters["disabled_dbc_hashes"])

    window.dbc_library.setCurrentItem(window.dbc_library.topLevelItem(0))
    window._remove_selected_dbc()
    qtbot.waitUntil(lambda: window.dbc_library.topLevelItemCount() == 1)
    assert len(window.selected_profile.dbc_paths) == 1


def test_parity_dbc_conflicts_are_explicit_and_resolution_persists(qtbot, tmp_path):
    store = ProfileStore(tmp_path / "settings")
    window = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window._load_dbc_path(_write(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    window._load_dbc_path(_write(tmp_path, "gateway.dbc", CONFLICTING_DBC))

    assert window.conflict_selector.count() > 1

    window.conflict_selector.setCurrentIndex(1)
    qtbot.waitUntil(
        lambda: bool(store.load().selected.trace_filters["dbc_conflict_resolutions"])
    )
    resolutions = store.load().selected.trace_filters["dbc_conflict_resolutions"]

    assert "291" in resolutions


def test_parity_signal_explorer_groups_filters_and_favorites(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_write(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    window._load_dbc_path(_write(tmp_path, "body.dbc", BODY_DBC))

    # DBC -> message -> signal grouping.
    assert window.signal_explorer.topLevelItemCount() == 2
    dbc_item = window.signal_explorer.topLevelItem(0)
    assert dbc_item.childCount() == 1
    assert dbc_item.child(0).childCount() == 1

    door = _signal_item(window, "BodyStatus.DoorOpen")
    door.setCheckState(1, Qt.CheckState.Checked)
    door.setCheckState(2, Qt.CheckState.Checked)
    assert "BodyStatus.DoorOpen" in window.selected_profile.displayed_signals
    assert window.selected_profile.favorite_signals == ["BodyStatus.DoorOpen"]

    window.signal_filter.setText("doorop")
    window._signal_explorer_debouncer.flush()
    assert window.signal_explorer.topLevelItemCount() == 1

    window.signal_filter.setText("")
    window.favorites_only_checkbox.setChecked(True)
    window._signal_explorer_debouncer.flush()
    assert window.signal_explorer.topLevelItemCount() == 1
    window.favorites_only_checkbox.setChecked(False)

    window.shown_only_checkbox.setChecked(True)
    window._signal_explorer_debouncer.flush()
    shown_keys = {
        item.data(0, SIGNAL_KEY_ROLE)
        for item in window.signal_explorer.findItems(
            "", Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive, 0
        )
        if item.data(0, SIGNAL_KEY_ROLE)
    }
    assert shown_keys == set(window.selected_profile.displayed_signals)


def test_parity_graph_stack_renders_one_plot_per_shown_signal_with_cursors(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    # With no DBC signal shown, the raw-byte preview keeps the workspace useful.
    assert set(window._plot_curves) == {"Raw byte 0"}
    assert window.live_plot.accessibleName() == "Live signal plot"

    window._load_dbc_path(_write(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    window._load_dbc_path(_write(tmp_path, "body.dbc", BODY_DBC))
    _signal_item(window, "BodyStatus.DoorOpen").setCheckState(1, Qt.CheckState.Checked)

    assert set(window._plot_curves) == {"BodyStatus.DoorOpen", "VehicleStatus.Speed"}
    for plot in window._plot_widgets.values():
        assert plot._peaklive_cursor_a is not None
        assert plot._peaklive_cursor_b is not None


def test_parity_panels_collapse_independently_without_losing_state(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window.show()
    window._load_dbc_path(_write(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    displayed = list(window.selected_profile.displayed_signals)

    for panel, body in (
        (window.signals_panel, window.signals_body),
        (window.inspector_panel, window.inspector_body),
        (window.trace_graph_panel, window.trace_graph_body),
    ):
        button = panel.findChild(QToolButton, "collapseButton")
        assert button is not None
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        assert not body.isVisible()
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        assert body.isVisible()

    assert list(window.selected_profile.displayed_signals) == displayed


def test_parity_workspace_modes_switch_graph_and_trace_visibility(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window.show()

    for mode, graphs_visible, trace_visible in (
        ("graphs", True, False),
        ("trace", False, True),
        ("combo", True, True),
    ):
        window.workspace_mode_selector.setCurrentIndex(
            window.workspace_mode_selector.findData(mode)
        )
        assert window.graph_scroll.isVisible() is graphs_visible
        assert window.trace_table.isVisible() is trace_visible


def test_parity_acquisition_setup_persists_and_stays_receive_only(qtbot, tmp_path):
    store = ProfileStore(tmp_path / "settings")
    window = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)

    window.bitrate_selector.setCurrentIndex(window.bitrate_selector.findData(1_000_000))
    window.capture_format_selector.setCurrentIndex(window.capture_format_selector.findData("trc"))
    window.controller_mode_selector.setCurrentIndex(
        window.controller_mode_selector.findData(ControllerMode.NORMAL_RECEIVE.value)
    )

    restored = store.load().selected
    assert restored.bitrate == 1_000_000
    assert restored.recording.capture_format == "trc"
    assert restored.controller_mode is ControllerMode.NORMAL_RECEIVE
    assert "APP READ-ONLY" in window.mode_label.text()

    # No transmit affordance may exist anywhere in the workspace.
    from PySide6.QtWidgets import QAbstractButton

    forbidden = ("transmit", "send", "tx frame")
    for button in window.findChildren(QAbstractButton):
        label = f"{button.text()} {button.objectName()} {button.accessibleName()}".casefold()
        assert not any(word in label for word in forbidden)


def test_parity_instrument_stylesheet_is_applied(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    style = window.styleSheet()
    assert "QFrame#instrument" in style
    assert "panelHeading" in style
