from PySide6.QtCore import Qt

from peaklive.domain import CanFrame
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow

DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 291 VehicleStatus: 8 ECU
 SG_ Speed : 0|16@1+ (0.1,0) [0|250] "km/h" ECU
'''


def test_main_window_has_accessible_workspace_and_explicit_lifecycle(qtbot, tmp_path):
    window = MainWindow(ProfileStore(tmp_path))
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
    window = MainWindow(ProfileStore(tmp_path / "settings"))
    qtbot.addWidget(window)

    window._load_dbc_path(dbc_path)
    window._render_frames([CanFrame(10.0, 291, b"\xd2\x04" + b"\x00" * 6)])

    assert window.signal_explorer.currentItem().text() == "VehicleStatus.Speed"
    assert window._plot_curve.getData()[1].tolist() == [123.4]
    assert "123.4 km/h" in window.inspector.text()
    assert str(dbc_path) in window.selected_profile.dbc_paths
