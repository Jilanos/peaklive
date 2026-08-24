"""Vendor-neutral adapter port. Concrete hardware remains outside the UI."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol

from peaklive.domain import BusEvent, CanFrame, MeasurementProfile


class CanAdapter(Protocol):
    """Owns one driver lifecycle and emits normalized domain events."""

    @property
    def connected(self) -> bool: ...

    def connect(self, profile: MeasurementProfile) -> BusEvent: ...

    def disconnect(self) -> BusEvent: ...

    def receive(self, timeout: float) -> CanFrame | BusEvent | None: ...

    def frames(self) -> Iterator[CanFrame]: ...
