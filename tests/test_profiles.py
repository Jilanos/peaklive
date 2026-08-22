from peaklive.domain import ControllerMode, MeasurementProfile
from peaklive.services.profiles import ProfileState, ProfileStore


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
