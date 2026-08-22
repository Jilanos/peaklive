"""A deterministic adapter for UI and domain testing without a physical bus."""

from __future__ import annotations

from collections.abc import Iterator
from itertools import count
from time import monotonic

from peaklive.domain import BusEvent, CanFrame, MeasurementProfile


class FakeCanAdapter:
    def __init__(self) -> None:
        self._connected = False
        self._profile: MeasurementProfile | None = None
        self._sequence = count()

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(self, profile: MeasurementProfile) -> BusEvent:
        self._profile = profile
        self._connected = True
        return BusEvent(
            monotonic(),
            "connected",
            f"Connected at {profile.bitrate} bit/s",
            profile.channel,
        )

    def disconnect(self) -> BusEvent:
        channel = self._profile.channel if self._profile else "channel-1"
        self._connected = False
        return BusEvent(monotonic(), "disconnected", "Disconnected", channel)

    def frames(self) -> Iterator[CanFrame]:
        if not self._connected:
            return
        for _ in range(32):
            sequence = next(self._sequence)
            yield CanFrame(
                timestamp=monotonic(),
                arbitration_id=0x120 + sequence % 16,
                data=sequence.to_bytes(8, "little"),
                channel=self._profile.channel if self._profile else "channel-1",
            )
