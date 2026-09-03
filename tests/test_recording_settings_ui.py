"""item_049 coverage: the profile-scoped Recording settings route and preview."""

from __future__ import annotations

from PySide6.QtWidgets import QFileDialog

from peaklive.adapters import FakeCanAdapter
from peaklive.services.profiles import ProfileState, ProfileStore
from peaklive.ui import MainWindow
from peaklive.ui.dialogs import RecordingSettingsDialog


def _window(qtbot, tmp_path):
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    return window


def test_recording_settings_dialog_is_reachable_and_shows_the_profile(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window.selected_profile.recording.enabled = True
    window.selected_profile.recording.directory = str(tmp_path / "captures")
    window.selected_profile.recording.iteration = 3

    dialog = window._open_recording_dialog()
    qtbot.addWidget(dialog)

    assert dialog.enabled_checkbox.isChecked() is True
    assert dialog.directory_edit.text() == str(tmp_path / "captures")
    assert dialog.iteration_spin.value() == 3
    assert dialog.template_edit.accessibleName()
    assert dialog.directory_edit.accessibleName()
    assert dialog.iteration_spin.accessibleName()


def test_toggling_and_editing_fields_persists_through_profile_storage(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    dialog = window._open_recording_dialog()
    qtbot.addWidget(dialog)

    dialog.enabled_checkbox.setChecked(False)
    dialog.template_edit.setText("{profile}_{iteration:03d}")
    dialog.iteration_spin.setValue(9)

    reloaded = ProfileStore(tmp_path / "settings").load().selected
    assert reloaded.recording.enabled is False
    assert reloaded.recording.filename_template == "{profile}_{iteration:03d}"
    assert reloaded.recording.iteration == 9


def test_browse_cancellation_leaves_the_profile_unchanged(qtbot, tmp_path, monkeypatch):
    window = _window(qtbot, tmp_path)
    original = window.selected_profile.recording.directory
    dialog = window._open_recording_dialog()
    qtbot.addWidget(dialog)
    monkeypatch.setattr(
        QFileDialog, "getExistingDirectory", staticmethod(lambda *a, **k: "")
    )

    dialog._browse()

    assert window.selected_profile.recording.directory == original
    assert dialog.directory_edit.text() == original


def test_browse_selection_commits_and_persists_the_chosen_folder(qtbot, tmp_path, monkeypatch):
    window = _window(qtbot, tmp_path)
    dialog = window._open_recording_dialog()
    qtbot.addWidget(dialog)
    chosen = tmp_path / "chosen-folder"
    chosen.mkdir()
    monkeypatch.setattr(
        QFileDialog, "getExistingDirectory", staticmethod(lambda *a, **k: str(chosen))
    )

    dialog._browse()

    assert window.selected_profile.recording.directory == str(chosen)
    assert dialog.directory_edit.text() == str(chosen)
    reloaded = ProfileStore(tmp_path / "settings").load().selected
    assert reloaded.recording.directory == str(chosen)


def test_preview_updates_live_and_never_creates_a_file(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window.selected_profile.recording.directory = str(tmp_path / "captures")
    dialog = window._open_recording_dialog()
    qtbot.addWidget(dialog)

    dialog.template_edit.setText("bench_{iteration:03d}")
    dialog.iteration_spin.setValue(4)

    assert dialog.preview_label.text() == "bench_004.asc"
    assert not (tmp_path / "captures").exists()


def test_invalid_template_shows_actionable_feedback_and_placeholder_preview(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    dialog = window._open_recording_dialog()
    qtbot.addWidget(dialog)

    dialog.template_edit.setText("{unsupported}")

    assert dialog.preview_label.text() != "{unsupported}.asc"
    assert dialog.note.level == "error"
    assert dialog.note.text()


def test_reset_restarts_the_visible_iteration_at_one(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    dialog = window._open_recording_dialog()
    qtbot.addWidget(dialog)
    dialog.iteration_spin.setValue(42)

    dialog.reset_button.click()

    assert dialog.iteration_spin.value() == 1
    assert window.selected_profile.recording.iteration == 1


def test_each_profile_keeps_its_own_independent_recording_settings(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    store = window._store
    state: ProfileState = store.load()
    second = state.profiles[0]
    from peaklive.domain import MeasurementProfile

    third = MeasurementProfile(name="Second profile")
    store.save(ProfileState([second, third], second.identifier))
    window._state = store.load()
    window.acquisition_bar.profile_selector.clear()
    window.acquisition_bar.profile_selector.addItems([p.name for p in window._state.profiles])
    window._select_last_profile()

    window.acquisition_bar.profile_selector.setCurrentIndex(0)
    dialog_a = window._open_recording_dialog()
    qtbot.addWidget(dialog_a)
    dialog_a.template_edit.setText("first_{iteration:03d}")
    dialog_a.close()

    window.acquisition_bar.profile_selector.setCurrentIndex(1)
    dialog_b = window._open_recording_dialog()
    qtbot.addWidget(dialog_b)

    assert dialog_b.template_edit.text() != "first_{iteration:03d}"


def test_recording_dialog_can_be_constructed_headlessly(qtbot, tmp_path):
    """A pytest-qt offscreen instantiation exercises the same code as the menu action."""
    from peaklive.domain import MeasurementProfile

    profile = MeasurementProfile(name="Standalone")
    dialog = RecordingSettingsDialog(profile)
    qtbot.addWidget(dialog)

    assert dialog.windowTitle()


def test_the_text_field_sits_directly_below_next_iteration(qtbot, tmp_path):
    from PySide6.QtWidgets import QFormLayout

    window = _window(qtbot, tmp_path)
    dialog = window._open_recording_dialog()
    qtbot.addWidget(dialog)
    form = dialog.findChild(QFormLayout)

    rows = [
        form.itemAt(row, QFormLayout.ItemRole.FieldRole).widget()
        for row in range(form.rowCount())
    ]
    iteration_row = next(
        index
        for index, widget in enumerate(rows)
        if widget.findChild(type(dialog.iteration_spin)) is dialog.iteration_spin
    )

    assert rows[iteration_row + 1] is dialog.text_edit
    assert dialog.text_edit.accessibleName()
    assert dialog.text_edit.toolTip()


def test_editing_the_text_updates_the_preview_and_persists(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window.selected_profile.recording.directory = str(tmp_path / "captures")
    dialog = window._open_recording_dialog()
    qtbot.addWidget(dialog)

    dialog.template_edit.setText("bench_{text}_{iteration:03d}")
    dialog.text_edit.setText("roulage BL")

    assert dialog.preview_label.text() == "bench_roulage_BL_001.asc"
    assert not (tmp_path / "captures").exists()
    reloaded = ProfileStore(tmp_path / "settings").load().selected
    assert reloaded.recording.text == "roulage BL"


def test_the_text_belongs_to_one_setup_only(qtbot, tmp_path):
    from peaklive.domain import MeasurementProfile

    window = _window(qtbot, tmp_path)
    store = window._store
    state = store.load()
    first = state.profiles[0]
    second = MeasurementProfile(name="Second profile")
    store.save(ProfileState([first, second], first.identifier))
    window._state = store.load()
    window.acquisition_bar.profile_selector.clear()
    window.acquisition_bar.profile_selector.addItems([p.name for p in window._state.profiles])
    window._select_last_profile()

    window.acquisition_bar.profile_selector.setCurrentIndex(0)
    dialog_a = window._open_recording_dialog()
    qtbot.addWidget(dialog_a)
    dialog_a.text_edit.setText("first only")
    dialog_a.close()

    window.acquisition_bar.profile_selector.setCurrentIndex(1)
    dialog_b = window._open_recording_dialog()
    qtbot.addWidget(dialog_b)

    assert dialog_b.text_edit.text() == ""
    assert ProfileStore(tmp_path / "settings").load().profiles[0].recording.text == "first only"
