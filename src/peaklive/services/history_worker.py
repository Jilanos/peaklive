"""Cancellable source-backed historical viewport reads."""
from __future__ import annotations

from pathlib import Path
from threading import Event

from PySide6.QtCore import QThread, Signal

from peaklive.analysis.history import HistoricalSignalStore, historical_points
from peaklive.diagnostics import logger


class HistoryViewportWorker(QThread):
    """Read one immutable viewport snapshot away from the Qt GUI thread."""

    completed = Signal(object, int)
    failed = Signal(str, int)

    def __init__(self, path: Path, signals: tuple[str, ...], extent, visible, generation: int):
        super().__init__()
        self._path = path
        self._signals = signals
        self._extent = extent
        self._visible = visible
        self._generation = generation
        self._cancel = Event()

    def request_cancel(self) -> None:
        self._cancel.set()

    def run(self) -> None:
        if self._cancel.is_set():
            return
        result = {}
        try:
            with HistoricalSignalStore(self._path, read_only=True) as history:
                for signal in self._signals:
                    if self._cancel.is_set():
                        return
                    result[signal] = historical_points(
                        history, signal, self._extent, self._visible
                    )
        except Exception as error:
            if not self._cancel.is_set():
                logger().exception("historical viewport read failed: %s", error)
                self.failed.emit(str(error), self._generation)
            return
        if not self._cancel.is_set():
            self.completed.emit(result, self._generation)
