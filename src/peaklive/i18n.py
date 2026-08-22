"""Small semantic-key catalog loader for the English MVP."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

CATALOG_PATH = Path(__file__).parent / "i18n" / "en.json"


@lru_cache
def _catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def translate(key: str) -> str:
    value: Any = _catalog()
    for segment in key.split("."):
        value = value[segment]
    if not isinstance(value, str):
        raise KeyError(f"Translation key does not resolve to text: {key}")
    return value
