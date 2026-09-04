from datetime import datetime

import pytest

from peaklive.domain import DEFAULT_FILENAME_TEMPLATE, RecordingSettings
from peaklive.recording import (
    EMPTY_TEXT_COMPONENT,
    InvalidTemplateError,
    RecordingNaming,
    ReservationCancelledError,
    ReservationExhaustedError,
)


def _settings(tmp_path, **overrides):
    settings = RecordingSettings(directory=str(tmp_path))
    for name, value in overrides.items():
        setattr(settings, name, value)
    return settings


def test_preview_formats_every_documented_placeholder_without_touching_disk(tmp_path):
    naming = RecordingNaming()
    settings = _settings(
        tmp_path,
        filename_template="{date}_{time}_{profile}_{iteration:03d}_{segment:02d}",
        iteration=7,
    )

    filename = naming.preview(settings, "Vehicle Test", now=datetime(2026, 9, 3, 14, 5, 30))

    assert filename == "2026-09-03_14-05-30_Vehicle_Test_007_01.asc"
    assert not list(tmp_path.iterdir())


def test_preview_accepts_a_bare_numeric_width_without_the_d_type(tmp_path):
    naming = RecordingNaming()
    settings = _settings(tmp_path, filename_template="capture_{iteration:03}", iteration=5)

    filename = naming.preview(settings, "Bench", now=datetime(2026, 9, 3, 9, 0, 0))

    assert filename == "capture_005.asc"


@pytest.mark.parametrize(
    "template",
    [
        "",
        "   ",
        "{unknown}",
        "{profile:03d}",
        "{iteration:xyz}",
        "../{iteration}",
        "sub/dir_{iteration}",
        "back\\slash_{iteration}",
        "{iteration",
    ],
)
def test_malformed_or_unsafe_templates_are_rejected_with_an_actionable_message(tmp_path, template):
    naming = RecordingNaming()
    settings = _settings(tmp_path, filename_template=template)

    with pytest.raises(InvalidTemplateError):
        naming.preview(settings, "Bench", now=datetime(2026, 9, 3, 9, 0, 0))


def test_reserve_creates_a_marker_and_advances_the_next_iteration(tmp_path):
    naming = RecordingNaming()
    settings = _settings(tmp_path, filename_template="capture_{iteration:03d}", iteration=1)

    reservation = naming.reserve(settings, "Bench", now=datetime(2026, 9, 3, 9, 0, 0))

    assert reservation.iteration == 1
    assert reservation.next_iteration == 2
    assert reservation.marker_path.exists()
    assert reservation.final_path.name == "capture_001.asc"


def test_reserve_skips_existing_final_and_partial_files(tmp_path):
    naming = RecordingNaming()
    settings = _settings(tmp_path, filename_template="capture_{iteration:03d}", iteration=1)
    (tmp_path / "capture_001.asc").write_text("done", encoding="utf-8")
    (tmp_path / "capture_002.asc.partial").write_text("partial", encoding="utf-8")

    reservation = naming.reserve(settings, "Bench", now=datetime(2026, 9, 3, 9, 0, 0))

    assert reservation.iteration == 3
    assert reservation.final_path.name == "capture_003.asc"


def test_reserve_skips_a_stale_reservation_marker_left_by_a_crash(tmp_path):
    naming = RecordingNaming()
    settings = _settings(tmp_path, filename_template="capture_{iteration:03d}", iteration=1)
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "capture_001.asc.reserved").touch()

    reservation = naming.reserve(settings, "Bench", now=datetime(2026, 9, 3, 9, 0, 0))

    assert reservation.iteration == 2


def test_two_competing_reservations_never_claim_the_same_candidate(tmp_path):
    naming_a = RecordingNaming()
    naming_b = RecordingNaming()
    settings = _settings(tmp_path, filename_template="capture_{iteration:03d}", iteration=1)

    first = naming_a.reserve(settings, "Bench", now=datetime(2026, 9, 3, 9, 0, 0))
    second = naming_b.reserve(settings, "Bench", now=datetime(2026, 9, 3, 9, 0, 0))

    assert first.iteration != second.iteration
    assert {first.iteration, second.iteration} == {1, 2}


def test_release_frees_an_unused_reservation_for_a_later_search(tmp_path):
    naming = RecordingNaming()
    settings = _settings(tmp_path, filename_template="capture_{iteration:03d}", iteration=1)

    reservation = naming.reserve(settings, "Bench", now=datetime(2026, 9, 3, 9, 0, 0))
    reservation.release()

    assert not reservation.marker_path.exists()
    retried = naming.reserve(settings, "Bench", now=datetime(2026, 9, 3, 9, 0, 0))
    assert retried.iteration == 1


def test_reset_to_one_restarts_the_search_rather_than_permitting_an_overwrite(tmp_path):
    naming = RecordingNaming()
    settings = _settings(tmp_path, filename_template="capture_{iteration:03d}", iteration=1)
    (tmp_path / "capture_001.asc").write_text("evidence", encoding="utf-8")
    (tmp_path / "capture_002.asc").write_text("evidence", encoding="utf-8")

    settings.iteration = 1
    reservation = naming.reserve(settings, "Bench", now=datetime(2026, 9, 3, 9, 0, 0))

    assert reservation.iteration == 3
    assert (tmp_path / "capture_001.asc").read_text(encoding="utf-8") == "evidence"
    assert (tmp_path / "capture_002.asc").read_text(encoding="utf-8") == "evidence"


