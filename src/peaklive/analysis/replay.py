"""Streaming ASC and PCAN-View text TRC replay without eager file loading."""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

from peaklive.domain import BusEvent, CanFrame

_TIMESTAMP = re.compile(r"^\s*([+-]?\d+(?:\.\d+)?)\s+(.*)$")
_TRC = re.compile(r"^\s*\d+\)\s*([+-]?\d+(?:\.\d+)?)\s+(.*)$")
_HEX = re.compile(r"^[0-9A-Fa-f]+$")


def iter_trace(path: Path) -> Iterator[CanFrame | BusEvent]:
    """Incrementally normalize supported `.asc` and text `.trc` captures."""
    parser = _parse_trc_line if path.suffix.lower() == ".trc" else _parse_asc_line
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line_number, raw in enumerate(handle, 1):
            record = parser(raw)
            if record is not None:
                yield record
            elif raw.strip() and not _is_header(raw):
                yield BusEvent(0.0, "replay_anomaly", f"Line {line_number}: unsupported record")


def _parse_asc_line(raw: str) -> CanFrame | BusEvent | None:
    match = _TIMESTAMP.match(raw)
    if not match:
        return None
    timestamp = float(match.group(1))
    tokens = match.group(2).split()
    if len(tokens) >= 2 and tokens[1].lower().startswith("errorframe"):
        return BusEvent(timestamp, "error_frame", "ErrorFrame", tokens[0])
    if "status" in raw.lower():
        return BusEvent(timestamp, "bus_status", match.group(2))
    if len(tokens) < 5 or tokens[2] not in {"Rx", "Tx"}:
        return BusEvent(timestamp, "replay_anomaly", "Unsupported ASC record")
    channel, identifier, _, kind, dlc_text, *payload = tokens
    return _frame(timestamp, channel, identifier, kind, dlc_text, payload)


def _parse_trc_line(raw: str) -> CanFrame | BusEvent | None:
    if raw.lstrip().startswith(";"):
        return None
    match = _TRC.match(raw)
    if not match:
        return None
    timestamp = float(match.group(1)) / 1000
    tokens = match.group(2).split()
    if not tokens:
        return BusEvent(timestamp, "replay_anomaly", "Empty TRC record")
    if tokens[0].lower() in {"warning", "warn", "error"}:
        return BusEvent(timestamp, "trc_event", match.group(2))
    if len(tokens) < 3 or tokens[0].lower() not in {"rx", "tx"}:
        return BusEvent(timestamp, "replay_anomaly", "Unsupported TRC record")
    return _frame(timestamp, "1", tokens[1], "d", tokens[2], tokens[3:])


def _frame(
    timestamp: float,
    channel: str,
    identifier: str,
    kind: str,
    dlc_text: str,
    payload: list[str],
) -> CanFrame | BusEvent:
    extended = identifier.endswith(("x", "X"))
    identifier = identifier[:-1] if extended else identifier
    if not _HEX.fullmatch(identifier):
        return BusEvent(timestamp, "replay_anomaly", "Invalid arbitration ID", channel)
    try:
        dlc = int(dlc_text)
    except ValueError:
        return BusEvent(timestamp, "replay_anomaly", "Invalid DLC", channel)
    if not 0 <= dlc <= 8 or (kind.lower() != "r" and len(payload) != dlc):
        return BusEvent(timestamp, "replay_anomaly", "Invalid classic CAN payload", channel)
    if any(not _HEX.fullmatch(byte) or len(byte) > 2 for byte in payload):
        return BusEvent(timestamp, "replay_anomaly", "Invalid payload byte", channel)
    return CanFrame(
        timestamp,
        int(identifier, 16),
        b"" if kind.lower() == "r" else bytes(int(byte, 16) for byte in payload),
        channel,
        extended,
        kind.lower() == "r",
    )


def _is_header(raw: str) -> bool:
    lowered = raw.strip().lower()
    prefixes = ("//", ";", "date", "base", "internal", "begin", "end")
    return not lowered or lowered.startswith(prefixes)
