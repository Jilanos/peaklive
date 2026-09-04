"""Streaming ASC and PCAN-View text TRC replay without eager file loading."""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from peaklive.domain import BusEvent, CanFrame

_TIMESTAMP = re.compile(r"^\s*([+-]?\d+(?:\.\d+)?)\s+(.*)$")
_TRC = re.compile(r"^\s*\d+\)\s*([+-]?\d+(?:\.\d+)?)\s+(.*)$")
_HEX = re.compile(r"^[0-9A-Fa-f]+$")

#: The longest chunk one `readline()` call will buffer. Supported captures are
#: one short record per line; binary-like input can be one line for its
#: entire length, and reading that unbounded would defeat every other bound
#: in the parse path. A line longer than this is read in bounded slices and
#: each slice is judged - and, if unparseable, counted - on its own.
_MAX_LINE_LENGTH = 65_536


@dataclass(slots=True)
class TraceCursor:
    """How much of the source a streaming parse has consumed so far.

    A text-mode iterator cannot be asked for its file offset, so the cursor
    accumulates line lengths instead. Supported ASC and TRC captures are ASCII,
    which makes that an exact byte count in practice and a close approximation
    otherwise - close enough for a progress bar, and never a reason to read the
    file twice.
    """

    consumed: int = 0


def iter_trace(path: Path, cursor: TraceCursor | None = None) -> Iterator[CanFrame | BusEvent]:
    """Incrementally normalize supported `.asc` and text `.trc` captures."""
    parser = _parse_trc_line if path.suffix.lower() == ".trc" else None
    base = 16
    with path.open(encoding="utf-8", errors="replace") as handle:
        for raw in _read_bounded_lines(handle):
            if cursor is not None:
                cursor.consumed += len(raw)
            if parser is None:
                header_base = _declared_base(raw)
                if header_base is not None:
                    base = header_base
                record = _parse_asc_line(raw, base=base)
            else:
                record = parser(raw)
            if record is not None:
                yield record
            elif raw.strip() and not _is_header(raw):
                # A stable, line-count-independent message: the anomaly key
                # every caller aggregates on must never grow with the file.
                yield BusEvent(0.0, "replay_anomaly", "Unsupported record")


def _read_bounded_lines(handle) -> Iterator[str]:  # type: ignore[no-untyped-def]
    """Yield each line, splitting anything longer than `_MAX_LINE_LENGTH`.

    `TextIOWrapper.readline(size)` never reads more than `size` characters and
    stops early at a real newline, so ordinary captures are unaffected; only a
    pathologically long or newline-free line - the shape binary-like input
    tends to take - is ever read in more than one bounded slice.
    """
    while True:
        raw = handle.readline(_MAX_LINE_LENGTH)
        if not raw:
            return
        yield raw


def _parse_asc_line(raw: str, *, base: int = 16) -> CanFrame | BusEvent | None:
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
    return _frame(timestamp, channel, identifier, kind, dlc_text, payload, base=base)


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
    # PCAN-View exports either ``Rx ID DLC data`` or ``Rx ID d DLC data``.
    if len(tokens) >= 4 and tokens[2].lower() in {"d", "r"}:
        return _frame(timestamp, "1", tokens[1], tokens[2], tokens[3], tokens[4:])
    return _frame(timestamp, "1", tokens[1], "d", tokens[2], tokens[3:])


def _frame(
    timestamp: float,
    channel: str,
    identifier: str,
    kind: str,
    dlc_text: str,
    payload: list[str],
    *,
    base: int = 16,
) -> CanFrame | BusEvent:
    extended = identifier.endswith(("x", "X"))
    identifier = identifier[:-1] if extended else identifier
    if base == 16 and identifier.lower().startswith("0x"):
        identifier = identifier[2:]
    invalid_identifier = (
        not identifier
        or (base == 16 and not _HEX.fullmatch(identifier))
        or (base == 10 and not identifier.isdecimal())
    )
    if invalid_identifier:
        return BusEvent(timestamp, "replay_anomaly", "Invalid arbitration ID", channel)
    try:
        dlc = int(dlc_text)
    except ValueError:
        return BusEvent(timestamp, "replay_anomaly", "Invalid DLC", channel)
    if not 0 <= dlc <= 8 or (kind.lower() != "r" and len(payload) < dlc):
        return BusEvent(timestamp, "replay_anomaly", "Invalid classic CAN payload", channel)
    # Vector ASC exports can append record metadata (for example ``Length``,
    # ``BitCount``, and ``ID``) after the data bytes.  It is not part of the
    # CAN payload, which is always exactly DLC bytes long.
    payload = payload[:dlc]
    def valid_byte(value: str) -> bool:
        if base == 16:
            return bool(_HEX.fullmatch(value)) and len(value) <= 2
        return value.isdecimal() and int(value) <= 255
    if any(not valid_byte(byte) for byte in payload):
        return BusEvent(timestamp, "replay_anomaly", "Invalid payload byte", channel)
    return CanFrame(
        timestamp,
        int(identifier, base),
        b"" if kind.lower() == "r" else bytes(int(byte, base) for byte in payload),
        channel,
        extended,
        kind.lower() == "r",
    )


def _is_header(raw: str) -> bool:
    lowered = raw.strip().lower()
    prefixes = ("//", ";", "date", "base", "internal", "begin", "end")
    return not lowered or lowered.startswith(prefixes)


def _declared_base(raw: str) -> int | None:
    match = re.match(r"^\s*base\s+(hex|dec(?:imal)?)\b", raw, re.IGNORECASE)
    if not match:
        return None
    return 16 if match.group(1).lower() == "hex" else 10
