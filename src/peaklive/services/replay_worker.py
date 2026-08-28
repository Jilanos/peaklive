"""Background replay of large traces without loading the capture into memory."""

from __future__ import annotations

from collections import Counter
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
    # done/total are source bytes, allowing truthful monotonic progress without
    # preloading or counting records.
    progressed = Signal(int, int)

    def __init__(self, path: Path) -> None:
        super().__init__()
        self._path = path
        self._stop_requested = Event()
        self._last_progress = 0

    def request_stop(self) -> None:
        self._stop_requested.set()

    def run(self) -> None:
        batch: list[CanFrame] = []
        anomalies: Counter[str] = Counter()
        try:
            total = self._path.stat().st_size
            for record in iter_trace(self._path):
                if self._stop_requested.is_set():
                    break
                if isinstance(record, BusEvent):
                    if record.kind == "replay_anomaly":
                        anomalies[record.message] += 1
                    else:
                        self.event_received.emit(record)
                    continue
                batch.append(record)
                if len(batch) >= 512:
                    self.frames_received.emit(batch)
                    batch = []
                self._emit_progress(total)
            if batch:
                self.frames_received.emit(batch)
            for message, count in anomalies.items():
                suffix = f" ({count} occurrences)" if count > 1 else ""
                self.event_received.emit(BusEvent(0.0, "replay_anomaly", message + suffix))
            self.progressed.emit(total, total)
        except OSError as error:
            self.replay_failed.emit(str(error))

    def _emit_progress(self, total: int) -> None:
        if total <= 0:
            return
        try:
            done = self._path.stat().st_size
        except OSError:
            return
        # The iterator is streaming; file size is available as a coarse but
        # monotonic completion signal and avoids a callback per source line.
        if done > self._last_progress:
            self._last_progress = done
            self.progressed.emit(min(done, total), total)
