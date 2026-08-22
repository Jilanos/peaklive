"""Content-addressed, deterministic DBC decoding."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import cantools

from peaklive.domain import CanFrame


class AmbiguousMessageError(RuntimeError):
    """Raised until an arbitration-ID conflict is resolved explicitly."""


@dataclass(frozen=True, slots=True)
class DecodedSignal:
    database_hash: str
    message_name: str
    signal_name: str
    value: Any
    unit: str | None


@dataclass(frozen=True, slots=True)
class DbcDefinition:
    content_hash: str
    path: Path
    database: Any


class DbcCatalog:
    def __init__(self) -> None:
        self._definitions: list[DbcDefinition] = []
        self._resolutions: dict[int, str] = {}

    @property
    def definitions(self) -> tuple[DbcDefinition, ...]:
        return tuple(self._definitions)

    def load(self, path: Path) -> DbcDefinition:
        content = path.read_bytes()
        digest = sha256(content).hexdigest()
        existing = next((item for item in self._definitions if item.content_hash == digest), None)
        if existing is not None:
            return existing
        database = cantools.database.load_string(content.decode("utf-8"))
        definition = DbcDefinition(digest, path, database)
        self._definitions.append(definition)
        return definition

    def resolve(self, arbitration_id: int, content_hash: str) -> None:
        if content_hash not in {definition.content_hash for definition in self._definitions}:
            raise KeyError(f"Unknown DBC hash: {content_hash}")
        self._resolutions[arbitration_id] = content_hash

    def decode(self, frame: CanFrame) -> list[DecodedSignal]:
        candidates = [
            (definition, definition.database.get_message_by_frame_id(frame.arbitration_id))
            for definition in self._definitions
            if self._has_message(definition.database, frame.arbitration_id)
        ]
        if not candidates:
            return []
        selected = self._select_candidate(frame.arbitration_id, candidates)
        definition, message = selected
        values = definition.database.decode_message(frame.arbitration_id, frame.data)
        return [
            DecodedSignal(
                definition.content_hash,
                message.name,
                signal.name,
                values[signal.name],
                signal.unit,
            )
            for signal in message.signals
            if signal.name in values
        ]

    @staticmethod
    def _has_message(database: Any, arbitration_id: int) -> bool:
        try:
            database.get_message_by_frame_id(arbitration_id)
        except KeyError:
            return False
        return True

    def _select_candidate(self, arbitration_id: int, candidates: list[tuple[DbcDefinition, Any]]):
        if len(candidates) == 1:
            return candidates[0]
        resolution = self._resolutions.get(arbitration_id)
        if resolution:
            return next(
                candidate for candidate in candidates if candidate[0].content_hash == resolution
            )
        fingerprints = {self._message_fingerprint(message) for _, message in candidates}
        if len(fingerprints) == 1:
            return candidates[0]
        raise AmbiguousMessageError(
            f"Arbitration ID 0x{arbitration_id:X} has non-equivalent DBC definitions"
        )

    @staticmethod
    def _message_fingerprint(message: Any) -> tuple[Any, ...]:
        return (
            message.frame_id,
            message.length,
            tuple(
                (
                    signal.name,
                    signal.start,
                    signal.length,
                    signal.byte_order,
                    signal.is_signed,
                    signal.scale,
                )
                for signal in message.signals
            ),
        )
