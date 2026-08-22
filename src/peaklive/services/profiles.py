"""Atomic, local-only persistence for named measurement profiles."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from platformdirs import user_data_path

from peaklive.domain import MeasurementProfile

SCHEMA_VERSION = 1


@dataclass(slots=True)
class ProfileState:
    profiles: list[MeasurementProfile]
    last_profile_id: str

    @property
    def selected(self) -> MeasurementProfile:
        return next(
            profile for profile in self.profiles if profile.identifier == self.last_profile_id
        )


class ProfileStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        configured = os.environ.get("PEAKLIVE_DATA_DIR")
        self.data_dir = data_dir or (Path(configured) if configured else user_data_path("PeakLive"))
        self.path = self.data_dir / "profiles.json"

    def load(self) -> ProfileState:
        if not self.path.exists():
            profile = MeasurementProfile(name="Default measurement")
            return ProfileState([profile], profile.identifier)
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        profiles = [MeasurementProfile.from_dict(item) for item in raw.get("profiles", [])]
        if not profiles:
            profile = MeasurementProfile(name="Default measurement")
            return ProfileState([profile], profile.identifier)
        requested = str(raw.get("last_profile_id", profiles[0].identifier))
        selected = next(
            (profile for profile in profiles if profile.identifier == requested),
            profiles[0],
        )
        return ProfileState(profiles, selected.identifier)

    def save(self, state: ProfileState) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        raw: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "last_profile_id": state.last_profile_id,
            "profiles": [profile.to_dict() for profile in state.profiles],
        }
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(self.path)
