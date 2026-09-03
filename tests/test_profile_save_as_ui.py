"""item_050 coverage: Save As, setup isolation, loading, and missing DBC feedback."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QInputDialog

from peaklive.adapters import FakeCanAdapter
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow

VEHICLE_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 291 VehicleStatus: 8 ECU
 SG_ Speed : 0|16@1+ (0.1,0) [0|250] "km/h" ECU
'''


def _window(qtbot, tmp_path, subdirectory: str = "setups"):
    window = MainWindow(ProfileStore(tmp_path / subdirectory), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    return window


def _answer(monkeypatch, text: str, accepted: bool = True):
    monkeypatch.setattr(
        QInputDialog, "getText", staticmethod(lambda *a, **k: (text, accepted))
    )


def test_the_save_as_affordance_is_reachable_and_labelled(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    button = window.acquisition_bar.save_profile_as_button

    assert button.accessibleName()
    assert button.toolTip()
    action = window.findChild(type(window.cursor_a_action), "menu_save_profile_as")
    assert action is not None
    assert not action.shortcut().isEmpty()


def test_save_as_creates_selects_and_persists_an_independent_setup(
    qtbot, tmp_path, monkeypatch
):
    window = _window(qtbot, tmp_path)
    window.selected_profile.recording.text = "origin"
    _answer(monkeypatch, "Vehicle bench")

    window.acquisition_bar.save_profile_as_button.click()

    assert window.selected_profile.name == "Vehicle bench"
    assert window.profile_selector.currentText() == "Vehicle bench"
    assert window.profile_selector.count() == 2
    assert window.selected_profile.recording.text == "origin"

    reloaded = ProfileStore(tmp_path / "setups").load()
    assert reloaded.selected.name == "Vehicle bench"
    assert len(reloaded.profiles) == 2


def test_cancelling_the_prompt_changes_nothing(qtbot, tmp_path, monkeypatch):
    window = _window(qtbot, tmp_path)
    before = window.selected_profile.identifier
    _answer(monkeypatch, "Ignored", accepted=False)

    window.acquisition_bar.save_profile_as_button.click()

    assert window.profile_selector.count() == 1
    assert window.selected_profile.identifier == before
    assert len(ProfileStore(tmp_path / "setups").load().profiles) == 1


def test_a_blank_name_is_refused_with_accessible_feedback(qtbot, tmp_path, monkeypatch):
    window = _window(qtbot, tmp_path)
    _answer(monkeypatch, "   ")

    window.acquisition_bar.save_profile_as_button.click()

    assert window.profile_selector.count() == 1
    assert window.session_note.level == "warning"
    assert window.session_note.text()
    assert len(ProfileStore(tmp_path / "setups").load().profiles) == 1


def test_a_duplicate_name_is_refused_and_leaves_the_setups_alone(
    qtbot, tmp_path, monkeypatch
):
    window = _window(qtbot, tmp_path)
    _answer(monkeypatch, window.selected_profile.name)

    window.acquisition_bar.save_profile_as_button.click()

    assert window.profile_selector.count() == 1
    assert window.session_note.level == "warning"
    assert len(ProfileStore(tmp_path / "setups").load().profiles) == 1


def test_later_edits_to_one_setup_never_reach_the_other(qtbot, tmp_path, monkeypatch):
    window = _window(qtbot, tmp_path)
    origin = window.selected_profile
    origin.recording.text = "origin"
    _answer(monkeypatch, "Copy")
    window.acquisition_bar.save_profile_as_button.click()

    copy = window.selected_profile
    copy.recording.text = "copy"
    copy.favorite_signals.append("Powertrain.Rpm")
    window._save()

    assert origin.recording.text == "origin"
    assert origin.favorite_signals == []
    stored = {p.name: p for p in ProfileStore(tmp_path / "setups").load().profiles}
    assert stored["Default measurement"].recording.text == "origin"
    assert stored["Copy"].recording.text == "copy"


def test_the_selector_reloads_each_saved_setup_after_a_restart(
    qtbot, tmp_path, monkeypatch
):
    window = _window(qtbot, tmp_path)
    window.selected_profile.bitrate = 125_000
    window._save()
    _answer(monkeypatch, "Fast bench")
    window.acquisition_bar.save_profile_as_button.click()
    window.acquisition_bar.bitrate_selector.setCurrentIndex(
        window.acquisition_bar.bitrate_selector.findData(1_000_000)
    )

    restarted = _window(qtbot, tmp_path)
    assert restarted.selected_profile.name == "Fast bench"
    assert restarted.selected_profile.bitrate == 1_000_000

    restarted.profile_selector.setCurrentIndex(0)
    assert restarted.selected_profile.name == "Default measurement"
    assert restarted.selected_profile.bitrate == 125_000


def test_an_unavailable_dbc_is_reported_without_dropping_the_reference(
    qtbot, tmp_path, monkeypatch
):
    readable = tmp_path / "vehicle.dbc"
    readable.write_text(VEHICLE_DBC, encoding="utf-8")
    missing = tmp_path / "gone.dbc"

    window = _window(qtbot, tmp_path)
    _answer(monkeypatch, "Bench with DBC")
    window.acquisition_bar.save_profile_as_button.click()
    window.selected_profile.dbc_paths = [str(readable), str(missing)]
    window._save()

    restarted = _window(qtbot, tmp_path)
    qtbot.waitUntil(lambda: restarted.dbc_panel.note.level == "error", timeout=5_000)

    assert Path(missing).name in restarted.dbc_panel.note.text()
    # The unreadable reference is kept, and the readable database still loaded.
    assert str(missing) in restarted.selected_profile.dbc_paths
    assert "VehicleStatus.Speed" in restarted._catalog.signal_names()
    assert str(missing) in ProfileStore(tmp_path / "setups").load().selected.dbc_paths
