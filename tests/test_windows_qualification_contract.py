from pathlib import Path

ROOT = Path(__file__).parents[1]
RUNNER = ROOT / "scripts" / "qualify-windows.ps1"
DOC = ROOT / "docs" / "windows-qualification.md"


def test_windows_runner_exposes_isolated_binary_first_contract() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    for token in (
        "ExecutablePath",
        "BuildMetadataPath",
        "PEAKLIVE_DATA_DIR",
        "Get-FileHash",
        "summary.json",
        "report.md",
        "NotRun",
        "HW-001",
        "FIX-001",
        "UI-001",
    ):
        assert token in text


def test_windows_qualification_document_preserves_safety_boundaries() -> None:
    text = DOC.read_text(encoding="utf-8")
    for phrase in (
        "mismatch",
        "hard failure",
        "NotRun",
        "passive",
        "listen-only",
        "must not transmit frames",
        "artifacts/windows-qualification",
    ):
        assert phrase in text


def test_ci_build_record_is_pinned_to_expected_binary() -> None:
    text = (ROOT / "docs" / "windows-ci-build-under-test.md").read_text(encoding="utf-8")
    assert "0.1.2+b202609071506" in text
    assert "E8E062387148A890AAB7FAE107D2A45F0F38269188CB36D789E7EF0FD28D4C21" in text
