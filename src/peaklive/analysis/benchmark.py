"""Deterministic synthetic captures for reproducible performance measurement.

An audit is only evidence if anyone can rerun it, which rules out shipping a
recorded capture: real traces are large, and they carry whatever was on the bus
the day they were taken. These generators produce byte-identical ASC text and a
matching DBC from nothing but a frame count, so the same measurement can be
taken on a developer machine, on CI, and on a packaged Windows build.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

#: The arbitration ID the synthetic messages start from.
BASE_ARBITRATION_ID = 0x300

#: Seconds between two synthetic frames - a 1 kHz bus.
FRAME_INTERVAL_S = 0.001


@dataclass(frozen=True, slots=True)
class CaptureProfile:
    """One representative volume the audit reports on."""

    name: str
    frames: int
    message_count: int = 8


#: The three volumes the audit covers: a glance, a normal bench capture, and a
#: capture large enough that any per-frame cost becomes visible.
SMALL = CaptureProfile("small", 2_000)
MEDIUM = CaptureProfile("medium", 20_000)
LARGE = CaptureProfile("large", 200_000)
CAPTURE_PROFILES: tuple[CaptureProfile, ...] = (SMALL, MEDIUM, LARGE)


def synthetic_dbc(message_count: int = 8) -> str:
    """Return DBC text decoding every message `synthetic_asc_lines` emits."""
    lines = ['VERSION ""', "NS_ :", "BS_:", "BU_: ECU"]
    for index in range(message_count):
        arbitration_id = BASE_ARBITRATION_ID + index
        lines.append(f"BO_ {arbitration_id} Synth{index}: 8 ECU")
        lines.append(f' SG_ Counter{index} : 0|16@1+ (1,0) [0|65535] "" ECU')
        lines.append(f' SG_ Level{index} : 16|16@1+ (0.1,0) [0|6553] "V" ECU')
        lines.append("")
    return "\n".join(lines) + "\n"


def synthetic_asc_lines(profile: CaptureProfile) -> list[str]:
    """Render one capture as ASC text lines, deterministically."""
    lines = ["date Thu Jan 1 00:00:00 1970", "base hex timestamps absolute", "Begin Triggerblock"]
    for index in range(profile.frames):
        timestamp = index * FRAME_INTERVAL_S
        arbitration_id = BASE_ARBITRATION_ID + index % profile.message_count
        counter = index % 65_536
        level = (index * 7) % 65_536
        payload = counter.to_bytes(2, "little") + level.to_bytes(2, "little") + b"\x00\x00\x00\x00"
        data = " ".join(f"{byte:02X}" for byte in payload)
        lines.append(f"{timestamp:.6f} 1 {arbitration_id:03X} Rx d 8 {data}")
    lines.append("End Triggerblock")
    return lines


def write_synthetic_capture(path: Path, profile: CaptureProfile) -> Path:
    """Write one synthetic ASC capture and return its path."""
    path.write_text("\n".join(synthetic_asc_lines(profile)) + "\n", encoding="utf-8")
    return path
