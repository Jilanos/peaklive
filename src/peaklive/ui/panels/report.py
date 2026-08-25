"""The session diagnostic report view."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from peaklive.analysis import ReportRenderer, SessionReport
from peaklive.i18n import translate
from peaklive.ui.widgets import StateNote


class ReportPanel(QWidget):
    """Shows the session synthesis and exports it verbatim to a local file."""

    refresh_requested = Signal()
    export_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.text = ""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        actions = QHBoxLayout()
        self.refresh_button = QPushButton(translate("report.refresh"), objectName="reportRefresh")
        self.refresh_button.setToolTip(translate("report.refresh"))
        self.refresh_button.setAccessibleName(translate("report.refresh"))
        self.refresh_button.clicked.connect(self.refresh_requested)
        actions.addWidget(self.refresh_button)
        self.export_button = QPushButton(translate("report.export"), objectName="reportExport")
        self.export_button.setToolTip(translate("report.export"))
        self.export_button.setAccessibleName(translate("report.export"))
        self.export_button.clicked.connect(self.export_requested)
        actions.addWidget(self.export_button)
        actions.addStretch(1)
        layout.addLayout(actions)

        self.view = QPlainTextEdit(objectName="reportView")
        self.view.setAccessibleName(translate("report.accessible"))
        self.view.setReadOnly(True)
        layout.addWidget(self.view, 1)

        self.note = StateNote(translate("report.empty"))
        layout.addWidget(self.note)

    def show_report(self, report: SessionReport) -> None:
        self.text = ReportRenderer(report).render()
        self.view.setPlainText(self.text)
        if report.is_empty:
            self.note.show_message(translate("report.empty"), "info")
        else:
            self.note.clear_message()
        self.export_button.setEnabled(not report.is_empty)
