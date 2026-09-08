import json
from pathlib import Path

from peaklive.qualification import QualificationMetrics


def test_metrics_are_aggregate_only_and_rate_limited(tmp_path: Path) -> None:
    path = tmp_path / "metrics.jsonl"
    metrics = QualificationMetrics(path, interval=60)
    metrics.record(state="running", frames=12, events=2, errors=1, force=True)
    metrics.record(frames=8, events=1)
    metrics.close("stopped")

    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert [row["frames"] for row in rows] == [12, 20]
    assert rows[-1]["state"] == "stopped"
    assert set(rows[-1]) == {"elapsed_s", "state", "frames", "events", "errors"}
    assert all("payload" not in row and "arbitration_id" not in row for row in rows)


def test_metrics_require_explicit_environment(monkeypatch) -> None:
    monkeypatch.delenv("PEAKLIVE_QUALIFICATION_METRICS", raising=False)
    assert QualificationMetrics.from_environment() is None
