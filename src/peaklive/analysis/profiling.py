"""Stage-level timing for the trace loading critical path.

Opening a capture spends its time in seven distinct stages, and only a
measurement can say which one dominates. The profiler exists so that question
is answered by evidence rather than by intuition, and it is disabled by
default: an inactive stage costs one attribute read and returns a shared
no-op context, so the instrumentation can stay on the hot path in production
builds without paying for itself.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from time import perf_counter
from typing import TypeVar

STAGE_PARSE = "parse"
STAGE_DISPATCH = "dispatch"
STAGE_DECODE = "decode"
STAGE_TRACE_PROJECTION = "trace_projection"
STAGE_SERIES_PROJECTION = "series_projection"
STAGE_GRAPH_REFRESH = "graph_refresh"
STAGE_REPORT_REFRESH = "report_refresh"

#: Every stage the audit reports on, in the order a frame passes through them.
STAGES: tuple[str, ...] = (
    STAGE_PARSE,
    STAGE_DISPATCH,
    STAGE_DECODE,
    STAGE_TRACE_PROJECTION,
    STAGE_SERIES_PROJECTION,
    STAGE_GRAPH_REFRESH,
    STAGE_REPORT_REFRESH,
)

#: Seconds one stage may spend per thousand ingested frames.
#:
#: These are deliberately generous relative to the measured profile recorded in
#: `docs/trace-performance-audit.md`: a budget is a regression alarm, not a
#: benchmark score, and it has to hold on the slowest CI runner as well as on a
#: developer machine.
STAGE_BUDGETS_PER_1K_FRAMES: dict[str, float] = {
    STAGE_PARSE: 0.040,
    STAGE_DISPATCH: 0.020,
    STAGE_DECODE: 0.030,
    STAGE_TRACE_PROJECTION: 0.150,
    STAGE_SERIES_PROJECTION: 0.010,
    STAGE_GRAPH_REFRESH: 0.030,
    STAGE_REPORT_REFRESH: 0.010,
}

#: How long a user action or a cancellation may wait behind ingestion work.
RESPONSIVENESS_BUDGET_S = 0.25

# QElapsedTimer includes the platform scheduler boundary that wakes the test
# harness. Keep the product budget at 250 ms, while allowing a tiny measuring
# tolerance so a 25 microsecond timer quantisation artefact cannot fail CI.
RESPONSIVENESS_MEASUREMENT_TOLERANCE_S = 0.005

#: How many graph refreshes one coalescing window may perform. Ingestion
#: batches arrive far faster than a plot can usefully redraw, so the refresh
#: count must stay bounded by elapsed time rather than by batch count.
MAX_GRAPH_REFRESHES_PER_WINDOW = 1

T = TypeVar("T")

_INACTIVE = nullcontext()


@dataclass(frozen=True, slots=True)
class StageProfile:
    """One measured run: total seconds and entry count for every stage."""

    totals: dict[str, float]
    counts: dict[str, int]
    frames: int = 0

    @property
    def elapsed(self) -> float:
        return sum(self.totals.values())

    @property
    def dominant(self) -> str | None:
        """The stage that cost the most, or None when nothing was measured."""
        measured = {stage: total for stage, total in self.totals.items() if total > 0}
        if not measured:
            return None
        return max(measured, key=lambda stage: measured[stage])

    def share(self, stage: str) -> float:
        elapsed = self.elapsed
        return self.totals.get(stage, 0.0) / elapsed if elapsed > 0 else 0.0

    def per_1k_frames(self, stage: str) -> float:
        if self.frames <= 0:
            return 0.0
        return self.totals.get(stage, 0.0) * 1000 / self.frames

    def overruns(
        self, budgets: dict[str, float] | None = None
    ) -> tuple[tuple[str, float, float], ...]:
        """Return `(stage, measured, budget)` for every stage over its budget."""
        limits = STAGE_BUDGETS_PER_1K_FRAMES if budgets is None else budgets
        if self.frames <= 0:
            return ()
        return tuple(
            (stage, self.per_1k_frames(stage), budget)
            for stage, budget in limits.items()
            if self.per_1k_frames(stage) > budget
        )

    def render(self) -> str:
        """Render the profile as the plain text the audit script publishes."""
        lines = [
            f"Frames: {self.frames}",
            f"Total measured: {self.elapsed * 1000:.1f} ms",
            "",
            f"{'Stage':<20}{'Total ms':>10}{'Calls':>8}{'ms/1k':>10}{'Share':>8}",
        ]
        for stage in STAGES:
            lines.append(
                f"{stage:<20}"
                f"{self.totals.get(stage, 0.0) * 1000:>10.2f}"
                f"{self.counts.get(stage, 0):>8}"
                f"{self.per_1k_frames(stage) * 1000:>10.2f}"
                f"{self.share(stage) * 100:>7.1f}%"
            )
        lines.append("")
        lines.append(f"Dominant stage: {self.dominant or 'none measured'}")
        return "\n".join(lines) + "\n"


class StageProfiler:
    """Accumulates per-stage wall time, costing nothing while disabled."""

    __slots__ = ("_counts", "_frames", "_totals", "enabled")

    def __init__(self, *, enabled: bool = False) -> None:
        self.enabled = enabled
        self._totals: dict[str, float] = {}
        self._counts: dict[str, int] = {}
        self._frames = 0

    def reset(self) -> None:
        self._totals = {}
        self._counts = {}
        self._frames = 0

    @contextmanager
    def _measure(self, stage: str) -> Iterator[None]:
        started = perf_counter()
        try:
            yield
        finally:
            self.add(stage, perf_counter() - started)

    def stage(self, stage: str):
        """Time a block, or hand back a shared no-op when profiling is off."""
        if not self.enabled:
            return _INACTIVE
        return self._measure(stage)

    def add(self, stage: str, seconds: float) -> None:
        if not self.enabled:
            return
        self._totals[stage] = self._totals.get(stage, 0.0) + seconds
        self._counts[stage] = self._counts.get(stage, 0) + 1

    def count_frames(self, frames: int) -> None:
        if self.enabled:
            self._frames += frames

    def timed_iter(self, stage: str, source: Iterable[T]) -> Iterator[T]:
        """Attribute the time spent producing each item to `stage`.

        Wrapping is skipped entirely when profiling is off, so a streaming
        parser keeps its original iteration cost.
        """
        if not self.enabled:
            return iter(source)
        return self._timed_iter(stage, source)

    def _timed_iter(self, stage: str, source: Iterable[T]) -> Iterator[T]:
        iterator = iter(source)
        while True:
            started = perf_counter()
            try:
                item = next(iterator)
            except StopIteration:
                self.add(stage, perf_counter() - started)
                return
            self.add(stage, perf_counter() - started)
            yield item

    def profile(self) -> StageProfile:
        return StageProfile(dict(self._totals), dict(self._counts), self._frames)


#: The profiler the shipped ingestion path reports into.
PROFILER = StageProfiler()
