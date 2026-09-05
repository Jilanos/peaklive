"""Atomic, local-only persistence for named measurement profiles."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from platformdirs import user_data_path

from peaklive.diagnostics import logger
from peaklive.domain import MeasurementProfile

SCHEMA_VERSION = 1


class ProfileSchemaError(ValueError):
    """The profile store uses a schema version this build cannot read."""


def migrate_profile_store(raw: dict[str, Any]) -> dict[str, Any]:
    """Dispatch persisted data through explicit, deterministic schema migrations."""
    version = raw.get("schema_version", 0)
    if isinstance(version, bool) or not isinstance(version, int) or version < 0:
        raise ProfileSchemaError("Profile store schema version is invalid.")
    if version > SCHEMA_VERSION:
        raise ProfileSchemaError(
            f"Profile store schema version {version} is newer than supported {SCHEMA_VERSION}."
        )
    migrated = dict(raw)
    if version == 0:
        # Pre-versioned stores already use the v1 profile shape; only the
        # dispatch marker was missing.
        migrated["schema_version"] = SCHEMA_VERSION
    return migrated


class ProfileNameError(ValueError):
    """An operator-supplied setup name is blank or already taken."""


@dataclass(slots=True)
class ProfileState:
    profiles: list[MeasurementProfile]
    last_profile_id: str
    #: Set only when ``load()`` had to discard an unreadable or invalid
    #: store and start from defaults; carries where the original file was
    #: moved so the shell can tell the operator.
    recovered_from: Path | None = None

    @property
    def selected(self) -> MeasurementProfile:
        return next(
            profile for profile in self.profiles if profile.identifier == self.last_profile_id
        )

    def duplicate_selected(self, name: str) -> MeasurementProfile:
        """Append an independent copy of the active setup and select it.

        Validation happens before anything is mutated, so a rejected name
        leaves the state exactly as it was.
        """
        cleaned = name.strip()
        if not cleaned:
            raise ProfileNameError("A measurement setup name cannot be blank.")
        if any(profile.name.casefold() == cleaned.casefold() for profile in self.profiles):
            raise ProfileNameError(f"A measurement setup named {cleaned!r} already exists.")
        copy = self.selected.duplicate(cleaned)
        self.profiles.append(copy)
        self.last_profile_id = copy.identifier
        return copy


class ProfileStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        configured = os.environ.get("PEAKLIVE_DATA_DIR")
        self.data_dir = data_dir or (Path(configured) if configured else user_data_path("PeakLive"))
        self.path = self.data_dir / "profiles.json"

    def load(self) -> ProfileState:
        if not self.path.exists():
            profile = MeasurementProfile(name="Default measurement")
            return ProfileState([profile], profile.identifier)
        try:
            raw = migrate_profile_store(json.loads(self.path.read_text(encoding="utf-8")))
            profiles = [MeasurementProfile.from_dict(item) for item in raw.get("profiles", [])]
        except (json.JSONDecodeError, OSError, ValueError, TypeError, KeyError, AttributeError):
            backup_path = self._quarantine_corrupt_store()
            logger().warning(
                "Profile store %s was unreadable or invalid; moved it to %s and started"
                " from defaults.",
                self.path,
                backup_path,
            )
            profile = MeasurementProfile(name="Default measurement")
            return ProfileState([profile], profile.identifier, recovered_from=backup_path)
        if not profiles:
            profile = MeasurementProfile(name="Default measurement")
            return ProfileState([profile], profile.identifier)
        requested = str(raw.get("last_profile_id", profiles[0].identifier))
        selected = next(
            (profile for profile in profiles if profile.identifier == requested),
            profiles[0],
        )
        return ProfileState(profiles, selected.identifier)

    def _quarantine_corrupt_store(self) -> Path:
        """Rename the unreadable store out of the way so it isn't overwritten."""
        stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
        backup_path = self.data_dir / f"profiles.json.corrupt-{stamp}"
        self.path.replace(backup_path)
        return backup_path

    def save_as(self, state: ProfileState, name: str) -> MeasurementProfile:
        """Duplicate the active setup under `name` and persist atomically.

        A failed write must not leave the in-memory state claiming a setup the
        file does not have, so the copy is rolled back when persistence fails.
        """
        previous = state.last_profile_id
        copy = state.duplicate_selected(name)
        try:
            self.save(state)
        except OSError:
            state.profiles.remove(copy)
            state.last_profile_id = previous
            raise
        return copy

    def save(self, state: ProfileState) -> None:
        """Write the store atomically, durably, and safely alongside another instance.

        A fixed temporary name lets two writers - two PeakLive instances, or
        a save racing a crash-recovery quarantine - collide on the same
        partial file. A name unique per process and per call rules that out.
        The write is flushed and fsynced before the rename, so a crash right
        after a successful save cannot leave the replaced file truncated; a
        failure before the rename never touches `self.path`, so a prior,
        readable store is always left in place.
        """
        self.data_dir.mkdir(parents=True, exist_ok=True)
        raw: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "last_profile_id": state.last_profile_id,
            "profiles": [profile.to_dict() for profile in state.profiles],
        }
        payload = json.dumps(raw, indent=2, sort_keys=True) + "\n"
        temporary = self.path.with_name(
            f"{self.path.name}.{os.getpid()}.{uuid4().hex[:8]}.tmp"
        )
        try:
            with temporary.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            temporary.replace(self.path)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise
