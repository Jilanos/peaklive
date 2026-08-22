"""Background replay of large traces without loading the capture into memory."""

from __future__ import annotations

from pathlib import Path
from threading import Event

from PySide6.QtCore import QThread, Signal

from peaklive.analysis import iter_trace
from peaklive.domain import BusEvent, CanFrame


class ReplayWorker(QThread):
    """Read ASC/TRC records incrementally and batch presentation notifications."""

    frames_received = Signal(list)
    event_received = Signal(object)
    replay_failed = Signal(str)

    def __init__(self, path: Path) -> None:
        super().__init__()
        self._path = path
        self._stop_requested = Event()

    def request_stop(self) -> None:
        self._stop_requested.set()

    def run(self) -> None:
        batch: list[CanFrame] = []
        try:
            for record in iter_trace(self._path):
                if self._stop_requested.is_set():
                    break
                if isinstance(record, BusEvent):
                    self.event_received.emit(record)
                    continue
                batch.append(record)
                if len(batch) >= 512:
                    self.frames_received.emit(batch)
                    batch = []
            if batch:
                self.frames_received.emit(batch)
        except OSError as error:
            self.replay_failed.emit(str(error))
