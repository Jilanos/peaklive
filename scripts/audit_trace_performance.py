"""Measure and gate the complete trace preparation lifecycle (item_130).

Ordinary use, bounded and safe for CI (the default `CAPTURE_PROFILES`):

    QT_QPA_PLATFORM=offscreen uv run python scripts/audit_trace_performance.py

Qualification use, at the operator's measured density (item_134) - NOT run in
ordinary CI; each qualification case can take minutes and gigabytes of temp
disk:

    QT_QPA_PLATFORM=offscreen uv run python scripts/audit_trace_performance.py \\
        --qualify --signals 1 8 16 --deadline-s 1800

Everything measured is generated on the spot from `peaklive.analysis.benchmark`,
so the numbers are reproducible and no recorded capture has to be committed.

Unlike the profiler this replaces, the exit code is a verdict, not a courtesy:
it is nonzero whenever any measured case timed out, the replay did not reach
a truthful ready state, the accepted frame count did not match the source, or
(only with `--enforce-budgets`) a stage exceeded its budget. Product stage
budgets and this harness's own environment-tolerance margins are kept
distinct; `--enforce-budgets` checks the former.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from PySide6.QtCore import QCoreApplication, QDeadlineTimer, QElapsedTimer
from PySide6.QtWidgets import QApplication

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis.benchmark import (
    CAPTURE_PROFILES,
    QUALIFICATION_PROFILES,
    CaptureProfile,
    synthetic_dbc,
    write_synthetic_capture,
)
from peaklive.analysis.profiling import PROFILER, RESPONSIVENESS_BUDGET_S, StageProfile
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow

#: How long one measured case may run before it is judged timed out.
DEFAULT_DEADLINE_S = 600.0

#: Selected-signal counts the request's matrix asks for by default.
DEFAULT_SIGNAL_COUNTS = (0, 1, 8, 16)


@dataclass(frozen=True, slots=True)
class LifecycleResult:
    """One measured case's complete outcome, evidence attached."""

    label: str
    frames: int
    signals: int
    expected_frames: int
    accepted_frames: int
    timed_out: bool
    history_failed: bool
    history_failure_message: str
    first_data_s: float | None
    ready_s: float | None
    wall_s: float
    slowest_tick_s: float
    profile: StageProfile

    @property
    def ok(self) -> bool:
        """Whether this case is a truthful, complete, on-time success."""
        return (
            not self.timed_out
            and not self.history_failed
            and self.accepted_frames == self.expected_frames
            and self.ready_s is not None
        )

    def failure_reason(self) -> str:
        if self.timed_out:
            return "timed out before reaching a ready state"
        if self.history_failed:
            return f"historical persistence failed: {self.history_failure_message}"
        if self.accepted_frames != self.expected_frames:
            return f"accepted {self.accepted_frames} of {self.expected_frames} source frames"
        if self.ready_s is None:
            return "never reached a ready state"
        return ""


def measure(
    capture_profile: CaptureProfile,
    signal_count: int,
    workspace: Path,
    deadline_s: float,
) -> LifecycleResult:
    """Replay one synthetic capture end to end and return its full lifecycle."""
    capture = write_synthetic_capture(
        workspace / f"{capture_profile.name}-{signal_count}.asc", capture_profile
    )
    dbc = workspace / f"{capture_profile.name}-{signal_count}.dbc"
    dbc.write_text(synthetic_dbc(capture_profile.message_count), encoding="utf-8")

    window = MainWindow(
        ProfileStore(workspace / f"settings-{capture_profile.name}-{signal_count}"),
        FakeCanAdapter,
    )
    window._load_dbc_path(dbc)
    window._selected_signal_names = set(window._catalog.signal_names()[:signal_count])
    window._sync_graphs()

    PROFILER.reset()
    PROFILER.enabled = True
    wall = QElapsedTimer()
    tick = QElapsedTimer()
    slowest_tick = 0.0
    first_data_s: float | None = None
    ready_s: float | None = None
    try:
        wall.start()
        window._open_trace(capture)
        deadline = QDeadlineTimer(int(deadline_s * 1000))
        while window._replay_worker is not None and not deadline.hasExpired():
            tick.restart()
            QCoreApplication.processEvents()
            slowest_tick = max(slowest_tick, tick.nsecsElapsed() / 1e9)
            if first_data_s is None and len(window._trace):
                first_data_s = wall.nsecsElapsed() / 1e9
        parsed = window._replay_worker is None
        # Parsing/decoding finishing is not "ready": the background writer
        # (item_133) may still be draining already-accepted batches.
        while parsed and not window._historical_view_ready and not deadline.hasExpired():
            tick.restart()
            QCoreApplication.processEvents()
            slowest_tick = max(slowest_tick, tick.nsecsElapsed() / 1e9)
        timed_out = not (parsed and window._historical_view_ready)
        if not timed_out:
            ready_s = wall.nsecsElapsed() / 1e9
        wall_s = wall.nsecsElapsed() / 1e9
        measured = PROFILER.profile()
        accepted_frames = window._facts._frames
        history_failed = window._history_failed
        history_failure_message = window._history_failure_message or ""
    finally:
        PROFILER.enabled = False
        window.close()
    return LifecycleResult(
        label=f"{capture_profile.name} ({signal_count} signal(s))",
        frames=capture_profile.frames,
        signals=signal_count,
        expected_frames=capture_profile.frames,
        accepted_frames=accepted_frames,
        timed_out=timed_out,
        history_failed=history_failed,
        history_failure_message=history_failure_message,
        first_data_s=first_data_s,
        ready_s=ready_s,
        wall_s=wall_s,
        slowest_tick_s=slowest_tick,
        profile=measured,
    )


