"""item_130: the trace-loading lifecycle harness must fail closed.

Before this fix, `scripts/audit_trace_performance.py::main` always returned 0
regardless of timeout, an incomplete replay, or a budget overrun - printing
"OVER BUDGET" lines while still reporting success. These tests prove the
rewritten harness's exit code is a real verdict, not a courtesy, and that it
now measures the previously-excluded history-write stage.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import sys
from pathlib import Path

import pytest

from peaklive.analysis.benchmark import SMALL
from peaklive.analysis.profiling import STAGE_HISTORY_WRITE, StageProfile

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "audit_trace_performance.py"


def _load_harness():
    spec = importlib.util.spec_from_file_location("audit_trace_performance", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def harness():
    return _load_harness()


def test_a_successful_small_case_measures_the_history_write_stage(harness, tmp_path, qtbot):
    result = harness.measure(SMALL, 1, tmp_path, deadline_s=60.0)

    assert result.ok
    assert result.accepted_frames == SMALL.frames
    assert result.ready_s is not None
    assert result.first_data_s is not None
    assert result.first_data_s <= result.ready_s
    assert result.profile.totals.get(STAGE_HISTORY_WRITE, 0.0) > 0


def test_main_exits_zero_for_a_successful_run(harness, qtbot):
    assert harness.main(["--profile", "small", "--signals", "0"]) == 0


def test_main_exits_nonzero_on_a_forced_timeout(harness, qtbot):
    code = harness.main(["--profile", "large", "--signals", "16", "--deadline-s", "0.001"])
    assert code != 0


def test_main_exits_nonzero_on_a_frame_count_mismatch(harness, monkeypatch, qtbot):
    """A source-derived accepted count below the expected total must fail
    the run even if the replay otherwise looked complete."""
    original = harness.measure

    def truncated(capture_profile, signal_count, workspace, deadline_s):
        result = original(capture_profile, signal_count, workspace, deadline_s)
        return dataclasses.replace(result, accepted_frames=result.accepted_frames - 1)

    monkeypatch.setattr(harness, "measure", truncated)
    assert harness.main(["--profile", "small", "--signals", "0"]) != 0


def test_main_exits_nonzero_when_history_persistence_fails(harness, monkeypatch, qtbot):
    """A contained historical-persistence failure (item_132/item_133) must
    still fail the harness, not just show up as a status message."""
    original = harness.measure

    def failed(capture_profile, signal_count, workspace, deadline_s):
        result = original(capture_profile, signal_count, workspace, deadline_s)
        return dataclasses.replace(
            result, history_failed=True, history_failure_message="synthetic"
        )

    monkeypatch.setattr(harness, "measure", failed)
    assert harness.main(["--profile", "small", "--signals", "0"]) != 0


def test_enforce_budgets_fails_only_when_asked(harness, monkeypatch, qtbot):
    """Budget overruns are a diagnostic by default; --enforce-budgets gates them."""
    original = harness.measure

    def slow(capture_profile, signal_count, workspace, deadline_s):
        result = original(capture_profile, signal_count, workspace, deadline_s)
        inflated = StageProfile(
            totals={**result.profile.totals, "parse": 1000.0},
            counts=result.profile.counts,
            frames=result.frames,
        )
        return dataclasses.replace(result, profile=inflated)

    monkeypatch.setattr(harness, "measure", slow)
    assert harness.main(["--profile", "small", "--signals", "0"]) == 0

    monkeypatch.setattr(harness, "measure", slow)
    assert harness.main(["--profile", "small", "--signals", "0", "--enforce-budgets"]) != 0


def test_qualification_profiles_use_the_operator_measured_density(harness):
    from peaklive.analysis.benchmark import LONG, TYPICAL

    assert TYPICAL.frames == 1_755_746
    assert LONG.frames == 5_575_042
    for profile in (TYPICAL, LONG):
        assert profile.frame_interval_s == pytest.approx(1.0 / 1858.347, rel=1e-3)
