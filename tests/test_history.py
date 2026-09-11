from peaklive.analysis.history import HistoricalSignalStore


def test_history_keeps_exact_samples_beyond_series_capacity(tmp_path):
    history = HistoricalSignalStore(tmp_path / "history.sqlite3")
    history.append_many(("speed", float(i), i % 100, "km/h") for i in range(25_000))

    assert history.signal_bounds("speed") == (0.0, 24_999.0)
    exact = history.exact("speed", 12_345, 12_350)
    assert exact == tuple((float(i), i % 100) for i in range(12_345, 12_351))


def test_history_overview_is_bounded_and_uses_source_timestamps(tmp_path):
    history = HistoricalSignalStore(tmp_path / "history.sqlite3")
    history.append_many(("speed", float(i), float(i), None) for i in range(10_000))

    overview = history.overview("speed", 0.0, 9_999.0, max_points=100)

    assert 0 < len(overview) <= 100
    assert all(timestamp == value for timestamp, value in overview)
    assert overview[0][0] == 0.0
    assert overview[-1][0] == 9_999.0


def test_history_exact_query_refuses_unbounded_range(tmp_path):
    history = HistoricalSignalStore(tmp_path / "history.sqlite3")
    history.append_many(("speed", float(i), i, None) for i in range(101))

    assert history.exact("speed", 0.0, 100.0, limit=100) == ()


def test_history_overview_preserves_late_extrema_and_chronological_order(tmp_path):
    history = HistoricalSignalStore(tmp_path / "history.sqlite3")
    history.append_many(
        ("signal", float(i), (100.0 if i % 4 == 0 else -100.0 if i % 4 == 1 else 0.0), None)
        for i in range(400)
    )

    overview = history.overview("signal", 0.0, 399.0, max_points=100)

    assert len(overview) <= 100
    assert overview[0][0] == 0.0
    assert overview[-1][0] == 399.0
    assert all(a[0] <= b[0] for a, b in zip(overview, overview[1:], strict=False))
    assert any(timestamp >= 300 and value == -100.0 for timestamp, value in overview)


def test_history_overview_is_materialized_and_invalidated_on_append(tmp_path):
    history = HistoricalSignalStore(tmp_path / "history.sqlite3")
    history.append_many(("speed", float(i), float(i), None) for i in range(100))
    first = history.overview("speed", 0.0, 99.0, max_points=20)
    cached = history._connection.execute("SELECT COUNT(*) FROM overview_cache").fetchone()[0]
    history.append_many([("speed", 100.0, 100.0, None)])
    invalidated = history._connection.execute("SELECT COUNT(*) FROM overview_cache").fetchone()[0]
    second = history.overview("speed", 0.0, 100.0, max_points=20)

    assert cached == 1
    assert invalidated == 0
    assert first[-1][0] == 99.0
    assert second[-1][0] == 100.0
