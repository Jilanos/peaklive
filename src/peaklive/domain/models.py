"""Immutable CAN events and serializable measurement profile data."""

from __future__ import annotations

from copy import deepcopy
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


#: The template a profile created from now on starts with. Stored templates
#: are never rewritten to it: an operator who tuned a filename keeps it.
DEFAULT_FILENAME_TEMPLATE = "{date}_{time}_{profile}_{text}_{iteration:03d}_{segment:03d}.asc"


@dataclass(slots=True)
class RecordingSettings:
    enabled: bool = True
    directory: str = ""
    filename_template: str = DEFAULT_FILENAME_TEMPLATE
    capture_format: str = "asc"
    #: Free operator label placed in the filename by the ``{text}`` placeholder.
    text: str = ""
    iteration: int = 1
    rotate_bytes: int = 2 * 1024**3
    warn_free_bytes: int = 10 * 1024**3
    stop_free_bytes: int = 2 * 1024**3

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "directory": self.directory,
            "filename_template": self.filename_template,
            "capture_format": self.capture_format,
            "text": self.text,
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
            capture_format=(
                str(raw.get("capture_format", "asc")).lower()
                if str(raw.get("capture_format", "asc")).lower() in {"asc", "trc"}
                else "asc"
            ),
            text=str(raw.get("text", "")),
            iteration=max(1, int(raw.get("iteration", 1))),
            rotate_bytes=max(1, int(raw.get("rotate_bytes", cls().rotate_bytes))),
            warn_free_bytes=max(1, int(raw.get("warn_free_bytes", cls().warn_free_bytes))),
            stop_free_bytes=max(1, int(raw.get("stop_free_bytes", cls().stop_free_bytes))),
        )


TRACE_DIRECTION_ANY = "any"
TRACE_DECODE_ANY = "any"


