from peaklive.analysis.series import SeriesStore, SignalSeries


def test_series_stays_bounded_and_keeps_the_newest_samples():
    series = SignalSeries(capacity=3)
    for index in range(10):
        series.append(float(index), float(index))

    assert len(series) == 3
    assert series.times == [7.0, 8.0, 9.0]
    assert series.numeric_values == [7.0, 8.0, 9.0]
    assert series.bounds == (7.0, 9.0)


def test_series_nearest_snaps_to_the_closest_sample():
    series = SignalSeries()
    for timestamp, value in ((0.0, 1.0), (1.0, 2.0), (2.0, 3.0)):
        series.append(timestamp, value)

    assert series.nearest(-5.0) == (0.0, 1.0)
    assert series.nearest(0.4) == (0.0, 1.0)
    assert series.nearest(0.6) == (1.0, 2.0)
    assert series.nearest(99.0) == (2.0, 3.0)
    assert SignalSeries().nearest(0.0) is None


def test_series_slice_is_inclusive_and_order_independent():
    series = SignalSeries()
    for index in range(5):
        series.append(float(index), float(index) * 10)

    times, values = series.slice(1.0, 3.0)
    assert times == [1.0, 2.0, 3.0]
    assert values == [10.0, 20.0, 30.0]
    assert series.slice(3.0, 1.0) == (times, values)


def test_series_keeps_textual_samples_and_reports_them_as_non_numeric():
    series = SignalSeries()
    series.append(0.0, "Closed")
    series.append(1.0, "Open")

    assert not series.is_numeric
    assert series.values == ["Closed", "Open"]
    assert series.numeric_values == [0.0, 0.0]


def test_store_anchors_every_series_on_a_shared_origin():
    store = SeriesStore()

    assert store.append("A", 100.0, 1.0) == 0.0
    assert store.append("B", 100.5, 2.0) == 0.5
    assert store.origin == 100.0
    assert store.bounds() == (0.0, 0.5)

    store.drop("A")
    store.drop("B")
    assert store.origin is None
    assert store.bounds() is None
