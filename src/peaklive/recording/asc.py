"""Recoverable ASC recording with a JSONL sidecar for acquisition events."""

from __future__ import annotations

import json
import re
import shutil
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TextIO

from peaklive.domain import BusEvent, CanFrame, RecordingSettings
from peaklive.recording.naming import RecordingNaming, Reservation

# Probe free space once per batch rather than once per received frame.  The
# same threshold semantics apply, while slow removable/network volumes cannot
# put storage latency on every acquisition iteration.
SPACE_CHECK_INTERVAL_FRAMES = 128


class RecordingStopped(RuntimeError):
    """Raised when the writer safely stops due to an integrity condition."""


@dataclass(slots=True)
class CaptureSegment:
    final_path: Path
    partial_path: Path
    event_final_path: Path
    event_partial_path: Path


@dataclass(slots=True)
class CaptureResult:
    segments: list[Path] = field(default_factory=list)
    incomplete: bool = False


class AscRecorder:
    """Write every supplied frame before any UI-specific projection exists.

    The historical name remains for compatibility; the profile selects ASC or
    PCAN-View text TRC before acquisition starts.
    """

    def __init__(self, free_space: Callable[[Path], int] | None = None) -> None:
        self._free_space = free_space or self._default_free_space
        self._naming = RecordingNaming()
        self._settings: RecordingSettings | None = None
        self._profile_name = "measurement"
        self._started_at: datetime | None = None
        self._timestamp_origin: float | None = None
        self._segment_number = 0
        self._segment: CaptureSegment | None = None
        self._reservation: Reservation | None = None
        self._asc: TextIO | None = None
        self._events: TextIO | None = None
        self._result = CaptureResult()
        self._warnings: list[str] = []
        self._warned_low_space = False
        self._frames_since_space_check = 0
        self._format = "asc"

    @property
    def active(self) -> bool:
        return self._asc is not None

    def start(
        self,
        settings: RecordingSettings,
        profile_name: str,
        now: datetime | None = None,
        reservation: Reservation | None = None,
    ) -> Path:
        """Open the first segment, honouring an already-reserved capture target.

        The reservation, when given, was created by ``RecordingNaming.reserve``
        immediately before this call: it names the exact first-segment path this
        writer must use so the atomic first-free search and the raw writer never
        disagree about which file is the acquisition's target.
        """
        if self.active:
            raise RuntimeError("A recording is already active")
        self._settings = settings
        self._format = settings.capture_format
        self._profile_name = profile_name
        self._started_at = now or datetime.now().astimezone()
        self._timestamp_origin = None
        self._segment_number = 0
        self._reservation = reservation
        self._result = CaptureResult()
        self._warnings.clear()
        self._warned_low_space = False
        self._frames_since_space_check = SPACE_CHECK_INTERVAL_FRAMES
        return self._open_next_segment()

    def write_frame(self, frame: CanFrame) -> None:
        self._require_active()
        self._ensure_space_if_due()
        assert self._asc is not None
        if self._timestamp_origin is None:
            self._timestamp_origin = frame.timestamp
        timestamp = max(0.0, frame.timestamp - self._timestamp_origin)
        if self._format == "trc":
            self._write_trc_frame(timestamp, frame)
            self._rotate_if_needed()
            return
        identifier = f"{frame.arbitration_id:X}{'x' if frame.is_extended_id else ''}"
        direction = "Rx"
        kind = "r" if frame.is_remote_frame else "d"
        payload = ""
        if not frame.is_remote_frame:
            payload = " " + " ".join(f"{byte:02X}" for byte in frame.data)
        self._asc.write(
            f"   {timestamp:.6f} {self._asc_channel(frame.channel)}  {identifier:<15} "
            f"{direction}   {kind} {frame.dlc}{payload}\n"
        )
        self._rotate_if_needed()

    def write_event(self, event: BusEvent) -> None:
        self._require_active()
        self._ensure_space_if_due()
        assert self._asc is not None and self._events is not None
        relative = 0.0
        if self._timestamp_origin is not None:
            relative = max(0.0, event.timestamp - self._timestamp_origin)
        if self._format == "trc":
            self._asc.write(f"; PeakLive {event.kind}: {event.message.replace(chr(10), ' ')}\n")
        elif event.kind == "error_frame":
            self._asc.write(f"   {relative:.6f} {self._asc_channel(event.channel)}  ErrorFrame\n")
        else:
            escaped = event.message.replace("\n", " ")
            self._asc.write(f"// PeakLive {event.kind}: {escaped}\n")
        self._events.write(
            json.dumps(
                {
                    "timestamp": event.timestamp,
                    "kind": event.kind,
                    "message": event.message,
                    "channel": event.channel,
                },
                sort_keys=True,
            )
            + "\n"
        )

    def flush(self) -> None:
        """Push buffered records to disk so a partial capture stays recoverable.

        A driver that blocks during shutdown can leave the process holding the
        last batch in a Python buffer. Flushing per batch bounds what an
        unclean finalization can lose to the records not yet handed over.
        """
        if self._asc is not None:
            self._asc.flush()
        if self._events is not None:
            self._events.flush()

    def stop(self, clean: bool = True) -> CaptureResult:
        if not self.active:
            return self._result
        self._close_segment(clean)
        return self._result

    def _open_next_segment(self) -> Path:
        assert self._settings is not None and self._started_at is not None
        self._segment_number += 1
        if self._segment_number == 1 and self._reservation is not None:
            reservation = self._reservation
            reservation.final_path.parent.mkdir(parents=True, exist_ok=True)
            self._segment = CaptureSegment(
                final_path=reservation.final_path,
                partial_path=reservation.partial_path,
                event_final_path=reservation.event_final_path,
                event_partial_path=reservation.event_partial_path,
            )
        else:
            default_directory = Path.home() / "Documents" / "PeakLive" / "Captures"
            directory = Path(self._settings.directory or default_directory)
            directory.mkdir(parents=True, exist_ok=True)
            filename = self._naming.expand(
                self._settings.filename_template,
                profile_name=self._profile_name,
                now=self._started_at,
                iteration=self._settings.iteration,
                segment=self._segment_number,
                capture_format=self._format,
                text=self._settings.text,
            )
            final_path = self._next_available_path(directory / filename)
            event_final = final_path.with_suffix(".peaklive-events.jsonl")
            self._segment = CaptureSegment(
                final_path=final_path,
                partial_path=final_path.with_suffix(final_path.suffix + ".partial"),
                event_final_path=event_final,
                event_partial_path=event_final.with_suffix(event_final.suffix + ".partial"),
            )
        self._asc = self._segment.partial_path.open("w", encoding="utf-8", newline="\n")
        self._events = self._segment.event_partial_path.open("w", encoding="utf-8", newline="\n")
        if self._segment_number == 1 and self._reservation is not None:
            # The partial file now exists, which alone is enough to keep a
            # future first-free search away from this target; the exclusive
            # marker has served its purpose for the handoff race.
            self._reservation.marker_path.unlink(missing_ok=True)
        if self._format == "trc":
            self._asc.write("; PeakLive PCAN-View text TRC recording\n")
            self._asc.write("; time values are milliseconds\n")
        else:
            self._asc.write(f"date {self._started_at.strftime('%a %b %d %H:%M:%S %Y')}\n")
            self._asc.write("base hex  timestamps absolute\ninternal events logged\n")
            self._asc.write("// PeakLive ASC recording\n")
            started = self._started_at.strftime("%a %b %d %H:%M:%S %Y")
            self._asc.write(f"Begin Triggerblock {started}\n")
        return self._segment.final_path

    def _close_segment(self, clean: bool) -> None:
        assert self._segment is not None and self._asc is not None and self._events is not None
        if clean and self._format == "asc":
            self._asc.write("End Triggerblock\n")
        self._asc.flush()
        self._events.flush()
        self._asc.close()
        self._events.close()
        if clean:
            self._segment.partial_path.replace(self._segment.final_path)
            self._segment.event_partial_path.replace(self._segment.event_final_path)
            self._result.segments.append(self._segment.final_path)
        else:
            self._result.incomplete = True
        self._asc = None
        self._events = None
        self._segment = None

    def _rotate_if_needed(self) -> None:
        assert self._settings is not None and self._asc is not None
        if self._asc.tell() < self._settings.rotate_bytes:
            return
        self._close_segment(clean=True)
        self._open_next_segment()

    def _ensure_space_if_due(self) -> None:
        self._frames_since_space_check += 1
        if self._frames_since_space_check < SPACE_CHECK_INTERVAL_FRAMES:
            return
        self._frames_since_space_check = 0
        self._ensure_space()

    def _ensure_space(self) -> None:
        assert self._settings is not None and self._segment is not None
        available = self._free_space(self._segment.partial_path.parent)
        if available <= self._settings.stop_free_bytes:
            self._close_segment(clean=False)
            raise RecordingStopped(
                "Recording stopped: free disk space fell below "
                f"{_bytes_text(self._settings.stop_free_bytes)}"
            )
        if available <= self._settings.warn_free_bytes and not self._warned_low_space:
            # Warn once per recording so a low-space bench does not spam the log.
            self._warned_low_space = True
            self._warnings.append(
                f"Recording disk space is low: {_bytes_text(available)} free"
            )

    def take_warnings(self) -> list[str]:
        """Drain the recording warnings raised since the last call."""
        drained = list(self._warnings)
        self._warnings.clear()
        return drained

    def _write_trc_frame(self, timestamp: float, frame: CanFrame) -> None:
        """Emit the text TRC subset accepted by PeakLive's PCAN-View parser."""
        identifier = f"{frame.arbitration_id:X}{'x' if frame.is_extended_id else ''}"
        kind = "r" if frame.is_remote_frame else "d"
        payload = ""
        if not frame.is_remote_frame:
            payload = " " + " ".join(f"{byte:02X}" for byte in frame.data)
        self._asc.write(
            f"{self._asc_channel(frame.channel)}) {timestamp * 1000:.3f} Rx {identifier} "
            f"{kind} {frame.dlc}{payload}\n"
        )

    @staticmethod
    def _next_available_path(path: Path) -> Path:
        if not path.exists() and not path.with_suffix(path.suffix + ".partial").exists():
            return path
        suffix = 1
        while True:
            candidate = path.with_stem(f"{path.stem}_{suffix:02d}")
            candidate_partial = candidate.with_suffix(candidate.suffix + ".partial")
            if not candidate.exists() and not candidate_partial.exists():
                return candidate
            suffix += 1

    @staticmethod
    def _asc_channel(channel: str) -> str:
        match = re.search(r"(\d+)$", channel)
        return match.group(1) if match else "1"

    @staticmethod
    def _default_free_space(path: Path) -> int:
        return shutil.disk_usage(path).free

    def _require_active(self) -> None:
        if not self.active:
            raise RuntimeError("No active recording")


def _bytes_text(value: int) -> str:
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(value) < 1024 or unit == "TiB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{value} B"
        value /= 1024  # type: ignore[assignment]
    return f"{value} B"