def _report(result: LifecycleResult, *, enforce_budgets: bool) -> list[str]:
    lines = [f"== {result.label}: {result.frames} frames =="]
    lines.append(result.profile.render())
    lines.append(f"Wall clock: {result.wall_s:.3f} s")
    if result.first_data_s is not None:
        lines.append(f"First data: {result.first_data_s:.3f} s")
    if result.ready_s is not None:
        lines.append(f"Ready: {result.ready_s:.3f} s")
    lines.append(f"Slowest event-loop tick: {result.slowest_tick_s * 1000:.1f} ms")
    lines.append(f"Responsiveness budget: {RESPONSIVENESS_BUDGET_S * 1000:.0f} ms")
    lines.append(f"Accepted frames: {result.accepted_frames}/{result.expected_frames}")
    overruns = result.profile.overruns()
    for stage, value, budget in overruns:
        marker = "OVER BUDGET" if enforce_budgets else "over budget (diagnostic only)"
        lines.append(f"{marker} {stage}: {value:.3f}s/1k frames > {budget:.3f}s/1k frames")
    if not result.ok:
        lines.append(f"FAILED: {result.failure_reason()}")
    lines.append("")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        action="append",
        choices=[item.name for item in CAPTURE_PROFILES],
        help="measure only this volume; repeatable (default: all of CAPTURE_PROFILES)",
    )
    parser.add_argument(
        "--signals",
        type=int,
        nargs="+",
        default=list(DEFAULT_SIGNAL_COUNTS),
        help="selected-signal counts to measure (default: 0 1 8 16)",
    )
    parser.add_argument(
        "--qualify",
        action="store_true",
        help="measure QUALIFICATION_PROFILES (typical/fifty-minute, operator density) "
        "instead of CAPTURE_PROFILES - large; not for routine CI",
    )
    parser.add_argument(
        "--deadline-s",
        type=float,
        default=DEFAULT_DEADLINE_S,
        help=f"per-case timeout in seconds (default: {DEFAULT_DEADLINE_S:.0f})",
    )
    parser.add_argument(
        "--enforce-budgets",
        action="store_true",
        help="also fail if a stage exceeds its product budget "
        "(off by default: budgets are a regression alarm, not this harness's gate)",
    )
    arguments = parser.parse_args(argv)

    available = QUALIFICATION_PROFILES if arguments.qualify else CAPTURE_PROFILES
    wanted = [
        item
        for item in available
        if arguments.qualify or arguments.profile is None or item.name in arguments.profile
    ]

    QApplication.instance() or QApplication([])
    failures: list[LifecycleResult] = []
    with TemporaryDirectory() as directory:
        workspace = Path(directory)
        for capture_profile in wanted:
            for signal_count in arguments.signals:
                result = measure(capture_profile, signal_count, workspace, arguments.deadline_s)
                for line in _report(result, enforce_budgets=arguments.enforce_budgets):
                    print(line)
                if not result.ok:
                    failures.append(result)
                elif arguments.enforce_budgets and result.profile.overruns():
                    failures.append(result)

    if failures:
        print(f"{len(failures)} of {len(wanted) * len(arguments.signals)} case(s) failed.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
