"""Off-thread streamed export with progress and cancellation."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from peaklive.analysis import ExportRow, export_csv, export_parquet

PROGRESS_STEP = 500


class ExportCancelled(RuntimeError):
    """Raised inside the row stream when the operator cancels the export."""


class ExportWorker(QThread):
    """Streams rows into CSV or Parquet, reporting progress and honouring stop.

    A cancelled export deletes its partial file: a half-written export must
    never be left behind looking like a complete one.
    """

    progress = Signal(int)
    export_finished = Signal(int)
    export_failed = Signal(str)
    export_cancelled = Signal()

    def __init__(
        self,
        path: Path,
        rows: Iterable[ExportRow],
        value_format: str = "csv",
        parent: object | None = None,
    ) -> None:
        super().__init__(parent)
        self._path = path
        self._rows = rows
        self._format = value_format
        self._stop = False
        self.written = 0

    def request_stop(self) -> None:
        self._stop = True

    def run(self) -> None:  # pragma: no cover - exercised through execute()
        self.execute()

    def execute(self) -> int:
        """Run the export inline; returns the written row count, -1 if cancelled."""
        writer = export_parquet if self._format == "parquet" else export_csv
        try:
            self.written = writer(self._path, self._counted(self._rows))
        except ExportCancelled:
            self._discard_partial()
            self.export_cancelled.emit()
            return -1
        except (OSError, ValueError, TypeError) as error:
            self._discard_partial()
            self.export_failed.emit(str(error))
            return -1
        self.export_finished.emit(self.written)
        return self.written

    def _counted(self, rows: Iterable[ExportRow]) -> Iterator[ExportRow]:
        count = 0
        for row in rows:
            if self._stop:
                raise ExportCancelled
            count += 1
            if count % PROGRESS_STEP == 0:
                self.progress.emit(count)
            yield row
        self.progress.emit(count)

    def _discard_partial(self) -> None:
        try:
            self._path.unlink(missing_ok=True)
        except OSError:
            # A file we cannot remove is reported by the caller's error message.
            pass
