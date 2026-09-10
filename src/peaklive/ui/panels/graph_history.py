"""Viewport selection helpers for source-backed historical graph data."""

from __future__ import annotations

from peaklive.analysis import HistoricalSignalStore, SeriesStore


def historical_extent(
    history: HistoricalSignalStore | None,
    fallback: tuple[float, float] | None,
) -> tuple[float, float] | None:
    return history.bounds() if history is not None else fallback


def viewport(
    history: HistoricalSignalStore | None,
    fallback: tuple[float, float] | None,
    chosen: bool,
    current: tuple[float, float] | None,
) -> tuple[tuple[float, float] | None, tuple[float, float] | None]:
    extent = historical_extent(history, fallback) or fallback
    return extent, (current if chosen else None) or extent


def historical_points(
    history: HistoricalSignalStore | None,
    signal: str,
    extent: tuple[float, float] | None,
    visible: tuple[float, float] | None,
    *,
    exact_threshold: float = 0.08,
) -> tuple[tuple[float, object], ...] | None:
    if history is None or extent is None or visible is None:
        return None
    full_span = max(0.0, extent[1] - extent[0])
    visible_span = max(0.0, visible[1] - visible[0])
    if full_span > 0 and visible_span / full_span <= exact_threshold:
        exact = history.exact(signal, *visible, limit=20_000)
        if exact:
            return exact
    return history.overview(signal, *visible, max_points=4_000)


def curve_points(
    history: HistoricalSignalStore | None,
    store: SeriesStore,
    signal: str,
    extent: tuple[float, float] | None,
    visible: tuple[float, float] | None,
) -> tuple[list[float], list[float]] | None:
    points = historical_points(history, signal, extent, visible)
    if points is None:
        series = store.series(signal)
        if series is None or not len(series):
            return None
        return series.times, series.numeric_values
    if not points:
        return None
    times = [timestamp for timestamp, _ in points]
    values = [
        float(value) if isinstance(value, int | float) and not isinstance(value, bool) else 0.0
        for _, value in points
    ]
    return times, values
