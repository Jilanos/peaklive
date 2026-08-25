"""Bounded per-signal sample buffers shared by plots, statistics, and export."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections import deque
from collections.abc import Iterator
from typing import Any

DEFAULT_CAPACITY = 20_000


class SignalSeries:
    """A bounded, chronologically ordered sample buffer for one signal.

    Numeric samples feed the plots and the range statistics. Textual or
    enumerated samples are retained too so the measurement table can show a
    value distribution instead of meaningless arithmetic.
    """

    __slots__ = ("_capacity", "_times", "_unit", "_values")

    def __init__(self, capacity: int = DEFAULT_CAPACITY, unit: str | None = None) -> None:
        if capacity < 1:
            raise ValueError("A signal series needs room for at least one sample")
        self._capacity = capacity
        self._times: deque[float] = deque(maxlen=capacity)
        self._values: deque[Any] = deque(maxlen=capacity)
        self._unit = unit

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def unit(self) -> str | None:
        return self._unit

    def append(self, timestamp: float, value: Any) -> None:
        self._times.append(float(timestamp))
        self._values.append(value)

    def clear(self) -> None:
        self._times.clear()
        self._values.clear()

    def __len__(self) -> int:
        return len(self._times)

    @property
    def times(self) -> list[float]:
        return list(self._times)

    @property
    def values(self) -> list[Any]:
        return list(self._values)

    @property
    def numeric_values(self) -> list[float]:
        """Return plottable values, substituting 0.0 for non-numeric samples."""
        return [float(value) if _is_numeric(value) else 0.0 for value in self._values]

    @property
    def is_numeric(self) -> bool:
        return any(_is_numeric(value) for value in self._values)

    @property
    def bounds(self) -> tuple[float, float] | None:
        if not self._times:
            return None
        return self._times[0], self._times[-1]

    def nearest(self, target: float) -> tuple[float, Any] | None:
        """Return the sample closest to `target`, or None when the series is empty."""
        times = self.times
        if not times:
            return None
        index = bisect_left(times, target)
        if index == 0:
            best = 0
        elif index >= len(times):
            best = len(times) - 1
        else:
            before = times[index - 1]
            after = times[index]
            best = index - 1 if target - before <= after - target else index
        return times[best], self._values[best]

    def slice(self, start: float, end: float) -> tuple[list[float], list[Any]]:
        """Return the samples inside the inclusive [start, end] time range."""
        if start > end:
            start, end = end, start
        times = self.times
        values = self.values
        low = bisect_left(times, start)
        high = bisect_right(times, end)
        return times[low:high], values[low:high]

    def iter_samples(self) -> Iterator[tuple[float, Any]]:
        yield from zip(self.times, self.values, strict=True)


class SeriesStore:
    """A bounded collection of named signal series with a shared time origin."""

    def __init__(self, capacity: int = DEFAULT_CAPACITY) -> None:
        self._capacity = capacity
        self._series: dict[str, SignalSeries] = {}
        self._origin: float | None = None

    @property
    def origin(self) -> float | None:
        return self._origin

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._series)

    def series(self, name: str) -> SignalSeries | None:
        return self._series.get(name)

    def ensure(self, name: str, unit: str | None = None) -> SignalSeries:
        existing = self._series.get(name)
        if existing is None:
            existing = SignalSeries(self._capacity, unit)
            self._series[name] = existing
        return existing

    def append(self, name: str, timestamp: float, value: Any, unit: str | None = None) -> float:
        """Append one sample and return its origin-relative time."""
        if self._origin is None:
            self._origin = float(timestamp)
        relative = float(timestamp) - self._origin
        self.ensure(name, unit).append(relative, value)
        return relative

    def drop(self, name: str) -> None:
        self._series.pop(name, None)
        if not self._series:
            self._origin = None

    def clear(self) -> None:
        self._series.clear()
        self._origin = None

    def bounds(self) -> tuple[float, float] | None:
        """Return the time extent covering every retained series."""
        extents = [series.bounds for series in self._series.values()]
        known = [extent for extent in extents if extent is not None]
        if not known:
            return None
        return min(start for start, _ in known), max(end for _, end in known)


def _is_numeric(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)
