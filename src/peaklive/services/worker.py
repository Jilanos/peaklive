"""Qt acquisition worker that keeps hardware I/O and durable recording off the UI thread."""

from __future__ import annotations

from collections.abc import Callable
from threading import Event
from time import monotonic

from PySide6.QtCore import QThread, Signal

from peaklive.adapters.base import CanAdapter
from peaklive.domain import BusEvent, CanFrame, MeasurementProfile
from peaklive.recording import AscRecorder
from peaklive.services.acquisition import AcquisitionSession
from peaklive.services.lifecycle import AcquisitionPhase

#: Kinds that represent a bus or driver problem rather than routine status.
ERROR_EVENT_KINDS = frozenset(
    {
        "error_frame",
        "bus_error",
        "bus_off",
        "bus_passive",
        "bus_warning",
        "driver_overrun",
        "driver_error",
    }
)

#: An identical error closer together than this is dropped rather than
#: flooding the UI signal queue and the event recording.
ERROR_EVENT_MIN_INTERVAL_S = 1.0

#: Backoff applied to `receive()` per consecutive error, capped so a driver
#: that returns errors instead of blocking cannot spin the poll loop hot.
ERROR_BACKOFF_STEP_MS = 50
MAX_ERROR_BACKOFF_MS = 1000

#: An error storm this long triggers an automatic, bounded reconnect instead
#: of polling a driver indefinitely that is not going to recover on its own.
ERRORS_BEFORE_RECONNECT = 20
MAX_RECONNECT_ATTEMPTS = 3
RECONNECT_BACKOFF_MS = 1000


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
    recording_reserved = Signal(int)

    def __init__(
        self,
        adapter: CanAdapter,
        profile: MeasurementProfile,
        generation: int = 0,
        presentation_sink: Callable[[int, list[CanFrame]], None] | None = None,
        recorder_factory: Callable[[], AscRecorder] | None = None,
    ) -> None:
        super().__init__()
        self._adapter = adapter
        self._profile = profile
        self._generation = generation
        self._presentation_sink = presentation_sink
        # Resolve the default at construction time so tests and deployments
        # can inject format-specific writers without patching worker logic.
        self._recorder_factory = recorder_factory or AscRecorder
        self._stop_requested = Event()
        self._consecutive_errors = 0
        self._last_error_signature: tuple[str, str] | None = None
        self._last_error_emitted_at = 0.0

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
        session = AcquisitionSession(self._adapter, self._recorder_factory())
        failure: str | None = None
        batch: list[CanFrame] = []
        self.phase_changed.emit(AcquisitionPhase.STARTING)
        try:
            event = session.start(self._profile, stop_requested=self._stop_requested.is_set)
            if self._profile.recording.enabled:
                # The reservation advanced the iteration on this worker's own
                # profile snapshot; the shell owns applying that count to the
                # shared profile and persisting it through its normal save path.
                self.recording_reserved.emit(self._profile.recording.iteration)
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
                    self._handle_event(session, record)
                    continue
                self._consecutive_errors = 0
                batch.append(record)
                if len(batch) >= 64:
                    self._flush(session, batch)
                    batch = []
                    # A saturated adapter can otherwise retain Python's GIL
                    # across an unbroken series of batches.  Give the GUI a
                    # scheduling opportunity after each durable write and
                    # visual hand-off so Stop and timers remain responsive.
                    self.msleep(1)
        except Exception as error:
            failure = str(error)
            self.acquisition_failed.emit(failure)
        finally:
            failure = self._shut_down(session, batch, failure)
            self.phase_changed.emit(
                AcquisitionPhase.FAILED if failure else AcquisitionPhase.STOPPED
            )

    def _shut_down(
        self,
        session: AcquisitionSession,
        batch: list[CanFrame],
        failure: str | None,
    ) -> str | None:
        """Drain, disconnect, and finalize, reporting the first failure seen.

        Every step is isolated: a recording error must not skip the disconnect,
        and a disconnect error must not skip finalization, because either one
        leaving work undone is what strands the operator. The adapter is
        recorded as connected the moment `connect()` returns, before recording
        reservation or the recorder can fail, so a failure anywhere after
        connect still reaches disconnect here instead of leaking the handle.
        """
        if not session.connected:
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

    def _handle_event(self, session: AcquisitionSession, record: BusEvent) -> None:
        """Surface one adapter event, rate-limiting and backing off persistent errors.

        A non-error event (connected, disconnected, a recording notice, ...)
        always reaches the recording and the UI unchanged. An error event is
        deduplicated so an unblinking fault does not flood the event
        recording or the UI signal queue, and each one costs a small,
        growing sleep so a driver returning errors instead of blocking cannot
        spin this loop hot. A long enough error storm triggers a bounded,
        alerted reconnect.
        """
        if record.kind not in ERROR_EVENT_KINDS:
            self._consecutive_errors = 0
            self._emit_event(session, record)
            return
        self._consecutive_errors += 1
        if not self._event_rate_limited(record):
            self._emit_event(session, record)
        self.msleep(min(ERROR_BACKOFF_STEP_MS * self._consecutive_errors, MAX_ERROR_BACKOFF_MS))
        if self._consecutive_errors >= ERRORS_BEFORE_RECONNECT:
            self._consecutive_errors = 0
            self._reconnect_or_raise(session)

    def _event_rate_limited(self, record: BusEvent) -> bool:
        now = monotonic()
        signature = (record.kind, record.message)
        if (
            signature == self._last_error_signature
            and now - self._last_error_emitted_at < ERROR_EVENT_MIN_INTERVAL_S
        ):
            return True
        self._last_error_signature = signature
        self._last_error_emitted_at = now
        return False

    def _emit_event(self, session: AcquisitionSession, record: BusEvent) -> None:
        session.record_event(record)
        self.event_received.emit(record)
        self.status_changed.emit(record.message)

    def _reconnect_or_raise(self, session: AcquisitionSession) -> None:
        """Cycle the adapter up to `MAX_RECONNECT_ATTEMPTS` times, alerting on each.

        A caller that gives up all attempts raises rather than continuing to
        poll a driver that will not recover; the caller's existing failure
        handling turns that into a restartable, alerted failed state.
        """
        last_error: Exception | None = None
        for attempt in range(1, MAX_RECONNECT_ATTEMPTS + 1):
            if self._stop_requested.is_set():
                return
            notice = BusEvent(
                monotonic(),
                "reconnecting",
                f"Reconnecting (attempt {attempt} of {MAX_RECONNECT_ATTEMPTS}) "
                "after a persistent adapter error...",
                self._profile.channel,
            )
            self.event_received.emit(notice)
            self.status_changed.emit(notice.message)
            self.msleep(RECONNECT_BACKOFF_MS)
            if self._stop_requested.is_set():
                return
            try:
                event = session.reconnect(self._profile)
            except Exception as error:
                last_error = error
                continue
            self.event_received.emit(event)
            self.status_changed.emit(event.message)
            return
        raise RuntimeError(
            f"Adapter unavailable after {MAX_RECONNECT_ATTEMPTS} reconnect attempts: {last_error}"
        )
