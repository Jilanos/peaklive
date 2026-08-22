"""Windows Classic USB adapter backed by python-can's PCAN interface."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from time import monotonic
from typing import Any

from peaklive.domain import BusEvent, CanFrame, ControllerMode, MeasurementProfile

COMMON_BITRATES = frozenset({125_000, 250_000, 500_000, 1_000_000})


class PcanAdapter:
    """Owns one PCAN driver handle and normalizes it into domain events.

    The `bus_factory` seam keeps all unit tests independent from Windows and
    allows a future hardware-in-loop fixture to exercise the exact lifecycle.
    """

    def __init__(self, bus_factory: Callable[..., Any] | None = None) -> None:
        self._bus_factory = bus_factory
        self._bus: Any | None = None
        self._profile: MeasurementProfile | None = None

    @property
    def connected(self) -> bool:
        return self._bus is not None

    @staticmethod
    def supported_bitrates() -> tuple[int, ...]:
        return tuple(sorted(COMMON_BITRATES))

    def connect(self, profile: MeasurementProfile) -> BusEvent:
        if profile.bitrate not in COMMON_BITRATES:
            raise ValueError(f"Unsupported initial bitrate: {profile.bitrate}")
        if self.connected:
            self.disconnect()
        can = self._can_module()
        state = (
            can.BusState.PASSIVE
            if profile.controller_mode is ControllerMode.PASSIVE_LISTEN_ONLY
            else can.BusState.ACTIVE
        )
        factory = self._bus_factory or can.Bus
        self._bus = factory(
            interface="pcan",
            channel=self._driver_channel(profile.channel),
            bitrate=profile.bitrate,
            state=state,
            receive_own_messages=False,
        )
        self._profile = profile
        mode = "passive listen-only" if state is can.BusState.PASSIVE else "normal receive"
        return BusEvent(monotonic(), "connected", f"Connected: {mode}", profile.channel)

    def disconnect(self) -> BusEvent:
        channel = self._profile.channel if self._profile else "channel-1"
        if self._bus is not None:
            self._bus.shutdown()
        self._bus = None
        self._profile = None
        return BusEvent(monotonic(), "disconnected", "Disconnected", channel)

    def frames(self) -> Iterator[CanFrame]:
        if self._bus is None:
            return
        while self._bus is not None:
            message = self._bus.recv(timeout=0.25)
            if message is None:
                continue
            yield CanFrame(
                timestamp=float(message.timestamp),
                arbitration_id=int(message.arbitration_id),
                data=bytes(message.data),
                channel=self._profile.channel if self._profile else "channel-1",
                is_extended_id=bool(message.is_extended_id),
                is_remote_frame=bool(message.is_remote_frame),
            )

    @staticmethod
    def _can_module() -> Any:
        try:
            import can
        except ImportError as error:  # pragma: no cover - packaging guard
            raise RuntimeError("python-can is required for live CAN acquisition") from error
        return can

    @staticmethod
    def _driver_channel(channel: str) -> str:
        return "PCAN_USBBUS1" if channel == "channel-1" else channel