def test_the_default_template_carries_the_operator_text(tmp_path):
    naming = RecordingNaming()
    settings = _settings(tmp_path, text="roulage BL")

    filename = naming.preview(settings, "Vehicle Test", now=datetime(2026, 9, 3, 14, 5, 30))

    assert settings.filename_template == DEFAULT_FILENAME_TEMPLATE
    assert filename == "2026-09-03_14-05-30_Vehicle_Test_roulage_BL_001_001.asc"


@pytest.mark.parametrize(
    ("text", "component"),
    [
        ("roulage BL", "roulage_BL"),
        ("../../etc/passwd", "etc_passwd"),
        ("a:b*c?d", "a_b_c_d"),
        ("  spaced  ", "spaced"),
        ("", EMPTY_TEXT_COMPONENT),
        ("   ", EMPTY_TEXT_COMPONENT),
        ("///", EMPTY_TEXT_COMPONENT),
        ("...", EMPTY_TEXT_COMPONENT),
    ],
)
def test_text_is_sanitized_into_exactly_one_safe_component(tmp_path, text, component):
    naming = RecordingNaming()
    settings = _settings(tmp_path, filename_template="{text}", text=text)

    filename = naming.preview(settings, "Bench", now=datetime(2026, 9, 3, 9, 0, 0))

    assert filename == f"{component}.asc"


def test_text_does_not_accept_a_format_spec(tmp_path):
    naming = RecordingNaming()
    settings = _settings(tmp_path, filename_template="{text:03d}", text="bench")

    with pytest.raises(InvalidTemplateError):
        naming.preview(settings, "Bench", now=datetime(2026, 9, 3, 9, 0, 0))


def test_reservation_preview_and_sidecars_agree_on_the_text_basename(tmp_path):
    naming = RecordingNaming()
    settings = _settings(tmp_path, text="roulage BL")
    moment = datetime(2026, 9, 3, 14, 5, 30)

    expected = naming.preview(settings, "Bench", now=moment)
    reservation = naming.reserve(settings, "Bench", now=moment)

    assert reservation.final_path.name == expected
    assert reservation.partial_path.name == f"{expected}.partial"
    assert reservation.marker_path.name == f"{expected}.reserved"
    assert reservation.event_final_path.name.startswith(expected.removesuffix(".asc"))
    assert reservation.event_final_path.name.endswith(".peaklive-events.jsonl")
    assert "roulage_BL" in reservation.event_final_path.name


def test_changing_only_the_text_reserves_a_different_capture(tmp_path):
    naming = RecordingNaming()
    moment = datetime(2026, 9, 3, 14, 5, 30)
    first = naming.reserve(_settings(tmp_path, text="run A"), "Bench", now=moment)
    second = naming.reserve(_settings(tmp_path, text="run B"), "Bench", now=moment)

    assert first.final_path != second.final_path
    assert first.iteration == second.iteration == 1


def test_two_captures_with_the_same_text_never_collide(tmp_path):
    naming = RecordingNaming()
    moment = datetime(2026, 9, 3, 14, 5, 30)
    settings = _settings(tmp_path, text="run A")

    first = naming.reserve(settings, "Bench", now=moment)
    second = naming.reserve(settings, "Bench", now=moment)

    assert first.final_path != second.final_path
    assert second.iteration == first.iteration + 1


def test_a_repeated_non_discriminating_template_reserves_a_suffixed_path(tmp_path):
    naming = RecordingNaming()
    settings = _settings(tmp_path, filename_template="{profile}")
    (tmp_path / "Bench.asc").write_text("done", encoding="utf-8")

    reservation = naming.reserve(settings, "Bench", now=datetime(2026, 9, 3, 9, 0, 0))

    assert reservation.final_path.name == "Bench-2.asc"


def test_a_non_discriminating_template_fails_clearly_within_the_search_bound(
    tmp_path, monkeypatch
):
    naming = RecordingNaming()
    settings = _settings(tmp_path, filename_template="{profile}")

    def _always_taken(*args, **kwargs):
        raise FileExistsError

    monkeypatch.setattr("peaklive.recording.naming.os.open", _always_taken)

    with pytest.raises(ReservationExhaustedError):
        naming.reserve(settings, "Bench", now=datetime(2026, 9, 3, 9, 0, 0))


def test_stop_requested_cancels_reservation_before_a_candidate_is_claimed(tmp_path):
    naming = RecordingNaming()
    settings = _settings(tmp_path, filename_template="capture_{iteration:03d}", iteration=1)

    with pytest.raises(ReservationCancelledError):
        naming.reserve(
            settings,
            "Bench",
            now=datetime(2026, 9, 3, 9, 0, 0),
            stop_requested=lambda: True,
        )
    assert not list(tmp_path.iterdir()) or all(
        not path.name.endswith(".reserved") for path in tmp_path.iterdir()
    )


def test_stop_requested_does_not_interrupt_a_successful_reservation(tmp_path):
    naming = RecordingNaming()
    settings = _settings(tmp_path, filename_template="capture_{iteration:03d}", iteration=1)

    reservation = naming.reserve(
        settings,
        "Bench",
        now=datetime(2026, 9, 3, 9, 0, 0),
        stop_requested=lambda: False,
    )

    assert reservation.marker_path.exists()
