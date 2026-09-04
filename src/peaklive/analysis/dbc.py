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


class _Unresolved:
    """Sentinel: no enabled definition has a message for this arbitration ID."""


_UNRESOLVED = _Unresolved()


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

    @property
    def short_hash(self) -> str:
        return self.content_hash[:8]


@dataclass(frozen=True, slots=True)
class DbcSignalReference:
    database_hash: str
    database_name: str
    message_name: str
    signal_name: str
    frame_id: int
    unit: str | None

    @property
    def display_name(self) -> str:
        return f"{self.message_name}.{self.signal_name}"


@dataclass(frozen=True, slots=True)
class DbcConflict:
    arbitration_id: int
    candidates: tuple[DbcDefinition, ...]


@dataclass(frozen=True, slots=True)
class CatalogView:
    """Everything the workspace needs to redraw itself for one catalog state.

    Deriving conflicts and signal references is the expensive part of any DBC
    mutation, so it is computed once — off the UI thread where possible — and
    handed to the panels as finished data. A view is immutable and describes
    exactly one catalog, which is what makes a mutation commit atomically:
    either every panel sees the new view or every panel still sees the old one.
    """

    catalog: DbcCatalog
    definitions: tuple[DbcDefinition, ...]
    references: tuple[DbcSignalReference, ...]
    signal_names: tuple[str, ...]
    conflicts: tuple[DbcConflict, ...]
    signal_counts: dict[str, int]
    enabled_hashes: frozenset[str]
    resolutions: dict[int, str]

    def is_enabled(self, content_hash: str) -> bool:
        return content_hash in self.enabled_hashes

    @property
    def unresolved_conflicts(self) -> tuple[DbcConflict, ...]:
        return tuple(
            conflict
            for conflict in self.conflicts
            if conflict.arbitration_id not in self.resolutions
        )


