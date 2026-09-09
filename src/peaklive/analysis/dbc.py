"""Content-addressed, deterministic DBC decoding."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import cantools

from peaklive.domain import CanFrame

FrameKey = tuple[int, bool]


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
    database_name: str = ""
    frame_id: int = 0
    is_extended_id: bool = False

    @property
    def signal_key(self) -> str:
        if not self.database_name and self.frame_id == 0:
            return self.display_name
        return signal_key(
            self.database_hash,
            self.frame_id,
            self.is_extended_id,
            self.message_name,
            self.signal_name,
        )

    @property
    def display_name(self) -> str:
        return f"{self.message_name}.{self.signal_name}"


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
    is_extended_id: bool
    unit: str | None

    @property
    def display_name(self) -> str:
        return f"{self.message_name}.{self.signal_name}"

    @property
    def signal_key(self) -> str:
        return signal_key(
            self.database_hash,
            self.frame_id,
            self.is_extended_id,
            self.message_name,
            self.signal_name,
        )

    @property
    def frame_label(self) -> str:
        suffix = "x" if self.is_extended_id else ""
        return f"0x{self.frame_id:03X}{suffix}"


@dataclass(frozen=True, slots=True)
class DbcConflict:
    arbitration_id: int
    is_extended_id: bool
    candidates: tuple[DbcDefinition, ...]

    @property
    def frame_key(self) -> FrameKey:
        return self.arbitration_id, self.is_extended_id


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
    all_signal_names: tuple[str, ...]
    all_references: tuple[DbcSignalReference, ...]
    conflicts: tuple[DbcConflict, ...]
    signal_counts: dict[str, int]
    enabled_hashes: frozenset[str]
    resolutions: dict[FrameKey, str]

    def is_enabled(self, content_hash: str) -> bool:
        return content_hash in self.enabled_hashes

    @property
    def unresolved_conflicts(self) -> tuple[DbcConflict, ...]:
        return tuple(
            conflict
            for conflict in self.conflicts
            if conflict.frame_key not in self.resolutions
        )


class DbcCatalog:
    def __init__(self) -> None:
        self._definitions: list[DbcDefinition] = []
        self._disabled_hashes: set[str] = set()
        self._resolutions: dict[FrameKey, str] = {}
        # Keyed by arbitration ID: the resolved (definition, message) pair, the
        # _UNRESOLVED sentinel, or a cached AmbiguousMessageError to re-raise -
        # rebuilding candidates and fingerprints costs the same whether the
        # frame decodes cleanly or not, and a session can see thousands of
        # frames for the same ID before its catalog changes at all.
        self._decode_cache: dict[
            FrameKey, tuple[DbcDefinition, Any] | _Unresolved | AmbiguousMessageError
        ] = {}

    def _invalidate_decode_cache(self) -> None:
        self._decode_cache.clear()

    @property
    def definitions(self) -> tuple[DbcDefinition, ...]:
        return tuple(self._definitions)

    def signal_names(self, *, include_disabled: bool = False) -> tuple[str, ...]:
        """Return stable provenance-qualified keys suitable for persisted selection."""
        names = {
            signal_key(
                definition.content_hash,
                _message_arbitration_id(message),
                _message_is_extended(message),
                message.name,
                signal.name,
            )
            for definition in (
                self.definitions if include_disabled else self.enabled_definitions
            )
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
    def resolutions(self) -> dict[FrameKey, str]:
        return dict(self._resolutions)

    def signal_references(
        self, *, include_disabled: bool = False
    ) -> tuple[DbcSignalReference, ...]:
        """Return DBC/message/signal references for grouped operator navigation."""
        references = [
            DbcSignalReference(
                definition.content_hash,
                definition.path.name,
                message.name,
                signal.name,
                _message_arbitration_id(message),
                _message_is_extended(message),
                signal.unit,
            )
            for definition in (
                self.definitions if include_disabled else self.enabled_definitions
            )
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
                    item.frame_id,
                    item.is_extended_id,
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
            all_signal_names=self.signal_names(include_disabled=True),
            all_references=self.signal_references(include_disabled=True),
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
            frame_key: resolution
            for frame_key, resolution in self._resolutions.items()
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
                frame_key: resolution
                for frame_key, resolution in self._resolutions.items()
                if resolution != content_hash
            }
        self._invalidate_decode_cache()

    def is_enabled(self, content_hash: str) -> bool:
        return content_hash not in self._disabled_hashes

    def conflicts(self) -> tuple[DbcConflict, ...]:
        """Return non-equivalent frame-ID collisions requiring operator choice."""
        conflicts: list[DbcConflict] = []
        frame_keys = {
            (int(message.frame_id), _message_is_extended(message))
            for definition in self.enabled_definitions
            for message in definition.database.messages
        }
        for frame_id, is_extended in sorted(frame_keys):
            candidates = [
                (
                    definition,
                    _get_message_by_frame_key(definition.database, frame_id, is_extended),
                )
                for definition in self.enabled_definitions
                if self._has_message(definition.database, frame_id, is_extended)
            ]
            if len(candidates) < 2:
                continue
            fingerprints = {self._message_fingerprint(message) for _, message in candidates}
            if len(fingerprints) > 1:
                conflicts.append(
                    DbcConflict(
                        frame_id,
                        is_extended,
                        tuple(definition for definition, _ in candidates),
                    )
                )
        return tuple(conflicts)

    def resolve(
        self, arbitration_id: int, content_hash: str, is_extended_id: bool = False
    ) -> None:
        if content_hash not in {definition.content_hash for definition in self._definitions}:
            raise KeyError(f"Unknown DBC hash: {content_hash}")
        self._resolutions[(arbitration_id, is_extended_id)] = content_hash
        self._invalidate_decode_cache()

    def decode(self, frame: CanFrame) -> list[DecodedSignal]:
        if frame.is_remote_frame:
            return []
        key = frame.identifier_key
        cached = self._decode_cache.get(key)
        if cached is None:
            cached = self._resolve_candidate(key)
            self._decode_cache[key] = cached
        if cached is _UNRESOLVED:
            return []
        if isinstance(cached, AmbiguousMessageError):
            raise cached
        definition, message = cached
        values = definition.database.decode_message(
            _message_arbitration_id(message),
            frame.data,
            force_extended_id=_message_is_extended(message),
        )
        return [
            DecodedSignal(
                database_hash=definition.content_hash,
                message_name=message.name,
                signal_name=signal.name,
                value=values[signal.name],
                unit=signal.unit,
                database_name=definition.path.name,
                frame_id=_message_arbitration_id(message),
                is_extended_id=_message_is_extended(message),
            )
            for signal in message.signals
            if signal.name in values
        ]

    def _resolve_candidate(
        self, frame_key: FrameKey
    ) -> tuple[DbcDefinition, Any] | _Unresolved | AmbiguousMessageError:
        """Do the expensive per-ID work exactly once between catalog mutations."""
        arbitration_id, is_extended_id = frame_key
        candidates = [
            (
                definition,
                _get_message_by_frame_key(definition.database, arbitration_id, is_extended_id),
            )
            for definition in self.enabled_definitions
            if self._has_message(definition.database, arbitration_id, is_extended_id)
        ]
        if not candidates:
            return _UNRESOLVED
        try:
            return self._select_candidate(frame_key, candidates)
        except AmbiguousMessageError as error:
            return error

    @staticmethod
    def _has_message(database: Any, arbitration_id: int, is_extended_id: bool) -> bool:
        try:
            message = _get_message_by_frame_key(database, arbitration_id, is_extended_id)
        except KeyError:
            return False
        return _message_is_extended(message) == is_extended_id

    @staticmethod
    def _decode_dbc_text(content: bytes) -> str:
        for encoding in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError("dbc", content, 0, 1, "unsupported DBC text encoding")

    def _select_candidate(self, frame_key: FrameKey, candidates: list[tuple[DbcDefinition, Any]]):
        arbitration_id, is_extended_id = frame_key
        if len(candidates) == 1:
            return candidates[0]
        resolution = self._resolutions.get(frame_key)
        if resolution:
            return next(
                candidate for candidate in candidates if candidate[0].content_hash == resolution
            )
        fingerprints = {self._message_fingerprint(message) for _, message in candidates}
        if len(fingerprints) == 1:
            return candidates[0]
        raise AmbiguousMessageError(
            f"Arbitration ID 0x{arbitration_id:X}{'x' if is_extended_id else ''} "
            "has non-equivalent DBC definitions"
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


def frame_key_text(frame_key: FrameKey) -> str:
    arbitration_id, is_extended_id = frame_key
    prefix = "x" if is_extended_id else "s"
    return f"{prefix}:{arbitration_id}"


def parse_frame_key_text(raw: str) -> FrameKey:
    text = str(raw)
    if ":" not in text:
        return int(text), False
    prefix, value = text.split(":", 1)
    return int(value), prefix.casefold() == "x"


def signal_key(
    database_hash: str,
    frame_id: int,
    is_extended_id: bool,
    message_name: str,
    signal_name: str,
) -> str:
    suffix = "x" if is_extended_id else "s"
    return f"{database_hash}:{suffix}:{frame_id:X}:{message_name}.{signal_name}"


def signal_display_name(signal_name: str, references: tuple[DbcSignalReference, ...]) -> str:
    reference = next((item for item in references if item.signal_key == signal_name), None)
    return reference.display_name if reference is not None else signal_name


def split_signal_key(name: str) -> tuple[str, str]:
    legacy = name
    if name.count(":") >= 3:
        database_hash, frame_format, frame_id, legacy = name.split(":", 3)
        message, separator, signal = legacy.partition(".")
        if not separator:
            return name, name
        suffix = "x" if frame_format == "x" else ""
        return f"{message} [{database_hash[:8]} 0x{int(frame_id, 16):03X}{suffix}]", signal
    message, separator, signal = legacy.partition(".")
    if not separator:
        return name, name
    return message, signal


def signal_label(name: str) -> str:
    if name.count(":") < 3:
        return name
    database_hash, frame_format, frame_id, legacy = name.split(":", 3)
    suffix = "x" if frame_format == "x" else ""
    return f"{legacy} [{database_hash[:8]} 0x{int(frame_id, 16):03X}{suffix}]"


def signal_display_title(name: str) -> str:
    """The operator-facing "Message.Signal" identity, with no DBC hash or frame id.

    Unlike `signal_label`, this never leaks the technical provenance suffix, so
    it is safe to show by default (a graph lane title, a concise tooltip);
    `signal_label` remains the place to reach for the full technical identity.
    """
    if name.count(":") < 3:
        return name
    return name.split(":", 3)[3]


def _message_is_extended(message: Any) -> bool:
    return bool(getattr(message, "is_extended_frame", False))


def _message_arbitration_id(message: Any) -> int:
    frame_id = int(message.frame_id)
    return frame_id & 0x1FFFFFFF if _message_is_extended(message) else frame_id


def _get_message_by_frame_key(database: Any, arbitration_id: int, is_extended_id: bool) -> Any:
    try:
        return database.get_message_by_frame_id(arbitration_id)
    except KeyError:
        if not is_extended_id:
            raise
    return database.get_message_by_frame_id(arbitration_id | 0x80000000)
