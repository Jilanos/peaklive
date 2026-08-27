"""Coordinates adapter lifecycle and complete recording before presentation."""

from __future__ import annotations

from collections.abc import Iterable

from peaklive.adapters.base import CanAdapter
from peaklive.domain import BusEvent, CanFrame, MeasurementProfile
from peaklive.recording import AscRecorder, RecordingStopped


class AcquisitionSession:
    def __init__(self, adapter: CanAdapter, recorder: AscRecorder) -> None:
        self._adapter = adapter
        self._recorder = recorder
        self._notices: list[BusEvent] = []
        self.profile: MeasurementProfile | None = None

    def start(self, profile: MeasurementProfile) -> BusEvent:
        self.profile = profile
        event = self._adapter.connect(profile)
        if profile.recording.enabled:
            self._recorder.start(profile.recording, profile.name)
            self._recorder.write_event(event)
        return event

    def ingest(self, frames: Iterable[CanFrame]) -> list[CanFrame]:
        """Record every frame, then hand the batch on unchanged.

        A recording that stops on a disk threshold must not stop the
        acquisition: the frames keep flowing receive-only and the operator gets
        a notice instead of a dead session.
        """
        captured = list(frames)
        if self._recorder.active:
            for index, frame in enumerate(captured):
                try:
                    self._recorder.write_frame(frame)
                except RecordingStopped as error:
                    self._note(captured[index].timestamp, "recording_warning", str(error))
                    break
            self._drain_recorder_warnings(captured)
            self._recorder.flush()
        return captured

    def take_notices(self) -> list[BusEvent]:
        """Drain the recording notices raised since the last call."""
        drained = list(self._notices)
        self._notices.clear()
        return drained

    def _drain_recorder_warnings(self, captured: list[CanFrame]) -> None:
        timestamp = captured[-1].timestamp if captured else 0.0
        for message in self._recorder.take_warnings():
            self._note(timestamp, "recording_warning", message)

    def _note(self, timestamp: float, kind: str, message: str) -> None:
        self._notices.append(BusEvent(timestamp, kind, message))

    def record_event(self, event: BusEvent) -> BusEvent:
        if self._recorder.active:
            self._recorder.write_event(event)
        return event

    def stop(self, clean: bool = True) -> BusEvent:
        """Close the driver and finalize the recording exactly once.

        The recorder is finalized even when the driver disconnect raises, so a
        failing adapter cannot also cost the operator the capture. A disconnect
        failure marks the capture incomplete and is re-raised for the caller to
        surface; the partial segments stay on disk as recoverable evidence.
        """
        try:
            event = self._adapter.disconnect()
        except Exception as error:
            self._finalize(
                BusEvent(0.0, "disconnect_failed", f"Disconnect failed: {error}"),
                clean=False,
            )
            raise
        self._finalize(event, clean=clean)
        return event

    def _finalize(self, event: BusEvent, clean: bool) -> None:
        if not self._recorder.active:
            return
        try:
            self._recorder.write_event(event)
        except RecordingStopped:
            # The writer already closed itself on an integrity condition; the
            # capture is finalized below either way.
            pass
        self._recorder.stop(clean=clean)
