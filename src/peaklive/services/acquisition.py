"""Coordinates adapter lifecycle and complete recording before presentation."""

from __future__ import annotations

from collections.abc import Iterable

from peaklive.adapters.base import CanAdapter
from peaklive.domain import BusEvent, CanFrame, MeasurementProfile
from peaklive.recording import AscRecorder


class AcquisitionSession:
    def __init__(self, adapter: CanAdapter, recorder: AscRecorder) -> None:
        self._adapter = adapter
        self._recorder = recorder
        self.profile: MeasurementProfile | None = None

    def start(self, profile: MeasurementProfile) -> BusEvent:
        self.profile = profile
        event = self._adapter.connect(profile)
        if profile.recording.enabled:
            self._recorder.start(profile.recording, profile.name)
            self._recorder.write_event(event)
        return event

    def ingest(self, frames: Iterable[CanFrame]) -> list[CanFrame]:
        captured = list(frames)
        if self._recorder.active:
            for frame in captured:
                self._recorder.write_frame(frame)
        return captured

    def stop(self) -> BusEvent:
        event = self._adapter.disconnect()
        if self._recorder.active:
            self._recorder.write_event(event)
            self._recorder.stop()
        return event