@dataclass(slots=True)
class TraceFilterSettings:
    """Display-only trace filtering, never applied to recorded data."""

    arbitration_id: str = ""
    message: str = ""
    signal: str = ""
    direction: str = TRACE_DIRECTION_ANY
    event_kind: str = ""
    decode_status: str = TRACE_DECODE_ANY
    time_start: float | None = None
    time_end: float | None = None
    show_frames: bool = True
    show_events: bool = True

    def is_active(self) -> bool:
        return bool(self.active_chips())

    def active_chips(self) -> list[tuple[str, str]]:
        """Return (field, label) pairs for the removable active-filter chips."""
        chips: list[tuple[str, str]] = []
        if self.arbitration_id:
            chips.append(("arbitration_id", f"ID {self.arbitration_id}"))
        if self.message:
            chips.append(("message", f"Message {self.message}"))
        if self.signal:
            chips.append(("signal", f"Signal {self.signal}"))
        if self.direction != TRACE_DIRECTION_ANY:
            chips.append(("direction", f"Direction {self.direction.upper()}"))
        if self.event_kind:
            chips.append(("event_kind", f"Event {self.event_kind}"))
        if self.decode_status != TRACE_DECODE_ANY:
            chips.append(("decode_status", f"Decode {self.decode_status}"))
        if self.time_start is not None:
            chips.append(("time_start", f"From {self.time_start:.6f}s"))
        if self.time_end is not None:
            chips.append(("time_end", f"To {self.time_end:.6f}s"))
        if not self.show_frames:
            chips.append(("show_frames", "Events only"))
        if not self.show_events:
            chips.append(("show_events", "Frames only"))
        return chips

    def reset_field(self, field_name: str) -> None:
        defaults = TraceFilterSettings()
        setattr(self, field_name, getattr(defaults, field_name))

    def clear(self) -> None:
        defaults = TraceFilterSettings()
        for field_name in (
            "arbitration_id",
            "message",
            "signal",
            "direction",
            "event_kind",
            "decode_status",
            "time_start",
            "time_end",
            "show_frames",
            "show_events",
        ):
            setattr(self, field_name, getattr(defaults, field_name))

    def to_dict(self) -> dict[str, Any]:
        return {
            "arbitration_id": self.arbitration_id,
            "message": self.message,
            "signal": self.signal,
            "direction": self.direction,
            "event_kind": self.event_kind,
            "decode_status": self.decode_status,
            "time_start": self.time_start,
            "time_end": self.time_end,
            "show_frames": self.show_frames,
            "show_events": self.show_events,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> TraceFilterSettings:
        def optional_float(key: str) -> float | None:
            value = raw.get(key)
            if value in (None, ""):
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        return cls(
            arbitration_id=str(raw.get("arbitration_id", "")),
            message=str(raw.get("message", "")),
            signal=str(raw.get("signal", "")),
            direction=str(raw.get("direction", TRACE_DIRECTION_ANY)),
            event_kind=str(raw.get("event_kind", "")),
            decode_status=str(raw.get("decode_status", TRACE_DECODE_ANY)),
            time_start=optional_float("time_start"),
            time_end=optional_float("time_end"),
            show_frames=bool(raw.get("show_frames", True)),
            show_events=bool(raw.get("show_events", True)),
        )


@dataclass(slots=True)
class TraceColumn:
    """One configurable trace column: visibility, width, and value format."""

    key: str
    visible: bool = True
    width: int = 90
    value_format: str = "text"

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "visible": self.visible,
            "width": self.width,
            "value_format": self.value_format,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> TraceColumn:
        return cls(
            key=str(raw["key"]),
            visible=bool(raw.get("visible", True)),
            width=max(20, int(raw.get("width", 90))),
            value_format=str(raw.get("value_format", "text")),
        )


TRACE_COLUMN_DEFAULTS: tuple[TraceColumn, ...] = (
    TraceColumn("time", value_format="time", width=110),
    TraceColumn("id", value_format="hex", width=80),
    TraceColumn("dlc", value_format="dec", width=50),
    TraceColumn("data", value_format="hex", width=200),
    TraceColumn("channel", width=90),
    TraceColumn("direction", width=70),
    TraceColumn("message", width=150),
    TraceColumn("status", value_format="status", width=90),
)

TRACE_COLUMN_FORMATS: dict[str, tuple[str, ...]] = {
    "time": ("time", "dec"),
    "id": ("hex", "dec"),
    "dlc": ("dec", "hex"),
    "data": ("hex", "dec", "bin"),
    "channel": ("text",),
    "direction": ("text",),
    "message": ("text",),
    "status": ("status", "text"),
}


def default_trace_columns() -> list[TraceColumn]:
    return [TraceColumn(**column.to_dict()) for column in TRACE_COLUMN_DEFAULTS]


@dataclass(slots=True)
class WorkspaceLayout:
    """Persisted workspace geometry, visible configuration, and cursor state."""

    workspace_mode: str = "combo"
    splitter_sizes: list[int] = field(default_factory=list)
    divider_sizes: list[int] = field(default_factory=list)
    collapsed_panels: list[str] = field(default_factory=list)
    #: Remembered expanded width per side panel, so a collapsed panel comes
    #: back to the width the operator gave it rather than to a guess.
    panel_widths: dict[str, int] = field(default_factory=dict)
    cursor_a: float | None = None
    cursor_b: float | None = None
    fullscreen: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_mode": self.workspace_mode,
            "splitter_sizes": list(self.splitter_sizes),
            "divider_sizes": list(self.divider_sizes),
            "collapsed_panels": list(self.collapsed_panels),
            "panel_widths": dict(self.panel_widths),
            "cursor_a": self.cursor_a,
            "cursor_b": self.cursor_b,
            "fullscreen": self.fullscreen,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> WorkspaceLayout:
        def optional_float(key: str) -> float | None:
            value = raw.get(key)
            if value in (None, ""):
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        def widths(key: str) -> dict[str, int]:
            """Drop any stored width that is missing, unusable, or not a size."""
            raw_widths = raw.get(key, {})
            if not isinstance(raw_widths, dict):
                return {}
            usable: dict[str, int] = {}
            for name, value in raw_widths.items():
                try:
                    width = int(value)
                except (TypeError, ValueError):
                    continue
                if width > 0:
                    usable[str(name)] = width
            return usable

        def sizes(key: str) -> list[int]:
            try:
                return [int(item) for item in raw.get(key, [])]
            except (TypeError, ValueError):
                return []

        return cls(
            workspace_mode=str(raw.get("workspace_mode", "combo")),
            splitter_sizes=sizes("splitter_sizes"),
            divider_sizes=sizes("divider_sizes"),
            collapsed_panels=[str(name) for name in raw.get("collapsed_panels", [])],
            panel_widths=widths("panel_widths"),
            cursor_a=optional_float("cursor_a"),
            cursor_b=optional_float("cursor_b"),
            fullscreen=bool(raw.get("fullscreen", False)),
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
    trace_filter: TraceFilterSettings = field(default_factory=TraceFilterSettings)
    trace_columns: list[TraceColumn] = field(default_factory=default_trace_columns)
    layout: WorkspaceLayout = field(default_factory=WorkspaceLayout)
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
            "trace_filter": self.trace_filter.to_dict(),
            "trace_columns": [column.to_dict() for column in self.trace_columns],
            "layout": self.layout.to_dict(),
            "recording": self.recording.to_dict(),
            "updated_at": self.updated_at,
        }

    def duplicate(self, name: str) -> MeasurementProfile:
        """Return an independent copy of the persisted configuration.

        The copy is rebuilt from the serialized form, so every nested
        structure — DBC paths and their choices, signal lists, trace columns,
        layout, recording settings — is a new object. Nothing that belongs to
        a running session (acquired frames, events, reservations, capture
        files) lives in this dataclass, so nothing of the sort can be copied.
        """
        raw = deepcopy(self.to_dict())
        copy = MeasurementProfile.from_dict(raw)
        copy.identifier = str(uuid4())
        copy.name = name
        copy.updated_at = datetime.now().astimezone().isoformat()
        return copy

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
            trace_filter=TraceFilterSettings.from_dict(dict(raw.get("trace_filter", {}))),
            trace_columns=_columns_from_raw(raw.get("trace_columns")),
            layout=_layout_from_raw(raw),
            recording=RecordingSettings.from_dict(dict(raw.get("recording", {}))),
            updated_at=str(raw.get("updated_at", datetime.now().astimezone().isoformat())),
        )


def _columns_from_raw(raw: Any) -> list[TraceColumn]:
    """Restore persisted columns, healing an unknown or truncated column set."""
    if not isinstance(raw, list) or not raw:
        return default_trace_columns()
    known = {column.key: column for column in TRACE_COLUMN_DEFAULTS}
    restored: list[TraceColumn] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        default = known.get(str(item.get("key")))
        if default is None:
            continue
        merged = default.to_dict() | {
            key: value for key, value in item.items() if key in default.to_dict()
        }
        restored.append(TraceColumn.from_dict(merged))
    seen = {column.key for column in restored}
    restored.extend(
        TraceColumn(**column.to_dict())
        for column in TRACE_COLUMN_DEFAULTS
        if column.key not in seen
    )
    return restored


def _layout_from_raw(raw: dict[str, Any]) -> WorkspaceLayout:
    """Restore the layout, migrating the legacy workspace mode from trace_filters."""
    stored = dict(raw.get("layout", {}))
    legacy = dict(raw.get("trace_filters", {}))
    if "workspace_mode" not in stored and "workspace_mode" in legacy:
        stored["workspace_mode"] = legacy["workspace_mode"]
    return WorkspaceLayout.from_dict(stored)
