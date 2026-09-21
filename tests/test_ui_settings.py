"""The application-scoped interface preference and its recovery behaviour."""

from __future__ import annotations

import json

import pytest

from peaklive.i18n import SOURCE_LOCALE, current_locale, set_locale
from peaklive.services.profiles import ProfileStore
from peaklive.services.ui_settings import SETTINGS_FILENAME, UiSettingsStore


def test_a_fresh_installation_starts_in_english(tmp_path):
    store = UiSettingsStore(tmp_path)

    assert not store.path.exists()
    assert store.load().locale == SOURCE_LOCALE


def test_the_selected_locale_survives_a_restart(tmp_path):
    UiSettingsStore(tmp_path).save_locale("fr")

    # A second store is what the next launch constructs.
    assert UiSettingsStore(tmp_path).load().locale == "fr"


def test_the_store_honours_the_data_directory_override(tmp_path, monkeypatch):
    monkeypatch.setenv("PEAKLIVE_DATA_DIR", str(tmp_path))

    store = UiSettingsStore()

    assert store.path == tmp_path / SETTINGS_FILENAME


def test_an_unknown_stored_locale_recovers_to_english(tmp_path):
    store = UiSettingsStore(tmp_path)
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_text(json.dumps({"locale": "de"}), encoding="utf-8")

    assert store.load().locale == SOURCE_LOCALE


@pytest.mark.parametrize("content", ["{not json", "[]", '"fr"', ""])
def test_malformed_settings_recover_to_english(tmp_path, content):
    store = UiSettingsStore(tmp_path)
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_text(content, encoding="utf-8")

    assert store.load().locale == SOURCE_LOCALE


def test_a_byte_order_mark_does_not_make_the_preference_unreadable(tmp_path):
    """Windows tooling adds one; the file is still perfectly good JSON."""
    store = UiSettingsStore(tmp_path)
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_bytes(b"\xef\xbb\xbf" + json.dumps({"locale": "fr"}).encode("utf-8"))

    assert store.load().locale == "fr"


def test_recovering_from_damaged_settings_leaves_measurement_setups_alone(tmp_path):
    profiles = ProfileStore(tmp_path)
    state = profiles.load()
    profiles.save(state)
    before = profiles.path.read_text(encoding="utf-8")
    settings = UiSettingsStore(tmp_path)
    settings.path.write_text("{ broken", encoding="utf-8")

    assert settings.load().locale == SOURCE_LOCALE
    assert profiles.path.read_text(encoding="utf-8") == before
    assert profiles.load().selected.name == state.selected.name


def test_saving_a_locale_preserves_settings_this_build_does_not_own(tmp_path):
    store = UiSettingsStore(tmp_path)
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_text(
        json.dumps({"locale": "en", "future_setting": {"kept": True}}), encoding="utf-8"
    )

    store.save_locale("fr")

    stored = json.loads(store.path.read_text(encoding="utf-8"))
    assert stored["locale"] == "fr"
    assert stored["future_setting"] == {"kept": True}


def test_an_unwritable_store_raises_rather_than_claiming_it_saved(tmp_path):
    store = UiSettingsStore(tmp_path / "settings")
    # A file where the directory must go: the write cannot succeed, and the
    # caller has to learn that rather than be told the choice was remembered.
    (tmp_path / "settings").write_text("not a directory", encoding="utf-8")

    with pytest.raises(OSError):
        store.save_locale("fr")


def test_a_failed_save_leaves_no_partial_file_behind(tmp_path, monkeypatch):
    store = UiSettingsStore(tmp_path)
    original = json.dumps

    def explode(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr("peaklive.services.ui_settings.json.dumps", explode)
    with pytest.raises(OSError):
        store.save_locale("fr")
    monkeypatch.setattr("peaklive.services.ui_settings.json.dumps", original)

    assert list(tmp_path.glob(f"{SETTINGS_FILENAME}*")) == []


def test_saving_an_unknown_locale_stores_the_source_locale(tmp_path):
    store = UiSettingsStore(tmp_path)

    store.save_locale("de")

    assert json.loads(store.path.read_text(encoding="utf-8"))["locale"] == SOURCE_LOCALE


def test_measurement_setups_never_carry_the_interface_language(tmp_path):
    """Language is an installation preference, not part of a vehicle setup."""
    profiles = ProfileStore(tmp_path)
    state = profiles.load()
    set_locale("fr")
    UiSettingsStore(tmp_path).save_locale("fr")

    copy = profiles.save_as(state, "Bench copy")
    stored = json.loads(profiles.path.read_text(encoding="utf-8"))

    assert copy.name == "Bench copy"
    assert "locale" not in json.dumps(stored)
    assert current_locale() == "fr"
    assert UiSettingsStore(tmp_path).load().locale == "fr"
