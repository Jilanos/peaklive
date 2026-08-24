"""Qt acquisition worker that keeps hardware I/O and durable recording off the UI thread."""

from __future__ import annotations

from threading import Event

from PySide6.QtCore import QThread, Signal

from peaklive.adapters.base import CanAdapter
from peaklive.domain import BusEvent, CanFrame, MeasurementProfile
from peaklive.recording import AscRecorder
from peaklive.services.acquisition import AcquisitionSession


class AcquisitionWorker(QThread):
    """Poll a single adapter, recording frames before notifying the presentation layer."""

    frames_received = Signal(list)
    status_changed = Signal(str)
    event_received = Signal(object)
    acquisition_failed = Signal(str)

    def __init__(self, adapter: CanAdapter, profile: MeasurementProfile) -> None:
        super().__init__()
        self._adapter = adapter
        self._profile = profile
        self._stop_requested = Event()

    def request_stop(self) -> None:
        self._stop_requested.set()

    def run(self) -> None:
        session = AcquisitionSession(self._adapter, AscRecorder())
        started = False
        batch: list[CanFrame] = []
        try:
            event = session.start(self._profile)
            started = True
            self.status_changed.emit(event.message)
            while not self._stop_requested.is_set():
                record = self._adapter.receive(timeout=0.1)
                if record is None:
                    if batch:
                        self.frames_received.emit(session.ingest(batch))
                        batch = []
                    continue
                if isinstance(record, BusEvent):
                    session.record_event(record)
                    self.event_received.emit(record)
                    self.status_changed.emit(record.message)
                    continue
                batch.append(record)
                if len(batch) >= 64:
                    self.frames_received.emit(session.ingest(batch))
                    batch = []
        except Exception as error:
            self.acquisition_failed.emit(str(error))
        finally:
            if batch:
                self.frames_received.emit(session.ingest(batch))
            if started:
                event = session.stop()
                self.status_changed.emit(event.message)
