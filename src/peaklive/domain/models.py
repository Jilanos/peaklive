"""Immutable CAN events and serializable measurement profile data."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class ControllerMode(StrEnum):
    """Hardware controller semantics presented explicitly to operators."""

    NORMAL_RECEIVE = "normal_receive"
    PASSIVE_LISTEN_ONLY = "passive_listen_only"


@dataclass(frozen=True, slots=True)
class CanFrame:
    """A normalized raw CAN frame independent of a specific vendor driver."""

    timestamp: float
    arbitration_id: int
    data: bytes
    channel: str = "channel-1"
    is_extended_id: bool = False
    is_remote_frame: bool = False

    @property
    def dlc(self) -> int:
        return len(self.data)


@dataclass(frozen=True, slots=True)
class BusEvent:
    """A visible acquisition state or error event."""

    timestamp: float
    kind: str
    message: str
    channel: str = "channel-1"


@dataclass(slots=True)
class RecordingSettings:
    enabled: bool = True
    directory: str = ""
    filename_template: str = "{date}_{time}_{profile}_{iteration:03d}_{segment:03d}.asc"
    iteration: int = 1
    rotate_bytes: int = 2 * 1024**3
    warn_free_bytes: int = 10 * 1024**3
    stop_free_bytes: int = 2 * 1024**3

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "directory": self.directory,
            "filename_template": self.filename_template,
            "iteration": self.iteration,
            "rotate_bytes": self.rotate_bytes,
            "warn_free_bytes": self.warn_free_bytes,
            "stop_free_bytes": self.stop_free_bytes,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> RecordingSettings:
        return cls(
            enabled=bool(raw.get("enabled", True)),
            directory=str(raw.get("directory", "")),
            filename_template=str(raw.get("filename_template", cls().filename_template)),
            iteration=max(1, int(raw.get("iteration", 1))),
            rotate_bytes=max(1, int(raw.get("rotate_bytes", cls().rotate_bytes))),
            warn_free_bytes=max(1, int(raw.get("warn_free_bytes", cls().warn_free_bytes))),
            stop_free_bytes=max(1, int(raw.get("stop_free_bytes", cls().stop_free_bytes))),
        )


@dataclass(slots=True)
class MeasurementProfile:
    """A named, local-only acquisition and presentation configuration."""

    name: str
    identifier: str = field(default_factory=lambda: str(uuid4()))
    channel: str = "channel-1"
    bitrate: int = 500_000
    controller_mode: ControllerMode = ControllerMode.PASSIVE_LISTEN_ONLY
    dbc_paths: list[str] = field(default_factory=list)
    favorite_signals: list[str] = field(default_factory=list)
    displayed_signals: list[str] = field(default_factory=list)
    trace_filters: dict[str, Any] = field(default_factory=dict)
    recording: RecordingSettings = field(default_factory=RecordingSettings)
    updated_at: str = field(default_factory=lambda: datetime.now().astimezone().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "identifier": self.identifier,
            "name": self.name,
            "channel": self.channel,
            "bitrate": self.bitrate,
            "controller_mode": self.controller_mode.value,
            "dbc_paths": self.dbc_paths,
            "favorite_signals": self.favorite_signals,
            "displayed_signals": self.displayed_signals,
            "trace_filters": self.trace_filters,
            "recording": self.recording.to_dict(),
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> MeasurementProfile:
        mode = ControllerMode(raw.get("controller_mode", ControllerMode.PASSIVE_LISTEN_ONLY.value))
        return cls(
            identifier=str(raw.get("identifier") or uuid4()),
            name=str(raw.get("name", "Default measurement")),
            channel=str(raw.get("channel", "channel-1")),
            bitrate=int(raw.get("bitrate", 500_000)),
            controller_mode=mode,
            dbc_paths=[str(path) for path in raw.get("dbc_paths", [])],
            favorite_signals=[str(signal) for signal in raw.get("favorite_signals", [])],
            displayed_signals=[str(signal) for signal in raw.get("displayed_signals", [])],
            trace_filters=dict(raw.get("trace_filters", {})),
            recording=RecordingSettings.from_dict(dict(raw.get("recording", {}))),
            updated_at=str(raw.get("updated_at", datetime.now().astimezone().isoformat())),
        )
