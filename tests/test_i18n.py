"""The bilingual catalogs and the locale-aware lookup behind them."""

from __future__ import annotations

import json
from string import Formatter

import pytest

from peaklive.i18n import (
    LOCALE_AUTONYMS,
    SOURCE_LOCALE,
    SUPPORTED_LOCALES,
    catalog_entries,
    catalog_keys,
    catalog_path,
    current_locale,
    fallback_diagnostics,
    has_key,
    normalize_locale,
    render,
    set_locale,
    translate,
    translate_in,
)

#: Entries whose French is deliberately identical to their English. Every one is
#: either a product or protocol name (PeakLive, CAN, DBC, RX, bus off), a unit or
#: format token, or a word French and English genuinely share (Signal, Message,
#: Format, Visible, Standard, Destination, Trace). Nothing here is untranslated
#: prose; a new entry must be justified on that basis before it is added.
TECHNICAL_LITERALS = {
    "app.title",
    "app.build_label",
    "acquisition.bitrate_value",
    "bus.label",
    "bus.bus_off",
    "workspace.trace",
    "dbc.menu",
    "dbc.conflict_entry",
    "signals.summary_column_signal",
    "signals.summary_unavailable",
    "signals.column_signal",
    "graph.cursor_summary",
    "graph.cursor_unset",
    "measure.column_signal",
    "measure.column_a",
    "measure.column_b",
    "measure.column_delta",
    "measure.column_count",
    "measure.column_min",
    "measure.column_max",
    "measure.column_rms",
    "trace.filter_id",
    "trace.filter_message",
    "trace.filter_signal",
    "trace.column_id",
    "trace.column_dlc",
    "trace.column_message",
    "trace.direction_rx",
    "trace.direction_event",
    "columns.visible",
    "columns.format",
    "inspector.dlc",
    "inspector.standard",
    "inspector.message",
    "inspector.event_message",
    "export.format",
    "export.format_csv",
    "export.format_parquet",
    "export.destination",
    "recording.capture_format_asc",
    "recording.preview_invalid",
    "report.field_source",
    "report.section_anomalies",
}


def _placeholders(text: str) -> list[tuple[str, str]]:
    return sorted(
        (field, spec or "") for _, field, spec, _ in Formatter().parse(text) if field is not None
    )


def test_every_supported_locale_ships_a_catalog():
    for locale in SUPPORTED_LOCALES:
        assert catalog_path(locale).exists(), locale
    assert SOURCE_LOCALE in SUPPORTED_LOCALES
    assert set(LOCALE_AUTONYMS) == set(SUPPORTED_LOCALES)


def test_the_catalogs_have_identical_leaf_keys():
    reference = catalog_keys(SOURCE_LOCALE)

    assert reference
    for locale in SUPPORTED_LOCALES:
        assert catalog_keys(locale) == reference, locale


def test_every_entry_is_a_nonempty_string():
    for locale in SUPPORTED_LOCALES:
        empty = [
            key
            for key, value in catalog_entries(locale).items()
            if not isinstance(value, str) or not value.strip()
        ]
        assert empty == [], locale


def test_formatting_placeholders_and_specifications_match_across_locales():
    source = catalog_entries(SOURCE_LOCALE)

    for locale in SUPPORTED_LOCALES:
        entries = catalog_entries(locale)
        mismatched = {
            key
            for key, value in entries.items()
            if _placeholders(value) != _placeholders(source[key])
        }
        assert mismatched == set(), locale


def test_qt_progress_specifications_and_mnemonics_survive_translation():
    source = catalog_entries(SOURCE_LOCALE)

    for locale in SUPPORTED_LOCALES:
        for key, value in catalog_entries(locale).items():
            for token in ("%v", "%m", "%p"):
                assert (token in value) == (token in source[key]), (locale, key, token)
            # A command that offers a keyboard mnemonic in English has to offer
            # one in French too, or that command becomes unreachable by keyboard.
            assert ("&" in value) == ("&" in source[key]), (locale, key)


def test_mnemonics_stay_unique_within_each_menu():
    for locale in SUPPORTED_LOCALES:
        entries = catalog_entries(locale)
        menu_bar = [
            entries[key]
            for key in ("menu.file", "menu.recording", "menu.setup", "menu.view", "menu.help")
        ]
        letters = [text.split("&", 1)[1][0].casefold() for text in menu_bar]
        assert len(set(letters)) == len(letters), (locale, menu_bar)


def test_french_prose_is_translated_outside_the_reviewed_literal_allowlist():
    source = catalog_entries(SOURCE_LOCALE)
    french = catalog_entries("fr")

    untranslated = {key for key, value in french.items() if value == source[key]}

    assert untranslated <= TECHNICAL_LITERALS
    # Keep the allowlist honest: an entry that has since been translated must
    # be removed from it rather than left behind as permanent permission.
    assert TECHNICAL_LITERALS <= set(source)
    assert TECHNICAL_LITERALS - untranslated == set()


def test_the_catalogs_are_utf8_and_carry_their_accents():
    raw = catalog_path("fr").read_text(encoding="utf-8")

    assert json.loads(raw)
    assert "Événements" in raw
    assert "Débit" in raw


def test_translate_follows_the_selected_locale_both_ways():
    assert translate("acquisition.start") == "Start Acquisition"

    assert set_locale("fr") is True
    assert current_locale() == "fr"
    assert translate("acquisition.start") == "Démarrer l'acquisition"

    assert set_locale("en") is True
    assert translate("acquisition.start") == "Start Acquisition"


def test_selecting_the_active_locale_again_reports_no_change():
    assert set_locale("en") is False
    assert set_locale("fr") is True
    assert set_locale("fr") is False


def test_an_unknown_locale_falls_back_to_the_source_without_raising():
    assert normalize_locale("de") == SOURCE_LOCALE
    assert normalize_locale(None) == SOURCE_LOCALE
    assert normalize_locale(17) == SOURCE_LOCALE

    set_locale("de")

    assert current_locale() == SOURCE_LOCALE
    assert translate("workspace.signals") == "Signals"


def test_a_key_missing_from_one_catalog_falls_back_to_the_english_source():
    assert translate_in("fr", "acquisition.start") == "Démarrer l'acquisition"
    # A catalog that does not exist is a damaged deployment, not a crash.
    assert translate_in("xx", "acquisition.start") == "Start Acquisition"


def test_a_key_missing_from_both_catalogs_is_visible_but_never_raises():
    rendered = translate("nothing.defines.this")

    assert "nothing.defines.this" in rendered
    assert not has_key("nothing.defines.this")
    assert has_key("acquisition.start")
    # The placeholder must survive the ordinary formatting a caller applies.
    assert "nothing.defines.this" in rendered.format(anything=1)


def test_fallback_diagnostics_report_each_missing_key_once():
    for _ in range(50):
        translate("nothing.defines.this")
        translate_in("fr", "also.missing")

    reported = fallback_diagnostics()

    assert sorted({key for _, key in reported}) == ["also.missing", "nothing.defines.this"]
    assert len(reported) == len({(locale, key) for locale, key in reported})


def test_render_substitutes_only_when_parameters_are_supplied():
    assert render("app.build_label", identifier="1.2.3") == "v1.2.3"
    # Entries that show literal brace tokens to the operator must come back
    # untouched; formatting them would raise or eat the tokens.
    assert "{iteration:03d}" in render("recording.template_tooltip")


@pytest.mark.parametrize("locale", SUPPORTED_LOCALES)
def test_every_catalog_entry_resolves_in_every_locale(locale: str):
    set_locale(locale)

    assert all(translate(key) for key in catalog_keys(SOURCE_LOCALE))
