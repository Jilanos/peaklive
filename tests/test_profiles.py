import os
from pathlib import Path

import pytest

from peaklive.domain import ControllerMode, MeasurementProfile
from peaklive.services.profiles import ProfileNameError, ProfileState, ProfileStore


def test_profile_store_restores_last_selected_profile(tmp_path):
    store = ProfileStore(tmp_path)
    first = MeasurementProfile(name="Bench", bitrate=500_000)
    second = MeasurementProfile(
        name="Vehicle",
        bitrate=250_000,
        controller_mode=ControllerMode.NORMAL_RECEIVE,
        favorite_signals=["Powertrain.Speed"],
    )
    store.save(ProfileState([first, second], second.identifier))

    restored = store.load()

    assert restored.selected.name == "Vehicle"
    assert restored.selected.bitrate == 250_000
    assert restored.selected.controller_mode is ControllerMode.NORMAL_RECEIVE
    assert restored.selected.favorite_signals == ["Powertrain.Speed"]


def test_missing_store_has_passive_default_profile(tmp_path):
    profile = ProfileStore(tmp_path).load().selected

    assert profile.name == "Default measurement"
    assert profile.controller_mode is ControllerMode.PASSIVE_LISTEN_ONLY
    assert profile.recording.enabled is True


def test_missing_store_reports_no_recovery(tmp_path):
    assert ProfileStore(tmp_path).load().recovered_from is None


@pytest.mark.parametrize(
    "content",
    [
        "{not valid json",
        '{"profiles": [{"controller_mode": "not_a_real_mode"}]}',
        '{"profiles": [{"bitrate": "not_a_number"}]}',
        '{"profiles": "not_a_list"}',
    ],
)
def test_a_corrupt_or_invalid_store_starts_from_defaults_and_is_quarantined(tmp_path, content):
    store = ProfileStore(tmp_path)
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_text(content, encoding="utf-8")

    state = store.load()

    assert state.selected.name == "Default measurement"
    assert state.selected.controller_mode is ControllerMode.PASSIVE_LISTEN_ONLY
    assert not store.path.exists()
    assert state.recovered_from is not None
    assert state.recovered_from.exists()
    assert state.recovered_from.read_text(encoding="utf-8") == content
    assert state.recovered_from.name.startswith("profiles.json.corrupt-")


def test_save_as_persists_an_independent_copy_and_selects_it(tmp_path):
    store = ProfileStore(tmp_path)
    state = store.load()
    state.selected.dbc_paths.append("/bench/powertrain.dbc")
    state.selected.trace_filters["dbc_conflict_resolutions"] = {"256": "abc"}
    state.selected.recording.text = "roulage"

    copy = store.save_as(state, "  Vehicle bench  ")

    assert copy.name == "Vehicle bench"
    assert copy.identifier != state.profiles[0].identifier
    assert state.last_profile_id == copy.identifier

    reloaded = ProfileStore(tmp_path).load()
    assert [profile.name for profile in reloaded.profiles] == [
        "Default measurement",
        "Vehicle bench",
    ]
    assert reloaded.selected.name == "Vehicle bench"
    assert reloaded.selected.dbc_paths == ["/bench/powertrain.dbc"]
    assert reloaded.selected.recording.text == "roulage"


def test_a_saved_copy_carries_every_documented_configuration_field(tmp_path):
    store = ProfileStore(tmp_path)
    state = store.load()
    origin = state.selected
    origin.channel = "PCAN_USBBUS2"
    origin.bitrate = 250_000
    origin.controller_mode = ControllerMode.NORMAL_RECEIVE
    origin.dbc_paths = ["/bench/a.dbc", "/bench/b.dbc"]
    origin.displayed_signals = ["Powertrain.Speed"]
    origin.favorite_signals = ["Powertrain.Rpm"]
    origin.trace_filter.message = "Engine"
    origin.trace_columns[0].width = 321
    origin.layout.workspace_mode = "trace"
    origin.layout.panel_widths = {"signals": 400}
    origin.recording.text = "poc3"
    origin.recording.iteration = 12

    store.save_as(state, "Copy")
    copy = ProfileStore(tmp_path).load().selected

    assert copy.channel == "PCAN_USBBUS2"
    assert copy.bitrate == 250_000
    assert copy.controller_mode is ControllerMode.NORMAL_RECEIVE
    assert copy.dbc_paths == ["/bench/a.dbc", "/bench/b.dbc"]
    assert copy.displayed_signals == ["Powertrain.Speed"]
    assert copy.favorite_signals == ["Powertrain.Rpm"]
    assert copy.trace_filter.message == "Engine"
    assert copy.trace_columns[0].width == 321
    assert copy.layout.workspace_mode == "trace"
    assert copy.layout.panel_widths == {"signals": 400}
    assert copy.recording.text == "poc3"
    assert copy.recording.iteration == 12


