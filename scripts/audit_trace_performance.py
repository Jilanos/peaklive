"""Measure the trace loading critical path and report the dominant stage.

Run it from the repository root::

    QT_QPA_PLATFORM=offscreen uv run python scripts/audit_trace_performance.py

Everything it measures is generated on the spot from
`peaklive.analysis.benchmark`, so the numbers are reproducible and no recorded
capture has to be committed. The output is the table published in
`docs/trace-performance-audit.md`; rerun it after touching the ingest path and
compare, rather than trusting a summary.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from PySide6.QtCore import QCoreApplication, QDeadlineTimer, QElapsedTimer
from PySide6.QtWidgets import QApplication

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis.benchmark import (
    CAPTURE_PROFILES,
    CaptureProfile,
    synthetic_dbc,
    write_synthetic_capture,
)
from peaklive.analysis.profiling import (
    PROFILER,
    RESPONSIVENESS_BUDGET_S,
    StageProfile,
)
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow

#: How long one measured replay may take before the audit gives up on it.
REPLAY_DEADLINE_MS = 600_000


def measure(profile: CaptureProfile, workspace: Path) -> tuple[StageProfile, float, float]:
    """Replay one synthetic capture and return its profile and responsiveness."""
    capture = write_synthetic_capture(workspace / f"{profile.name}.asc", profile)
    dbc = workspace / "synthetic.dbc"
    dbc.write_text(synthetic_dbc(profile.message_count), encoding="utf-8")

    window = MainWindow(ProfileStore(workspace / f"settings-{profile.name}"), FakeCanAdapter)
    window._load_dbc_path(dbc)
    PROFILER.reset()
    PROFILER.enabled = True
    wall = QElapsedTimer()
    slowest_tick = 0.0
    tick = QElapsedTimer()
    try:
        wall.start()
        window._open_trace(capture)
        deadline = QDeadlineTimer(REPLAY_DEADLINE_MS)
        while window._replay_worker is not None and not deadline.hasExpired():
            tick.restart()
            QCoreApplication.processEvents()
            slowest_tick = max(slowest_tick, tick.nsecsElapsed() / 1e9)
        elapsed = wall.nsecsElapsed() / 1e9
        measured = PROFILER.profile()
    finally:
        PROFILER.enabled = False
        window.close()
    return measured, elapsed, slowest_tick


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        action="append",
        choices=[item.name for item in CAPTURE_PROFILES],
        help="measure only this volume; repeatable (default: all)",
    )
    arguments = parser.parse_args(argv)
    wanted = [
        item
        for item in CAPTURE_PROFILES
        if arguments.profile is None or item.name in arguments.profile
    ]

    QApplication.instance() or QApplication([])
    with TemporaryDirectory() as directory:
        workspace = Path(directory)
        for profile in wanted:
            measured, elapsed, slowest_tick = measure(profile, workspace)
            print(f"== {profile.name}: {profile.frames} frames ==")
            print(measured.render())
            print(f"Wall clock: {elapsed:.3f} s")
            print(f"Slowest event-loop tick: {slowest_tick * 1000:.1f} ms")
            print(f"Responsiveness budget: {RESPONSIVENESS_BUDGET_S * 1000:.0f} ms")
            for stage, value, budget in measured.overruns():
                print(f"OVER BUDGET {stage}: {value:.3f}s/1k frames > {budget:.3f}s/1k frames")
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
