"""Qt acquisition worker that keeps hardware I/O and durable recording off the UI thread."""

from __future__ import annotations

from collections.abc import Callable
from threading import Event

from PySide6.QtCore import QThread, Signal

from peaklive.adapters.base import CanAdapter
from peaklive.domain import BusEvent, CanFrame, MeasurementProfile
from peaklive.recording import AscRecorder
from peaklive.services.acquisition import AcquisitionSession
from peaklive.services.lifecycle import AcquisitionPhase


class AcquisitionWorker(QThread):
    """Poll a single adapter, recording frames before notifying the presentation layer.

    The worker narrates its own lifecycle through `phase_changed` and carries a
    `generation` so the shell can recognise — and discard — signals from a run
    it has already abandoned. Connect, receive, disconnect, and recorder
    finalization all happen here, never on the UI thread.
    """

    frames_received = Signal(list)
    status_changed = Signal(str)
    event_received = Signal(object)
    acquisition_failed = Signal(str)
    phase_changed = Signal(str)

    def __init__(
        self,
        adapter: CanAdapter,
        profile: MeasurementProfile,
        generation: int = 0,
        presentation_sink: Callable[[int, list[CanFrame]], None] | None = None,
    ) -> None:
        super().__init__()
        self._adapter = adapter
        self._profile = profile
        self._generation = generation
        self._presentation_sink = presentation_sink
        self._stop_requested = Event()

    @property
    def generation(self) -> int:
        return self._generation

    @property
    def stop_requested(self) -> bool:
        return self._stop_requested.is_set()

    def request_stop(self) -> None:
        """Ask the run loop to wind down. Safe to call repeatedly."""
        self._stop_requested.set()

    def run(self) -> None:
        session = AcquisitionSession(self._adapter, AscRecorder())
        started = False
        failure: str | None = None
        batch: list[CanFrame] = []
        self.phase_changed.emit(AcquisitionPhase.STARTING)
        try:
            event = session.start(self._profile)
            started = True
            self.status_changed.emit(event.message)
            self.phase_changed.emit(AcquisitionPhase.RUNNING)
            while not self._stop_requested.is_set():
                record = self._adapter.receive(timeout=0.1)
                if record is None:
                    if batch:
                        self._flush(session, batch)
                        batch = []
                    continue
                if isinstance(record, BusEvent):
                    session.record_event(record)
                    self.event_received.emit(record)
                    self.status_changed.emit(record.message)
                    continue
                batch.append(record)
                if len(batch) >= 64:
                    self._flush(session, batch)
                    batch = []
        except Exception as error:
            failure = str(error)
            self.acquisition_failed.emit(failure)
        finally:
            failure = self._shut_down(session, batch, started, failure)
            self.phase_changed.emit(
                AcquisitionPhase.FAILED if failure else AcquisitionPhase.STOPPED
            )

    def _shut_down(
        self,
        session: AcquisitionSession,
        batch: list[CanFrame],
        started: bool,
        failure: str | None,
    ) -> str | None:
        """Drain, disconnect, and finalize, reporting the first failure seen.

        Every step is isolated: a recording error must not skip the disconnect,
        and a disconnect error must not skip finalization, because either one
        leaving work undone is what strands the operator.
        """
        if not started:
            return failure
        self.phase_changed.emit(AcquisitionPhase.FINALIZING)
        if batch:
            try:
                self._flush(session, batch)
            except Exception as error:
                failure = failure or str(error)
                self.acquisition_failed.emit(str(error))
        try:
            event = session.stop(clean=failure is None)
            self.status_changed.emit(event.message)
        except Exception as error:
            failure = failure or str(error)
            self.acquisition_failed.emit(str(error))
        return failure

    def _flush(self, session: AcquisitionSession, batch: list[CanFrame]) -> None:
        """Emit one batch, then surface any recording notice it produced."""
        captured = session.ingest(batch)
        if self._presentation_sink is None:
            self.frames_received.emit(captured)
        else:
            # The sink is deliberately a lock-protected, non-Qt callback.  A
            # queued Qt signal per batch can otherwise leave hundreds of
            # render events ahead of Stop on a busy bus.
            self._presentation_sink(self._generation, captured)
        for notice in session.take_notices():
            self.event_received.emit(notice)
            self.status_changed.emit(notice.message)
