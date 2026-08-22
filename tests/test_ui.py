from PySide6.QtCore import Qt

from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow


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
    assert window.trace_table.rowCount() == 32
    assert len(window._plot_curve.getData()[0]) == 32

    qtbot.mouseClick(window.stop_button, Qt.MouseButton.LeftButton)
    assert window.start_button.isEnabled()
    assert not window.stop_button.isEnabled()
