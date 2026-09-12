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


def test_history_overview_coverage_is_independent_of_append_batching(tmp_path):
    times = [i / 100 for i in range(94_501)]
    rows = [("probe", t, i % 17, None) for i, t in enumerate(times)]

    reference = HistoricalSignalStore(tmp_path / "bulk.sqlite3")
    reference.append_many(rows)
    baseline = reference.overview("probe", 0.0, times[-1], max_points=4_000)
    assert len(baseline) > 100

    for split, tail in enumerate((1, 16, 32, 33, 256, 4096)):
        store = HistoricalSignalStore(tmp_path / f"split-{split}.sqlite3")
        store.append_many(rows[:-tail])
        store.append_many(rows[-tail:])
        overview = store.overview("probe", 0.0, times[-1], max_points=4_000)
        assert len(overview) == len(baseline), f"tail={tail} lost coverage: {len(overview)}"
        assert overview[0][0] == baseline[0][0]
        assert overview[-1][0] == baseline[-1][0]
        store.close()
    reference.close()


def test_history_overview_coverage_is_independent_of_mixed_signal_batching(tmp_path):
    times = [i / 100 for i in range(5_000)]
    rows_a = [("a", t, i % 11, None) for i, t in enumerate(times)]
    rows_b = [("b", t, (i % 11) * 2, None) for i, t in enumerate(times)]

    reference = HistoricalSignalStore(tmp_path / "mixed_bulk.sqlite3")
    reference.append_many(rows_a + rows_b)
    baseline_a = reference.overview("a", 0.0, times[-1], max_points=1_000)
    baseline_b = reference.overview("b", 0.0, times[-1], max_points=1_000)

    store = HistoricalSignalStore(tmp_path / "mixed_split.sqlite3")
    store.append_many(rows_a[:-16] + rows_b[:-1])
    store.append_many(rows_a[-16:] + rows_b[-1:])
    assert store.overview("a", 0.0, times[-1], max_points=1_000) == baseline_a
    assert store.overview("b", 0.0, times[-1], max_points=1_000) == baseline_b


def test_history_clear_invalidates_summary_and_overview_cache(tmp_path):
    history = HistoricalSignalStore(tmp_path / "history.sqlite3")
    history.append_many([("probe", 0.0, 1, None), ("probe", 1.0, 2, None)])
    assert history.overview("probe", 0.0, 1.0) == ((0.0, 1), (1.0, 2))

    history.clear()

    assert history._connection.execute("SELECT COUNT(*) FROM summary").fetchone()[0] == 0
    assert history._connection.execute("SELECT COUNT(*) FROM overview_cache").fetchone()[0] == 0
    assert history.exact("probe", 0.0, 1.0) == ()
    assert history.overview("probe", 0.0, 1.0) == ()


def test_history_overview_preserves_a_nonextreme_short_dip_beside_a_larger_one(tmp_path):
    """A 250 A to 180 A dip lasting 100 ms must not vanish behind a larger,
    unrelated 250 A to 100 A dip that shares the same overview bucket.

    A 1000 s / 100 Hz capture at a realistic max_points=256 budget puts both
    dips inside the same single coarse bucket (bucket width 100 s), so the
    bucket's own min/max can only ever report one of them; only an
    independent event anchor keeps the non-extreme 180 A dip discoverable.
    See logics/analysis/dense_overview_diagnosis.md, "nonextreme_short_dip".
    """
    history = HistoricalSignalStore(tmp_path / "history.sqlite3")
    history.append_many(
        ("current", i / 100, 100 if 100 <= i < 110 else 180 if 500 <= i < 510 else 250, "A")
        for i in range(100_000)
    )

    overview = history.overview("current", 0.0, 999.99, max_points=256)

    assert any(value == 180 for _, value in overview)
    assert any(value == 100 for _, value in overview)


def test_history_overview_preserves_a_four_frame_assertion_after_quiet_frames(tmp_path):
    """A binary signal staying at 0 for 50,000 frames then asserting for four
    frames must remain discoverable, without an amplitude threshold.
    """
    history = HistoricalSignalStore(tmp_path / "history.sqlite3")
    history.append_many(
        ("door", i / 100, 1 if 50_000 <= i < 50_004 else 0, None) for i in range(60_000)
    )

    overview = history.overview("door", 0.0, 599.99, max_points=256)

    assert any(value == 1 for _, value in overview)


def test_history_event_anchors_survive_append_batch_boundaries(tmp_path):
    """A transition split across two append_many() calls must still anchor
    both its exit and entry samples, not fabricate a spurious extra one.
    """
    history = HistoricalSignalStore(tmp_path / "history.sqlite3")
    rows = [("door", i / 100, 1 if 50_000 <= i < 50_004 else 0, None) for i in range(60_000)]
    history.append_many(rows[:50_002])
    history.append_many(rows[50_002:])

    overview = history.overview("door", 0.0, 599.99, max_points=256)

    assert any(value == 1 for _, value in overview)
