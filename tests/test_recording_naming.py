from datetime import datetime

import pytest

from peaklive.domain import RecordingSettings
from peaklive.recording import InvalidTemplateError, RecordingNaming


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
