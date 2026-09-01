"""The export dialog: signals, format, range scope, streaming, and cancellation."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from peaklive.analysis import SeriesStore, export_rows
from peaklive.i18n import translate
from peaklive.services.export_worker import ExportWorker
from peaklive.ui.widgets import StateNote

SCOPE_CURSORS = "cursors"
SCOPE_WINDOW = "window"
SCOPE_ALL = "all"


class ExportDialog(QDialog):
    """Streams the selected signals over a chosen range to CSV or Parquet."""

    def __init__(
        self,
        store: SeriesStore,
        signal_names: Sequence[str],
        cursor_range: tuple[float, float] | None,
        visible_window: tuple[float, float] | None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("exportDialog")
        self.setWindowTitle(translate("export.title"))
        self._store = store
        self._cursor_range = cursor_range
        self._visible_window = visible_window
        self._worker: ExportWorker | None = None
        self.destination: Path | None = None
        self.written = 0

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.signal_list = QListWidget(objectName="exportSignals")
        self.signal_list.setAccessibleName(translate("export.signals"))
        self.signal_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for name in signal_names:
            self.signal_list.addItem(name)
        self.signal_list.selectAll()
        form.addRow(QLabel(translate("export.signals")), self.signal_list)

        self.format_selector = QComboBox(objectName="exportFormat")
        self.format_selector.setAccessibleName(translate("export.format"))
        self.format_selector.addItem(translate("export.format_csv"), "csv")
        self.format_selector.addItem(translate("export.format_parquet"), "parquet")
        form.addRow(QLabel(translate("export.format")), self.format_selector)

        self.scope_selector = QComboBox(objectName="exportScope")
        self.scope_selector.setAccessibleName(translate("export.scope"))
        self.scope_selector.addItem(translate("export.scope_cursors"), SCOPE_CURSORS)
        self.scope_selector.addItem(translate("export.scope_window"), SCOPE_WINDOW)
        self.scope_selector.addItem(translate("export.scope_all"), SCOPE_ALL)
        if cursor_range is None:
            self.scope_selector.setCurrentIndex(self.scope_selector.findData(SCOPE_ALL))
        form.addRow(QLabel(translate("export.scope")), self.scope_selector)

        destination_row = QHBoxLayout()
        self.destination_label = QLabel("—", objectName="exportDestination")
        destination_row.addWidget(self.destination_label, 1)
        self.browse_button = QPushButton(translate("export.browse"), objectName="exportBrowse")
        self.browse_button.clicked.connect(self.choose_destination)
        destination_row.addWidget(self.browse_button)
        destination_host = QWidget()
        destination_host.setLayout(destination_row)
        form.addRow(QLabel(translate("export.destination")), destination_host)
        layout.addLayout(form)

        self.progress = QProgressBar(objectName="exportProgress")
        self.progress.setAccessibleName(translate("progress.accessible"))
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.note = StateNote()
        layout.addWidget(self.note)

        actions = QHBoxLayout()
        self.run_button = QPushButton(translate("export.run"), objectName="exportRun")
        self.run_button.setDefault(True)
        self.run_button.clicked.connect(lambda: self.run_export())
        actions.addWidget(self.run_button)
        self.cancel_button = QPushButton(translate("export.cancel"), objectName="exportCancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_export)
        actions.addWidget(self.cancel_button)
        self.close_button = QPushButton(translate("export.close"), objectName="exportClose")
        self.close_button.clicked.connect(self.reject)
        actions.addWidget(self.close_button)
        layout.addLayout(actions)

    # ---- inputs -------------------------------------------------------

    @property
    def selected_signals(self) -> list[str]:
        return [item.text() for item in self.signal_list.selectedItems()]

    @property
    def scope(self) -> str:
        return str(self.scope_selector.currentData() or SCOPE_ALL)

    @property
    def value_format(self) -> str:
        return str(self.format_selector.currentData() or "csv")

    def set_destination(self, path: Path) -> None:
        self.destination = path
        self.destination_label.setText(path.name)
        self.destination_label.setToolTip(str(path))

    def choose_destination(self) -> None:
        suffix = "parquet" if self.value_format == "parquet" else "csv"
        selected, _ = QFileDialog.getSaveFileName(
            self, translate("export.destination"), f"peaklive-export.{suffix}"
        )
        if selected:
            self.set_destination(Path(selected))

    def resolve_range(self) -> tuple[float | None, float | None]:
        if self.scope == SCOPE_CURSORS:
            if self._cursor_range is None:
                raise ValueError(translate("export.no_cursors"))
            return self._cursor_range
        if self.scope == SCOPE_WINDOW:
            if self._visible_window is None:
                raise ValueError(translate("export.no_range"))
            return self._visible_window
        return None, None

    # ---- execution ----------------------------------------------------

    def run_export(self, blocking: bool = False) -> int:
        """Validate and start the export.

        Interactive runs stream on a worker thread so the dialog stays
        responsive and Cancel can actually reach the row stream. Tests pass
        `blocking=True` to run the same code path inline and read the count.
        """
        names = self.selected_signals
        if not names:
            self.note.show_message(translate("export.no_signal"), "error")
            return -1
        if self.destination is None:
            self.note.show_message(translate("export.no_destination"), "error")
            return -1
        try:
            start, end = self.resolve_range()
        except ValueError as error:
            self.note.show_message(str(error), "error")
            return -1
        # Series caches are maintained by the UI thread.  Materialise the
        # selected range before crossing the thread boundary so the worker can
        # never observe an invalidated cache half-way through an acquisition.
        rows = tuple(export_rows(self._store, names, start, end))
        worker = ExportWorker(self.destination, rows, self.value_format, self)
        self._worker = worker
        worker.progress.connect(self._show_progress)
        worker.export_finished.connect(self._finished)
        worker.export_failed.connect(self._failed)
        worker.export_cancelled.connect(self._cancelled)
        self._set_running(True)
        if not blocking:
            worker.finished.connect(self._worker_done)
            worker.start()
            return 0
        written = worker.execute()
        self._worker_done()
        return written

    def _set_running(self, running: bool) -> None:
        self.progress.setVisible(running)
        self.run_button.setEnabled(not running)
        self.cancel_button.setEnabled(running)
        if running:
            self.note.clear_message()

    def _worker_done(self) -> None:
        self._set_running(False)
        self._worker = None

    def cancel_export(self) -> None:
        if self._worker is not None:
            self._worker.request_stop()

    def _show_progress(self, written: int) -> None:
        self.written = written
        self.note.show_message(translate("export.running").format(written=written), "info")

    def _finished(self, written: int) -> None:
        self.written = written
        destination = self.destination
        name = destination.name if destination is not None else ""
        if written == 0:
            self.note.show_message(translate("export.no_range"), "warning")
            return
        self.note.show_message(
            translate("export.done").format(written=written, name=name), "info"
        )

    def _failed(self, message: str) -> None:
        self.note.show_message(translate("export.failed").format(message=message), "error")

    def _cancelled(self) -> None:
        self.note.show_message(translate("export.cancelled"), "warning")

    def keyPressEvent(self, event) -> None:  # type: ignore[no-untyped-def]  # noqa: N802
        # Escape must close the dialog, never silently discard a running export.
        if event.key() == Qt.Key.Key_Escape and self._worker is not None:
            self.cancel_export()
            return
        super().keyPressEvent(event)
