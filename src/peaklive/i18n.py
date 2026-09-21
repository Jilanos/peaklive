"""Locale-aware semantic-key catalogs for the application-owned interface.

The lookup stays deliberately free of Qt so the analysis and service layers can
render operator-facing prose without importing the GUI toolkit. Language-change
subscribers are invoked synchronously by whoever calls :func:`set_locale`, which
is only ever the GUI thread.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from functools import lru_cache
from pathlib import Path
from typing import Any

CATALOG_DIR = Path(__file__).parent / "i18n"

#: The locale whose catalog is authoritative and used as the fallback.
SOURCE_LOCALE = "en"

#: Locale codes the application offers, in menu order.
SUPPORTED_LOCALES: tuple[str, ...] = ("en", "fr")

#: Autonyms shown to the operator; never translated between languages.
LOCALE_AUTONYMS: dict[str, str] = {"en": "English", "fr": "Français"}

_locale = SOURCE_LOCALE
_listeners: list[Callable[[str], None]] = []
_reported_missing: set[tuple[str, str]] = set()


def catalog_path(locale: str) -> Path:
    return CATALOG_DIR / f"{locale}.json"


@lru_cache
def _catalog(locale: str) -> dict[str, Any]:
    path = catalog_path(locale)
    if not path.exists():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # A damaged deployment must not take the live window down; the source
        # catalog still answers every key.
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _lookup(locale: str, key: str) -> str | None:
    value: Any = _catalog(locale)
    for segment in key.split("."):
        if not isinstance(value, dict) or segment not in value:
            return None
        value = value[segment]
    return value if isinstance(value, str) and value else None


def _walk(node: dict[str, Any], prefix: str = "") -> Iterator[tuple[str, Any]]:
    for name, value in node.items():
        key = f"{prefix}.{name}" if prefix else name
        if isinstance(value, dict):
            yield from _walk(value, key)
        else:
            yield key, value


def catalog_entries(locale: str) -> dict[str, Any]:
    """Every leaf of one catalog, flattened to dotted keys."""
    return dict(_walk(_catalog(locale)))


def catalog_keys(locale: str) -> set[str]:
    return set(catalog_entries(locale))


def has_key(key: str) -> bool:
    """Whether the source catalog defines `key`; the validation entry point."""
    return _lookup(SOURCE_LOCALE, key) is not None


def normalize_locale(locale: object) -> str:
    """Map anything unrecognised onto the source locale."""
    if isinstance(locale, str) and locale in SUPPORTED_LOCALES:
        return locale
    return SOURCE_LOCALE


def current_locale() -> str:
    return _locale


def set_locale(locale: str) -> bool:
    """Select `locale` and notify subscribers; returns whether it changed."""
    global _locale
    resolved = normalize_locale(locale)
    if resolved == _locale:
        return False
    _locale = resolved
    for listener in tuple(_listeners):
        listener(resolved)
    return True


def on_locale_changed(listener: Callable[[str], None]) -> None:
    _listeners.append(listener)


def remove_locale_listener(listener: Callable[[str], None]) -> None:
    if listener in _listeners:
        _listeners.remove(listener)


def reset_locale_state() -> None:
    """Restore the process-wide default; tests use this between cases."""
    global _locale
    _locale = SOURCE_LOCALE
    _listeners.clear()
    _reported_missing.clear()


def translate(key: str) -> str:
    """The text for `key` in the active locale, falling back to the source.

    Never raises: a damaged or incomplete deployment degrades to English and,
    failing that, to a visible diagnostic placeholder, because an exception here
    would reach a paint or signal handler.
    """
    return translate_in(_locale, key)


def translate_in(locale: str, key: str) -> str:
    resolved = _lookup(locale, key)
    if resolved is not None:
        return resolved
    if locale != SOURCE_LOCALE:
        source = _lookup(SOURCE_LOCALE, key)
        if source is not None:
            _report_fallback(locale, key)
            return source
    _report_fallback(locale, key)
    return f"⟨{key}⟩"


def render(key: str, **params: object) -> str:
    """Translate `key` and substitute `params`; no params means no substitution.

    Several catalog entries show literal brace tokens to the operator — the
    recording filename placeholders, for instance — so formatting only happens
    when the caller actually supplies values.
    """
    text = translate(key)
    return text.format(**params) if params else text


def _report_fallback(locale: str, key: str) -> None:
    """Record each missing key once so a per-frame path cannot flood the log."""
    marker = (locale, key)
    if marker in _reported_missing:
        return
    _reported_missing.add(marker)


def fallback_diagnostics() -> tuple[tuple[str, str], ...]:
    """Every (locale, key) that has fallen back, each reported once."""
    return tuple(sorted(_reported_missing))
