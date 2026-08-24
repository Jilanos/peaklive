from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolButton

from peaklive.adapters import FakeCanAdapter
from peaklive.domain import CanFrame, ControllerMode
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow
from peaklive.ui.main_window import SIGNAL_KEY_ROLE

DBC = '''VERSION ""
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


def test_main_window_has_accessible_workspace_and_explicit_lifecycle(qtbot, tmp_path):
    window = MainWindow(ProfileStore(tmp_path), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window.show()

    assert window.profile_selector.accessibleName() == "Measurement profile"
    assert window.trace_table.accessibleName() == "CAN trace"
    assert window.live_plot.accessibleName() == "Live signal plot"
    assert window.start_button.isEnabled()
    assert not window.stop_button.isEnabled()

    qtbot.mouseClick(window.start_button, Qt.MouseButton.LeftButton)
    assert not window.start_button.isEnabled()
    assert window.stop_button.isEnabled()
    qtbot.waitUntil(lambda: window.trace_table.rowCount() == 32)
    assert window.trace_table.rowCount() == 32
    assert len(window._plot_curve.getData()[0]) == 32

    qtbot.mouseClick(window.stop_button, Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda: window.start_button.isEnabled())
    assert window.start_button.isEnabled()
    assert not window.stop_button.isEnabled()


def test_main_window_loads_dbc_and_plots_selected_signal(qtbot, tmp_path):
    dbc_path = tmp_path / "vehicle.dbc"
    dbc_path.write_text(DBC, encoding="utf-8")
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)

    window._load_dbc_path(dbc_path)
    window._render_frames([CanFrame(10.0, 291, b"\xd2\x04" + b"\x00" * 6)])

    current = window.signal_explorer.currentItem()
    assert current is not None
    assert current.text(0) == "Speed [km/h]"
    assert window._plot_curve.getData()[1].tolist() == [123.4]
    assert "123.4 km/h" in window.inspector.text()
    assert str(dbc_path) in window.selected_profile.dbc_paths


def _signal_item(window: MainWindow, key: str):
    for item in window.signal_explorer.findItems(
        "",
        Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive,
        0,
    ):
        if item.data(0, SIGNAL_KEY_ROLE) == key:
            return item
    raise AssertionError(f"Signal item not found: {key}")


def test_main_window_manages_multi_dbc_signals_favorites_and_graphs(qtbot, tmp_path):
    vehicle_path = tmp_path / "vehicle.dbc"
    body_path = tmp_path / "body.dbc"
    vehicle_path.write_text(DBC, encoding="utf-8")
    body_path.write_text(BODY_DBC, encoding="utf-8")
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)

    window._load_dbc_path(vehicle_path)
    window._load_dbc_path(body_path)
    body_signal = _signal_item(window, "BodyStatus.DoorOpen")
    body_signal.setCheckState(1, Qt.CheckState.Checked)
    body_signal.setCheckState(2, Qt.CheckState.Checked)
    window._render_frames(
        [
            CanFrame(10.0, 291, b"\xd2\x04" + b"\x00" * 6),
            CanFrame(11.0, 292, b"\x01" + b"\x00" * 7),
        ]
    )

    assert window.dbc_library.topLevelItemCount() == 2
    assert set(window.selected_profile.displayed_signals) == {
        "BodyStatus.DoorOpen",
        "VehicleStatus.Speed",
    }
    assert window.selected_profile.favorite_signals == ["BodyStatus.DoorOpen"]
    assert set(window._plot_curves) == {"BodyStatus.DoorOpen", "VehicleStatus.Speed"}
    assert window._plot_curves["BodyStatus.DoorOpen"].getData()[1].tolist() == [1.0]

    window.shown_only_checkbox.setChecked(True)
    assert _signal_item(window, "BodyStatus.DoorOpen").text(0) == "DoorOpen"


def test_main_window_persists_acquisition_mode_and_collapsible_panels(qtbot, tmp_path):
    store = ProfileStore(tmp_path / "settings")
    window = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)

    window.bitrate_selector.setCurrentIndex(window.bitrate_selector.findData(250_000))
    window.controller_mode_selector.setCurrentIndex(
        window.controller_mode_selector.findData(ControllerMode.NORMAL_RECEIVE.value)
    )
    collapse_button = window.inspector_panel.findChild(QToolButton, "collapseButton")
    assert collapse_button is not None
    qtbot.mouseClick(collapse_button, Qt.MouseButton.LeftButton)

    restored = store.load().selected

    assert restored.bitrate == 250_000
    assert restored.controller_mode is ControllerMode.NORMAL_RECEIVE
    assert "APP READ-ONLY" in window.mode_label.text()
    assert "controller ACK" in window.mode_label.text()
    assert not window.inspector_body.isVisible()