def test_editing_one_setup_never_reaches_the_other(tmp_path):
    store = ProfileStore(tmp_path)
    state = store.load()
    origin = state.selected
    origin.dbc_paths = ["/bench/a.dbc"]
    origin.trace_filters["dbc_conflict_resolutions"] = {"256": "abc"}

    copy = store.save_as(state, "Copy")
    copy.dbc_paths.append("/bench/b.dbc")
    copy.favorite_signals.append("Powertrain.Rpm")
    copy.trace_columns[0].width = 250
    copy.layout.collapsed_panels.append("signals")
    copy.trace_filters["dbc_conflict_resolutions"]["512"] = "def"
    copy.recording.text = "copy only"
    store.save(state)

    restored = {profile.name: profile for profile in ProfileStore(tmp_path).load().profiles}
    original = restored["Default measurement"]
    assert original.dbc_paths == ["/bench/a.dbc"]
    assert original.favorite_signals == []
    assert original.trace_columns[0].width != 250
    assert original.layout.collapsed_panels == []
    assert original.trace_filters["dbc_conflict_resolutions"] == {"256": "abc"}
    assert original.recording.text == ""


def test_a_blank_or_duplicate_name_changes_nothing(tmp_path):
    store = ProfileStore(tmp_path)
    state = store.load()
    store.save(state)

    for rejected in ("", "   ", "Default measurement", "default MEASUREMENT"):
        with pytest.raises(ProfileNameError):
            store.save_as(state, rejected)

    assert len(state.profiles) == 1
    assert state.last_profile_id == state.profiles[0].identifier
    assert len(ProfileStore(tmp_path).load().profiles) == 1


def test_a_failed_write_rolls_the_copy_back_out_of_memory(tmp_path, monkeypatch):
    store = ProfileStore(tmp_path)
    state = store.load()
    store.save(state)
    original_id = state.last_profile_id

    def refuse(_state):
        raise OSError("disk full")

    monkeypatch.setattr(store, "save", refuse)
    with pytest.raises(OSError):
        store.save_as(state, "Copy")

    assert [profile.name for profile in state.profiles] == ["Default measurement"]
    assert state.last_profile_id == original_id
    assert len(ProfileStore(tmp_path).load().profiles) == 1


def test_two_saves_never_reuse_the_same_temporary_filename(tmp_path, monkeypatch):
    store = ProfileStore(tmp_path)
    state = store.load()
    seen: list[str] = []
    original_replace = Path.replace

    def spy_replace(self, target):
        seen.append(self.name)
        return original_replace(self, target)

    monkeypatch.setattr(Path, "replace", spy_replace)

    store.save(state)
    store.save(state)

    assert len(seen) == 2
    assert seen[0] != seen[1]


def test_save_flushes_and_fsyncs_before_replacing_the_store(tmp_path, monkeypatch):
    store = ProfileStore(tmp_path)
    state = store.load()
    order: list[str] = []
    original_fsync = os.fsync
    original_replace = Path.replace

    def spy_fsync(fd):
        order.append("fsync")
        return original_fsync(fd)

    def spy_replace(self, target):
        order.append("replace")
        return original_replace(self, target)

    monkeypatch.setattr(os, "fsync", spy_fsync)
    monkeypatch.setattr(Path, "replace", spy_replace)

    store.save(state)

    assert order == ["fsync", "replace"]


def test_a_failed_write_preserves_the_prior_readable_store(tmp_path, monkeypatch):
    store = ProfileStore(tmp_path)
    state = store.load()
    store.save(state)
    original_content = store.path.read_text(encoding="utf-8")

    state.selected.name = "Changed after the last durable save"

    def fail_fsync(fd):
        raise OSError("simulated fsync failure")

    monkeypatch.setattr(os, "fsync", fail_fsync)

    with pytest.raises(OSError):
        store.save(state)

    assert store.path.read_text(encoding="utf-8") == original_content
    assert ProfileStore(tmp_path).load().selected.name == "Default measurement"
    assert not list(tmp_path.glob("*.tmp"))


def test_each_saved_setup_reloads_its_own_configuration(tmp_path):
    store = ProfileStore(tmp_path)
    state = store.load()
    state.selected.bitrate = 125_000
    copy = store.save_as(state, "Second")
    copy.bitrate = 1_000_000
    store.save(state)

    restored = ProfileStore(tmp_path).load()
    by_name = {profile.name: profile for profile in restored.profiles}
    assert by_name["Default measurement"].bitrate == 125_000
    assert by_name["Second"].bitrate == 1_000_000
    assert restored.selected.name == "Second"
