from math import isclose

from peaklive.analysis.series import SignalSeries
from peaklive.analysis.statistics import (
    cursor_value,
    numeric_delta,
    range_statistics,
    value_distribution,
)


def _numeric_series() -> SignalSeries:
    series = SignalSeries()
    for timestamp, value in ((0.0, 2.0), (1.0, 4.0), (2.0, 4.0), (3.0, 4.0), (4.0, 6.0)):
        series.append(timestamp, value)
    return series


def test_range_statistics_match_the_known_series():
    stats = range_statistics(_numeric_series(), 0.0, 4.0)

    assert stats.count == 5
    assert stats.minimum == 2.0
    assert stats.maximum == 6.0
    assert isclose(stats.mean, 4.0)
    assert isclose(stats.std, 1.2649110640673518)
    assert isclose(stats.rms, 4.1952353926806065)
    assert stats.is_numeric


def test_range_statistics_only_cover_the_selected_window():
    stats = range_statistics(_numeric_series(), 1.0, 2.0)

    assert stats.count == 2
    assert stats.minimum == 4.0
    assert stats.maximum == 4.0
    assert stats.std == 0.0


def test_range_statistics_report_an_empty_window_rather_than_zero():
    stats = range_statistics(_numeric_series(), 10.0, 20.0)

    assert stats.count == 0
    assert stats.mean is None
    assert not stats.is_numeric


def test_range_statistics_fall_back_to_a_distribution_for_textual_signals():
    series = SignalSeries()
    for timestamp, value in ((0.0, "Closed"), (1.0, "Open"), (2.0, "Closed")):
        series.append(timestamp, value)

    stats = range_statistics(series, 0.0, 2.0)

    assert stats.count == 3
    assert stats.mean is None
    assert stats.distribution == (("Closed", 2), ("Open", 1))
    assert stats.distribution_text == "Closedx2, Openx1"


def test_value_distribution_is_bounded():
    values = [f"state-{index}" for index in range(20)]

    assert len(value_distribution(values, limit=5)) == 5


def test_cursor_value_and_delta():
    series = _numeric_series()

    assert cursor_value(series, 1.2) == (1.0, 4.0)
    assert numeric_delta(4.0, 6.0) == 2.0
    assert numeric_delta("Open", 6.0) is None
