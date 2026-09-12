from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_vehicle_runner_is_hard_limited_and_receive_only() -> None:
    text = (ROOT / "scripts" / "vehicle-test-10m.ps1").read_text(encoding="utf-8")
    assert "FromMinutes(10)" in text
    assert "duration_limit_seconds=600" in text
    assert "passive listen-only; no transmit" in text
    assert "Measure-LiveHealth" in text
    assert "Process.Responding" in text
    assert "frames_delta" in text
    assert "V10-009" in text


def test_vehicle_runbook_has_a_ten_minute_budget_and_safe_outcome() -> None:
    text = (ROOT / "docs" / "vehicle-test-10m.md").read_text(encoding="utf-8")
    assert "600 secondes" in text
    assert "réception passive" in text
    assert "NotRun" in text
    assert "9:00–10:00" in text