class DbcCatalog:
    def __init__(self) -> None:
        self._definitions: list[DbcDefinition] = []
        self._disabled_hashes: set[str] = set()
        self._resolutions: dict[int, str] = {}
        # Keyed by arbitration ID: the resolved (definition, message) pair, the
        # _UNRESOLVED sentinel, or a cached AmbiguousMessageError to re-raise -
        # rebuilding candidates and fingerprints costs the same whether the
        # frame decodes cleanly or not, and a session can see thousands of
        # frames for the same ID before its catalog changes at all.
        self._decode_cache: dict[
            int, tuple[DbcDefinition, Any] | _Unresolved | AmbiguousMessageError
        ] = {}

    def _invalidate_decode_cache(self) -> None:
        self._decode_cache.clear()

    @property
    def definitions(self) -> tuple[DbcDefinition, ...]:
        return tuple(self._definitions)

    def signal_names(self) -> tuple[str, ...]:
        """Return stable display names suitable for a signal-selection UI."""
        names = {
            f"{message.name}.{signal.name}"
            for definition in self.enabled_definitions
            for message in definition.database.messages
            for signal in message.signals
        }
        return tuple(sorted(names))

    @property
    def enabled_definitions(self) -> tuple[DbcDefinition, ...]:
        return tuple(
            definition
            for definition in self._definitions
            if definition.content_hash not in self._disabled_hashes
        )

    @property
    def resolutions(self) -> dict[int, str]:
        return dict(self._resolutions)

    def signal_references(self) -> tuple[DbcSignalReference, ...]:
        """Return DBC/message/signal references for grouped operator navigation."""
        references = [
            DbcSignalReference(
                definition.content_hash,
                definition.path.name,
                message.name,
                signal.name,
                int(message.frame_id),
                signal.unit,
            )
            for definition in self.enabled_definitions
            for message in definition.database.messages
            for signal in message.signals
        ]
        return tuple(
            sorted(
                references,
                key=lambda item: (
                    item.database_name.casefold(),
                    item.message_name.casefold(),
                    item.signal_name.casefold(),
                    item.database_hash,
                ),
            )
        )

    def clear(self) -> None:
        """Forget transient DBC definitions when the operator changes profile."""
        self._definitions.clear()
        self._disabled_hashes.clear()
        self._resolutions.clear()
        self._invalidate_decode_cache()

    def copy(self) -> DbcCatalog:
        """Return an independent catalog over the same immutable definitions.

        A mutation is prepared on a copy so the live catalog keeps decoding
        frames untouched until the new state is ready to commit.
        """
        duplicate = DbcCatalog()
        duplicate._definitions = list(self._definitions)
        duplicate._disabled_hashes = set(self._disabled_hashes)
        duplicate._resolutions = dict(self._resolutions)
        return duplicate

    def view(self) -> CatalogView:
        """Compute every derived projection the workspace panels need."""
        return CatalogView(
            catalog=self,
            definitions=self.definitions,
            references=self.signal_references(),
            signal_names=self.signal_names(),
            conflicts=self.conflicts(),
            signal_counts={
                definition.content_hash: sum(
                    len(message.signals) for message in definition.database.messages
                )
                for definition in self._definitions
            },
            enabled_hashes=frozenset(
                definition.content_hash
                for definition in self._definitions
                if definition.content_hash not in self._disabled_hashes
            ),
            resolutions=self.resolutions,
        )

    def load(self, path: Path) -> DbcDefinition:
        content = path.read_bytes()
        digest = sha256(content).hexdigest()
        existing = next((item for item in self._definitions if item.content_hash == digest), None)
        if existing is not None:
            return existing
        try:
            database = cantools.database.load_string(self._decode_dbc_text(content))
        except cantools.database.UnsupportedDatabaseFormatError as error:
            # Keep the boundary narrow: callers handle OSError and ValueError.
            raise ValueError(f"Unsupported or malformed DBC file: {error}") from error
        definition = DbcDefinition(digest, path, database)
        self._definitions.append(definition)
        self._invalidate_decode_cache()
        return definition

    def remove(self, content_hash: str) -> None:
        self._definitions = [
            definition
            for definition in self._definitions
            if definition.content_hash != content_hash
        ]
        self._disabled_hashes.discard(content_hash)
        self._resolutions = {
            arbitration_id: resolution
            for arbitration_id, resolution in self._resolutions.items()
            if resolution != content_hash
        }
        self._invalidate_decode_cache()

    def set_enabled(self, content_hash: str, enabled: bool) -> None:
        if content_hash not in {definition.content_hash for definition in self._definitions}:
            raise KeyError(f"Unknown DBC hash: {content_hash}")
        if enabled:
            self._disabled_hashes.discard(content_hash)
        else:
            self._disabled_hashes.add(content_hash)
            self._resolutions = {
                arbitration_id: resolution
                for arbitration_id, resolution in self._resolutions.items()
                if resolution != content_hash
            }
        self._invalidate_decode_cache()

    def is_enabled(self, content_hash: str) -> bool:
        return content_hash not in self._disabled_hashes

    def conflicts(self) -> tuple[DbcConflict, ...]:
        """Return non-equivalent frame-ID collisions requiring operator choice."""
        conflicts: list[DbcConflict] = []
        frame_ids = {
            int(message.frame_id)
            for definition in self.enabled_definitions
            for message in definition.database.messages
        }
        for frame_id in sorted(frame_ids):
            candidates = [
                (definition, definition.database.get_message_by_frame_id(frame_id))
                for definition in self.enabled_definitions
                if self._has_message(definition.database, frame_id)
            ]
            if len(candidates) < 2:
                continue
            fingerprints = {self._message_fingerprint(message) for _, message in candidates}
            if len(fingerprints) > 1:
                conflicts.append(
                    DbcConflict(frame_id, tuple(definition for definition, _ in candidates))
                )
        return tuple(conflicts)

    def resolve(self, arbitration_id: int, content_hash: str) -> None:
        if content_hash not in {definition.content_hash for definition in self._definitions}:
            raise KeyError(f"Unknown DBC hash: {content_hash}")
        self._resolutions[arbitration_id] = content_hash
        self._invalidate_decode_cache()

    def decode(self, frame: CanFrame) -> list[DecodedSignal]:
        cached = self._decode_cache.get(frame.arbitration_id)
        if cached is None:
            cached = self._resolve_candidate(frame.arbitration_id)
            self._decode_cache[frame.arbitration_id] = cached
        if cached is _UNRESOLVED:
            return []
        if isinstance(cached, AmbiguousMessageError):
            raise cached
        definition, message = cached
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

    def _resolve_candidate(
        self, arbitration_id: int
    ) -> tuple[DbcDefinition, Any] | _Unresolved | AmbiguousMessageError:
        """Do the expensive per-ID work exactly once between catalog mutations."""
        candidates = [
            (definition, definition.database.get_message_by_frame_id(arbitration_id))
            for definition in self.enabled_definitions
            if self._has_message(definition.database, arbitration_id)
        ]
        if not candidates:
            return _UNRESOLVED
        try:
            return self._select_candidate(arbitration_id, candidates)
        except AmbiguousMessageError as error:
            return error

    @staticmethod
    def _has_message(database: Any, arbitration_id: int) -> bool:
        try:
            database.get_message_by_frame_id(arbitration_id)
        except KeyError:
            return False
        return True

    @staticmethod
    def _decode_dbc_text(content: bytes) -> str:
        for encoding in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError("dbc", content, 0, 1, "unsupported DBC text encoding")

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
