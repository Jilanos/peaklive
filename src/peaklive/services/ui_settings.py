"""Application-scoped interface preferences, kept out of measurement profiles.

Language belongs to the installation, not to a vehicle setup: selecting another
measurement profile must never change the interface language, and adding a
language field to the profile schema would make exactly that happen.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from platformdirs import user_data_path

from peaklive.diagnostics import logger
from peaklive.i18n import SOURCE_LOCALE, normalize_locale

SCHEMA_VERSION = 1
SETTINGS_FILENAME = "ui-settings.json"


@dataclass(slots=True)
class UiSettings:
    """The interface preferences one installation carries between launches."""

    locale: str = SOURCE_LOCALE


class UiSettingsStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        configured = os.environ.get("PEAKLIVE_DATA_DIR")
        self.data_dir = data_dir or (Path(configured) if configured else user_data_path("PeakLive"))
        self.path = self.data_dir / SETTINGS_FILENAME
        self._unknown: dict[str, Any] = {}

    def load(self) -> UiSettings:
        """Read the stored preferences, recovering to defaults on any damage."""
        raw = self._read()
        return UiSettings(locale=normalize_locale(raw.get("locale")))

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            # utf-8-sig, not utf-8: on Windows anything that has passed through
            # Notepad or PowerShell carries a byte-order mark, and a preference
            # file edited by hand must not read as corrupt because of it.
            loaded = json.loads(self.path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            logger().warning("Interface settings %s were unreadable; using defaults.", self.path)
            return {}
        if not isinstance(loaded, dict):
            logger().warning("Interface settings %s were malformed; using defaults.", self.path)
            return {}
        # Settings a future build owns must survive this build writing the file.
        self._unknown = {
            name: value
            for name, value in loaded.items()
            if name not in {"schema_version", "locale"}
        }
        return loaded

    def save_locale(self, locale: str) -> None:
        """Persist the selected locale atomically, preserving unrelated settings.

        Raises ``OSError`` so the caller can keep the chosen language live and
        warn that it was not stored, rather than silently claiming it was.
        """
        self._read()
        payload = dict(self._unknown)
        payload["schema_version"] = SCHEMA_VERSION
        payload["locale"] = normalize_locale(locale)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(f"{SETTINGS_FILENAME}.{os.getpid()}.{uuid4().hex[:8]}.tmp")
        try:
            text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
            with temporary.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            temporary.replace(self.path)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise
