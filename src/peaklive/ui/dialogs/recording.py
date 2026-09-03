"""Profile-scoped recording settings: folder, template, iteration, and preview."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from peaklive.domain import MeasurementProfile
from peaklive.i18n import translate
from peaklive.recording import InvalidTemplateError, RecordingNaming
from peaklive.ui.widgets import StateNote


class RecordingSettingsDialog(QDialog):
    """Edits one profile's recording policy in place with an instant preview.

    Every field mutates ``profile.recording`` directly and emits
    ``recording_changed`` immediately, the same pattern ``ColumnsDialog`` uses,
    so the shell's existing persistence and profile-switch handling apply
    without any dialog-specific save path.
    """

    recording_changed = Signal()

    def __init__(
        self,
        profile: MeasurementProfile,
        naming: RecordingNaming | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("recordingSettingsDialog")
        self.setWindowTitle(translate("recording.title"))
        self._profile = profile
        self._naming = naming or RecordingNaming()

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.enabled_checkbox = QCheckBox(objectName="recordingEnabled")
        self.enabled_checkbox.setAccessibleName(translate("recording.enabled"))
        self.enabled_checkbox.setToolTip(translate("recording.enabled_tooltip"))
        self.enabled_checkbox.setChecked(profile.recording.enabled)
        self.enabled_checkbox.toggled.connect(self._set_enabled)
        form.addRow(QLabel(translate("recording.enabled")), self.enabled_checkbox)

        directory_row = QHBoxLayout()
        self.directory_edit = QLineEdit(
            profile.recording.directory, objectName="recordingDirectory"
        )
        self.directory_edit.setReadOnly(True)
        self.directory_edit.setAccessibleName(translate("recording.directory"))
        self.directory_edit.setToolTip(translate("recording.directory_tooltip"))
        self.directory_edit.setPlaceholderText(translate("recording.directory_default"))
        directory_row.addWidget(self.directory_edit, 1)
        self.browse_button = QPushButton(
            translate("recording.browse"), objectName="recordingBrowse"
        )
        self.browse_button.setAccessibleName(translate("recording.browse"))
        self.browse_button.clicked.connect(self._browse)
        directory_row.addWidget(self.browse_button)
        directory_host = QWidget()
        directory_host.setLayout(directory_row)
        form.addRow(QLabel(translate("recording.directory")), directory_host)

        self.template_edit = QLineEdit(
            profile.recording.filename_template, objectName="recordingTemplate"
        )
        self.template_edit.setAccessibleName(translate("recording.template"))
        self.template_edit.setToolTip(translate("recording.template_tooltip"))
        self.template_edit.textChanged.connect(self._set_template)
        form.addRow(QLabel(translate("recording.template")), self.template_edit)

        iteration_row = QHBoxLayout()
        self.iteration_spin = QSpinBox(objectName="recordingIteration")
        self.iteration_spin.setAccessibleName(translate("recording.iteration"))
        self.iteration_spin.setToolTip(translate("recording.iteration_tooltip"))
        self.iteration_spin.setRange(1, 999_999)
        self.iteration_spin.setValue(profile.recording.iteration)
        self.iteration_spin.valueChanged.connect(self._set_iteration)
        iteration_row.addWidget(self.iteration_spin, 1)
        self.reset_button = QPushButton(translate("recording.reset"), objectName="recordingReset")
        self.reset_button.setAccessibleName(translate("recording.reset"))
        self.reset_button.setToolTip(translate("recording.reset_tooltip"))
        self.reset_button.clicked.connect(self._reset_iteration)
        iteration_row.addWidget(self.reset_button)
        iteration_host = QWidget()
        iteration_host.setLayout(iteration_row)
        form.addRow(QLabel(translate("recording.iteration")), iteration_host)

        self.preview_label = QLabel(objectName="recordingPreview")
        self.preview_label.setAccessibleName(translate("recording.preview"))
        self.preview_label.setToolTip(translate("recording.preview_tooltip"))
        form.addRow(QLabel(translate("recording.preview")), self.preview_label)

        layout.addLayout(form)

        self.note = StateNote()
        layout.addWidget(self.note)

        actions = QHBoxLayout()
        actions.addStretch(1)
        self.close_button = QPushButton(translate("recording.close"), objectName="recordingClose")
        self.close_button.setDefault(True)
        self.close_button.clicked.connect(self.accept)
        actions.addWidget(self.close_button)
        layout.addLayout(actions)

        self._refresh_preview()

    # ---- field mutation -------------------------------------------------

    def _set_enabled(self, checked: bool) -> None:
        self._profile.recording.enabled = checked
        self.recording_changed.emit()

    def _browse(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            self, translate("recording.browse"), self._profile.recording.directory
        )
        if not selected:
            return
        self._profile.recording.directory = selected
        self.directory_edit.setText(selected)
        self._refresh_preview()
        self.recording_changed.emit()

    def _set_template(self, text: str) -> None:
        self._profile.recording.filename_template = text
        self._refresh_preview()
        self.recording_changed.emit()

    def _set_iteration(self, value: int) -> None:
        self._profile.recording.iteration = value
        self._refresh_preview()
        self.recording_changed.emit()

    def _reset_iteration(self) -> None:
        self.iteration_spin.setValue(1)

    # ---- preview ----------------------------------------------------------

    def _refresh_preview(self) -> None:
        """Show the exact next filename, never touching the filesystem."""
        try:
            filename = self._naming.preview(self._profile.recording, self._profile.name)
        except InvalidTemplateError as error:
            self.preview_label.setText(translate("recording.preview_invalid"))
            self.note.show_message(str(error), "error")
            return
        self.note.clear_message()
        self.preview_label.setText(filename)
