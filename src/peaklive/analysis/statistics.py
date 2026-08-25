"""Bounded range statistics and value distributions for cursor measurements."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import sqrt
from typing import Any

from peaklive.analysis.series import SignalSeries


@dataclass(frozen=True, slots=True)
class RangeStatistics:
    """A/B range synthesis for one signal over a bounded sample window."""

    count: int
    minimum: float | None = None
    maximum: float | None = None
    mean: float | None = None
    std: float | None = None
    rms: float | None = None
    distribution: tuple[tuple[str, int], ...] = ()

    @property
    def is_numeric(self) -> bool:
        return self.mean is not None

    @property
    def distribution_text(self) -> str:
        return ", ".join(f"{value}x{count}" for value, count in self.distribution)


def range_statistics(series: SignalSeries, start: float, end: float) -> RangeStatistics:
    """Summarize the samples inside [start, end], never loading more than that."""
    _, values = series.slice(start, end)
    if not values:
        return RangeStatistics(0)
    numeric = [float(value) for value in values if _is_numeric(value)]
    if not numeric:
        return RangeStatistics(len(values), distribution=value_distribution(values))
    count = len(numeric)
    mean = sum(numeric) / count
    variance = sum((value - mean) ** 2 for value in numeric) / count
    quadratic = sum(value * value for value in numeric) / count
    return RangeStatistics(
        count=count,
        minimum=min(numeric),
        maximum=max(numeric),
        mean=mean,
        std=sqrt(variance),
        rms=sqrt(quadratic),
    )


def value_distribution(values: list[Any], limit: int = 8) -> tuple[tuple[str, int], ...]:
    """Return the most frequent textual values, bounded to keep the table dense."""
    counter = Counter(str(value) for value in values)
    return tuple(counter.most_common(limit))


def cursor_value(series: SignalSeries, position: float) -> tuple[float, Any] | None:
    """Return the sample nearest to a cursor, or None when the series is empty."""
    return series.nearest(position)


def numeric_delta(first: Any, second: Any) -> float | None:
    """Return second - first when both cursor samples are numeric."""
    if _is_numeric(first) and _is_numeric(second):
        return float(second) - float(first)
    return None


def _is_numeric(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)
