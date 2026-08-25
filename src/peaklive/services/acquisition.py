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

    def stop(self) -> BusEvent:
        event = self._adapter.disconnect()
        if self._recorder.active:
            self._recorder.write_event(event)
            self._recorder.stop()
        return event
