"""item_141 - the setup strip is gone and the bus state lives in the header.

Configuration moved into the top menus in an earlier slice, but the visible
`AcquisitionBar` row stayed behind, spending a band of workspace height on
controls the menus already own. The row is removed here; everything that was
only reachable from it - profile selection, the timed-out recovery action and
the bus indicator - has to land somewhere the operator can still reach, and
the indicator has to be the same one in every centre view.
"""

from __future__ import annotations

from PySide6.QtWidgets import QMenu

from peaklive.adapters import FakeCanAdapter
from peaklive.domain import CanFrame
from peaklive.services.lifecycle import AcquisitionPhase
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow


def _window(qtbot, tmp_path, *, show: bool = False) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    if show:
        window.resize(1280, 720)
        window.show()
        qtbot.waitExposed(window)
    return window


def _menu(window: MainWindow, title: str) -> QMenu:
    return next(
        entry.menu()
        for entry in window.menuBar().actions()
        if entry.menu() is not None and entry.text().replace("&", "") == title
    )


def _submenu(menu: QMenu, object_name: str) -> QMenu:
    return next(
        action.menu()
        for action in menu.actions()
        if action.menu() is not None and action.menu().objectName() == object_name
    )


# --------------------------------------------------------------------------
# AC1 - no visible strip, and its height belongs to the workspace
# --------------------------------------------------------------------------


def test_the_measurement_profile_strip_is_not_on_screen(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)

    assert not window.acquisition_bar.isVisible()


def test_the_strip_claims_no_layout_band_above_the_workspace(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)

    root = window.centralWidget()
    layout = root.layout()
    widgets = {layout.itemAt(index).widget() for index in range(layout.count())}
    assert window.acquisition_bar not in widgets
    # The workspace now starts above where a strip of the bar's own height
    # would have pushed it, so that band really is reclaimed rather than
    # merely hidden behind an empty widget.
    assert window.workspace.y() < window.acquisition_bar.sizeHint().height()


# --------------------------------------------------------------------------
# AC2 - everything the strip alone offered is still reachable
# --------------------------------------------------------------------------


def test_profile_selection_moved_into_setup_as_persistent_checkable_choices(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._state.profiles.append(window.selected_profile.duplicate("Second setup"))
    window.profile_selector.addItem("Second setup")
    window._sync_setup_menu_enabled()

    entries = _submenu(_menu(window, "Setup"), "menu_profile").actions()
    names = [window.profile_selector.itemText(i) for i in range(window.profile_selector.count())]

    assert [entry.text() for entry in entries] == names
    assert all(entry.isCheckable() for entry in entries)
    assert entries[0].isChecked()

    entries[1].trigger()

    assert window.profile_selector.currentIndex() == 1
    assert _submenu(_menu(window, "Setup"), "menu_profile").actions()[1].isChecked()


def test_the_other_relocated_commands_keep_their_existing_menu_homes(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    setup_names = {action.objectName() for action in _menu(window, "Setup").actions()}
    file_names = {action.objectName() for action in _menu(window, "File").actions()}
    recording_names = {action.objectName() for action in _menu(window, "Recording").actions()}

    assert "menu_save_profile_as" in setup_names
    assert {"menu_load_dbc", "menu_open_trace", "menu_export"} <= file_names
    assert {"menu_start", "menu_stop"} <= recording_names


def test_timed_out_recovery_stays_reachable_from_the_workspace_header(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)
    recover = window.acquisition_bar.recover_button

    assert recover.parent() is window.workspace_header
    assert not recover.isVisible()

    window.acquisition_bar.set_lifecycle_phase(AcquisitionPhase.TIMED_OUT)

    assert recover.isVisible()
    assert recover.isEnabled()


def test_the_setup_choices_still_gate_themselves_on_the_lifecycle(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    def channel_entries() -> list[bool]:
        submenu = _submenu(_menu(window, "Setup"), "menu_channel")
        return [entry.isEnabled() for entry in submenu.actions()]

    window.acquisition_bar.set_lifecycle_phase(AcquisitionPhase.RUNNING)
    window._sync_setup_menu_enabled()
    running = channel_entries()

    window.acquisition_bar.set_lifecycle_phase(AcquisitionPhase.STOPPED)
    window._sync_setup_menu_enabled()
    stopped = channel_entries()

    assert not any(running)
    assert all(stopped)


# --------------------------------------------------------------------------
# AC3 - one bus indicator, beside Play/Stop, in every centre view
# --------------------------------------------------------------------------


def test_one_bus_indicator_sits_beside_play_and_stop(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)
    header = window.workspace_header
    indicator = window.acquisition_bar.bus_state_frame

    assert indicator.parent() is header
    assert indicator.isVisible()
    row = header.row
    order = [row.itemAt(index).widget() for index in range(row.count())]
    assert order.index(indicator) == order.index(window.stop_button) + 1


def test_the_one_indicator_stays_visible_in_every_centre_view(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)
    indicator = window.acquisition_bar.bus_state_frame

    for mode in ("combo", "graphs", "trace", "report"):
        window._apply_workspace_mode(mode)
        qtbot.wait(10)
        assert indicator.isVisible(), mode


def test_the_indicator_names_every_state_in_words_not_only_colour(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)
    label = window.acquisition_bar.bus_state_label

    seen = {}
    for phase, expected in (
        (AcquisitionPhase.RUNNING, "Running"),
        (AcquisitionPhase.STOPPING, "Stopping"),
        (AcquisitionPhase.FAILED, "Bus error"),
        (AcquisitionPhase.TIMED_OUT, "Shutdown degraded"),
    ):
        window.acquisition_bar.set_lifecycle_phase(phase)
        seen[phase] = label.text()
        assert label.text() == expected
        assert "Bus" in label.accessibleName()

    assert len(set(seen.values())) == len(seen)


def test_arriving_frames_read_as_running_only_while_the_session_is_running(qtbot, tmp_path):
    """Frames keep arriving all through a stop; they must not undo the phase."""
    window = _window(qtbot, tmp_path)
    generation = window._lifecycle.begin()
    window._lifecycle.advance(generation, AcquisitionPhase.RUNNING)
    window.acquisition_bar.set_lifecycle_phase(AcquisitionPhase.RUNNING)

    window._ingest_frames([CanFrame(0.0, 0x123, b"\x01" * 8)])
    assert window.bus_state == "running"

    window._lifecycle.advance(generation, AcquisitionPhase.STOPPING)
    window.acquisition_bar.set_lifecycle_phase(AcquisitionPhase.STOPPING)

    window._ingest_frames([CanFrame(0.001, 0x123, b"\x02" * 8)])
    assert window.bus_state == "stopping"


def test_the_indicator_tooltip_still_carries_the_read_only_channel_summary(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, show=True)

    tooltip = window.acquisition_bar.bus_state_frame.toolTip()

    assert "APP READ-ONLY" in tooltip
    assert "Bus" in tooltip
