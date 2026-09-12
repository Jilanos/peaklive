"""Bounded-memory historical signal storage for replay graph resolution.

The live graph keeps only a small ``SignalSeries`` projection.  This module
keeps the complete decoded history in a session-scoped SQLite file instead:
RAM contains only the cursor returned by a range query and the graph-sized
overview.  The same store can therefore serve a truthful overview and exact
samples for a narrow viewport without retaining every sample in Python.
"""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def rows_to_summary(rows):
    for signal, timestamp, encoded, _numeric, unit in rows:
        yield signal, timestamp, json.loads(encoded), unit


def historical_points(
    history: HistoricalSignalStore | None,
    signal: str,
    extent: tuple[float, float] | None,
    visible: tuple[float, float] | None,
    *,
    exact_threshold: float = 0.08,
) -> tuple[tuple[float, object], ...] | None:
    """Resolve a viewport without depending on the UI or importing Qt."""
    if history is None or extent is None or visible is None:
        return None
    full_span = max(0.0, extent[1] - extent[0])
    visible_span = max(0.0, visible[1] - visible[0])
    if full_span > 0 and visible_span / full_span <= exact_threshold:
        exact = history.exact(signal, *visible, limit=20_000)
        if exact:
            return exact
    return history.overview(signal, *visible, max_points=4_000)


class HistoricalSignalStore:
    """A temporary, indexed store of decoded signal samples."""

    def __init__(self, path: Path | None = None, *, read_only: bool = False) -> None:
        if read_only and path is None:
            raise ValueError("A read-only history requires an existing path")
        self._read_only = read_only
        self._owned_path = path is None
        if path is None:
            descriptor, name = tempfile.mkstemp(prefix="peaklive-history-", suffix=".sqlite3")
            os.close(descriptor)
            self._path = Path(name)
        else:
            self._path = path
        if read_only:
            # Never recreate a session file already removed by its owner, or
            # write schema/cache data from a background viewport reader.
            self._connection = sqlite3.connect(self._path.resolve().as_uri() + "?mode=ro", uri=True)
            return
        self._connection = sqlite3.connect(self._path)
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS samples ("
            "signal TEXT NOT NULL, timestamp REAL NOT NULL, "
            "value TEXT NOT NULL, numeric REAL, unit TEXT, "
            "sample_id INTEGER PRIMARY KEY AUTOINCREMENT"
            ")"
        )
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS summary ("
            "signal TEXT NOT NULL, level INTEGER NOT NULL, bucket INTEGER NOT NULL, "
            "first_ts REAL NOT NULL, first_value TEXT NOT NULL, last_ts REAL NOT NULL, "
            "last_value TEXT NOT NULL, min_ts REAL, min_value TEXT, max_ts REAL, "
            "max_value TEXT, PRIMARY KEY(signal, level, bucket))"
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS summary_lookup ON summary(signal, level, bucket)"
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS samples_signal_time ON samples(signal, timestamp)"
        )
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS overview_cache ("
            "signal TEXT NOT NULL, start REAL NOT NULL, end REAL NOT NULL, "
            "max_points INTEGER NOT NULL, payload TEXT NOT NULL, "
            "PRIMARY KEY(signal, start, end, max_points))"
        )
        # A "run" is a maximal span of consecutive (in time) samples that share
        # one exact value. `events` anchors the first and last timestamp of
        # every run transition, so a short plateau excursion (a four-frame
        # assertion after 50,000 quiet frames, a 250 A to 180 A dip lasting
        # 100 ms) stays discoverable even when it is not the bucket extremum
        # that the summary hierarchy would otherwise keep. `signal_run_state`
        # carries the open run across append_many() calls so a batch split
        # never fabricates a spurious transition at its boundary.
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS events ("
            "signal TEXT NOT NULL, timestamp REAL NOT NULL, PRIMARY KEY(signal, timestamp))"
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS events_signal_time ON events(signal, timestamp)"
        )
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS signal_run_state ("
            "signal TEXT PRIMARY KEY, run_start_ts REAL NOT NULL, run_start_value TEXT NOT NULL, "
            "last_ts REAL NOT NULL, last_value TEXT NOT NULL)"
        )
        self._connection.commit()

    @property
    def path(self) -> Path:
        return self._path

    def append_many(self, samples: Iterable[tuple[str, float, Any, str | None]]) -> int:
        rows = []
        for signal, timestamp, value, unit in samples:
            numeric = (
                float(value)
                if isinstance(value, int | float) and not isinstance(value, bool)
                else None
            )
            rows.append((signal, float(timestamp), json.dumps(value), numeric, unit))
        if not rows:
            return 0
        # Cached summaries are immutable views of the previous data revision.
        # Invalidation is transactional with the append so a worker can never
        # install a summary built from a partial write.
        self._connection.execute("DELETE FROM overview_cache")
        # Every batch must maintain complete summary coverage: a partial
        # summary that is merely nonempty was previously trusted as complete,
        # silently replacing whole intervals with a handful of points from the
        # last small append. Group the batch in Python first (already
        # in-memory) so each distinct bucket costs one SELECT/UPSERT instead
        # of one round trip per sample, keeping large batches bounded by the
        # number of touched buckets rather than the sample count.
        widths = (0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0)
        # (signal, level, bucket) -> (first_ts, first_value, last_ts, last_value,
        #  min_ts, min_value, max_ts, max_value). Ties are broken by timestamp
        # alone (earliest occurrence), never by batch/processing order, so a
        # bucket's summary is identical however the same raw rows are split
        # across append_many() calls.
        groups: dict[tuple[str, int, int], list] = {}
        for timestamp, encoded, numeric_flag, signal in (
            (timestamp, encoded, numeric_flag, signal)
            for signal, timestamp, encoded, numeric_flag, _unit in rows
        ):
            numeric = numeric_flag is not None
            for level, width in enumerate(widths):
                bucket = int(timestamp // width)
                key = (signal, level, bucket)
                group = groups.get(key)
                if group is None:
                    groups[key] = [
                        timestamp, encoded,  # first
                        timestamp, encoded,  # last
                        timestamp if numeric else None, encoded if numeric else None,  # min
                        timestamp if numeric else None, encoded if numeric else None,  # max
                    ]
                    continue
                if timestamp < group[0]:
                    group[0], group[1] = timestamp, encoded
                if timestamp > group[2]:
                    group[2], group[3] = timestamp, encoded
                if numeric and (
                    group[4] is None
                    or numeric_flag < json.loads(group[5])
                    or (numeric_flag == json.loads(group[5]) and timestamp < group[4])
                ):
                    group[4], group[5] = timestamp, encoded
                if numeric and (
                    group[6] is None
                    or numeric_flag > json.loads(group[7])
                    or (numeric_flag == json.loads(group[7]) and timestamp < group[6])
                ):
                    group[6], group[7] = timestamp, encoded
        for (signal, level, bucket), group in groups.items():
            first_ts, first_value = group[0], group[1]
            last_ts, last_value = group[2], group[3]
            min_ts, min_value = group[4], group[5]
            max_ts, max_value = group[6], group[7]
            existing = self._connection.execute(
                "SELECT first_ts, first_value, last_ts, last_value, min_ts, min_value, "
                "max_ts, max_value FROM summary WHERE signal=? AND level=? AND bucket=?",
                (signal, level, bucket),
            ).fetchone()
            if existing is not None:
                (
                    existing_first_ts,
                    existing_first_value,
                    existing_last_ts,
                    existing_last_value,
                    existing_min_ts,
                    existing_min_value,
                    existing_max_ts,
                    existing_max_value,
                ) = existing
                if existing_first_ts < first_ts:
                    first_ts, first_value = existing_first_ts, existing_first_value
                if existing_last_ts > last_ts:
                    last_ts, last_value = existing_last_ts, existing_last_value
                if existing_min_ts is not None and (
                    min_ts is None
                    or json.loads(existing_min_value) < json.loads(min_value)
                    or (
                        json.loads(existing_min_value) == json.loads(min_value)
                        and existing_min_ts < min_ts
                    )
                ):
                    min_ts, min_value = existing_min_ts, existing_min_value
                if existing_max_ts is not None and (
                    max_ts is None
                    or json.loads(existing_max_value) > json.loads(max_value)
                    or (
                        json.loads(existing_max_value) == json.loads(max_value)
                        and existing_max_ts < max_ts
                    )
                ):
                    max_ts, max_value = existing_max_ts, existing_max_value
                self._connection.execute(
                    "UPDATE summary SET first_ts=?, first_value=?, last_ts=?, last_value=?, "
                    "min_ts=?, min_value=?, max_ts=?, max_value=? "
                    "WHERE signal=? AND level=? AND bucket=?",
                    (
                        first_ts,
                        first_value,
                        last_ts,
                        last_value,
                        min_ts,
                        min_value,
                        max_ts,
                        max_value,
                        signal,
                        level,
                        bucket,
                    ),
                )
            else:
                self._connection.execute(
                    "INSERT INTO summary VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        signal,
                        level,
                        bucket,
                        first_ts,
                        first_value,
                        last_ts,
                        last_value,
                        min_ts,
                        min_value,
                        max_ts,
                        max_value,
                    ),
                )
        self._connection.executemany(
            "INSERT INTO samples(signal, timestamp, value, numeric, unit) VALUES (?, ?, ?, ?, ?)",
            rows,
        )
        self._record_run_events(rows)
        self._connection.commit()
        return len(rows)

    def _record_run_events(
        self, rows: list[tuple[str, float, str, float | None, str | None]]
    ) -> None:
        by_signal: dict[str, list[tuple[float, str]]] = {}
        for signal, timestamp, encoded, _numeric, _unit in rows:
            by_signal.setdefault(signal, []).append((timestamp, encoded))
        for signal, entries in by_signal.items():
            entries.sort(key=lambda item: item[0])
            state = self._connection.execute(
                "SELECT run_start_ts, run_start_value, last_ts, last_value "
                "FROM signal_run_state WHERE signal = ?",
                (signal,),
            ).fetchone()
            run_start_ts, run_start_value, last_ts, last_value = (
                state if state is not None else (None, None, None, None)
            )
            new_events: list[tuple[str, float]] = []
            for timestamp, encoded in entries:
                if last_value is None:
                    run_start_ts, run_start_value = timestamp, encoded
                    new_events.append((signal, timestamp))
                elif encoded != last_value:
                    new_events.append((signal, last_ts))
                    run_start_ts, run_start_value = timestamp, encoded
                    new_events.append((signal, timestamp))
                last_ts, last_value = timestamp, encoded
            if new_events:
                self._connection.executemany(
                    "INSERT OR IGNORE INTO events(signal, timestamp) VALUES (?, ?)", new_events
                )
            self._connection.execute(
                "INSERT INTO signal_run_state(signal, run_start_ts, run_start_value, "
                "last_ts, last_value) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(signal) DO UPDATE SET run_start_ts=excluded.run_start_ts, "
                "run_start_value=excluded.run_start_value, last_ts=excluded.last_ts, "
                "last_value=excluded.last_value",
                (signal, run_start_ts, run_start_value, last_ts, last_value),
            )

    def _event_anchors(
        self, signal: str, start: float, end: float, *, limit: int
    ) -> tuple[tuple[float, Any], ...]:
        """Run-boundary samples in range, or empty if there are too many to
        list individually. Listing a partial, arbitrarily truncated subset
        would misrepresent which events survive; an explicit clustered
        marker for the excess is future scope (see item_122 rare-event
        anchors), so this stays silent rather than fabricate a boundary.
        """
        if limit <= 0:
            return ()
        rows = self._connection.execute(
            "SELECT samples.timestamp, samples.value FROM events "
            "JOIN samples ON samples.signal = events.signal "
            "AND samples.timestamp = events.timestamp "
            "WHERE events.signal = ? AND events.timestamp BETWEEN ? AND ? "
            "ORDER BY samples.timestamp LIMIT ?",
            (signal, float(start), float(end), int(limit) + 1),
        ).fetchall()
        if len(rows) > limit:
            return ()
        return tuple((float(timestamp), json.loads(value)) for timestamp, value in rows)

    def bounds(self) -> tuple[float, float] | None:
        row = self._connection.execute(
            "SELECT MIN(timestamp), MAX(timestamp) FROM samples"
        ).fetchone()
        if row is None or row[0] is None:
            return None
        return float(row[0]), float(row[1])

    def signal_bounds(self, signal: str) -> tuple[float, float] | None:
        row = self._connection.execute(
            "SELECT MIN(timestamp), MAX(timestamp) FROM samples WHERE signal = ?", (signal,)
        ).fetchone()
        if row is None or row[0] is None:
            return None
        return float(row[0]), float(row[1])

    def exact(
        self, signal: str, start: float, end: float, *, limit: int = 20_000
    ) -> tuple[tuple[float, Any], ...]:
        """Return source-derived samples, refusing an unbounded exact query."""
        if start > end:
            start, end = end, start
        rows = self._connection.execute(
            "SELECT timestamp, value FROM samples "
            "WHERE signal = ? AND timestamp BETWEEN ? AND ? "
            "ORDER BY timestamp LIMIT ?",
            (signal, float(start), float(end), int(limit) + 1),
        ).fetchall()
        if len(rows) > limit:
            return ()
        return tuple((float(timestamp), json.loads(value)) for timestamp, value in rows)

    def _cache_overview(
        self, signal: str, start: float, end: float, max_points: int, result: tuple
    ) -> None:
        """Only the session owner may persist overview cache entries."""
        if self._read_only:
            return
        self._connection.execute(
            "INSERT OR REPLACE INTO overview_cache(signal, start, end, max_points, payload) "
            "VALUES (?, ?, ?, ?, ?)",
            (signal, float(start), float(end), int(max_points), json.dumps(result)),
        )
        self._connection.commit()

    def overview(
        self, signal: str, start: float, end: float, *, max_points: int = 2_000
    ) -> tuple[tuple[float, Any], ...]:
        """Return a bounded min/max envelope with original sample timestamps."""
        if start > end:
            start, end = end, start
        if max_points < 2 or end <= start:
            return self.exact(signal, start, end, limit=max_points)
        cached = self._connection.execute(
            "SELECT payload FROM overview_cache WHERE signal = ? AND start = ? "
            "AND end = ? AND max_points = ?",
            (signal, float(start), float(end), int(max_points)),
        ).fetchone()
        if cached is not None:
            return tuple((float(timestamp), value) for timestamp, value in json.loads(cached[0]))
        span = end - start
        widths = (0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0)
        level = next(
            (
                candidate
                for candidate, width in enumerate(widths)
                if span / width <= max_points // 4
            ),
            4,
        )
        width = widths[level]
        summaries = self._connection.execute(
            "SELECT first_ts, first_value, last_ts, last_value, min_ts, min_value, "
            "max_ts, max_value FROM summary WHERE signal=? AND level=? "
            "AND bucket BETWEEN ? AND ? ORDER BY bucket",
            (signal, level, int(start // width), int(end // width)),
        ).fetchall()
        if summaries:
            points = []
            for row in summaries:
                first_ts, first_value, last_ts, last_value, min_ts, min_value, max_ts, max_value = (
                    row
                )
                values = [(first_ts, json.loads(first_value)), (last_ts, json.loads(last_value))]
                if min_ts is not None:
                    values.extend(
                        ((min_ts, json.loads(min_value)), (max_ts, json.loads(max_value)))
                    )
                points.extend(values)
            # Reserve room for rare-event anchors before truncating: a bucket
            # extremum alone can miss a short plateau excursion (a two-frame
            # error, a 250 A to 180 A dip) that is neither the bucket's min
            # nor its max. Anchors are added to the same pool so they compete
            # for the budget honestly instead of being appended after the cut.
            anchor_budget = max(4, max_points // 4)
            points.extend(self._event_anchors(signal, start, end, limit=anchor_budget))
            ordered = sorted(points, key=lambda item: item[0])
            seen = set()
            unique = []
            for point in ordered:
                marker = (point[0], json.dumps(point[1], sort_keys=True))
                if marker not in seen:
                    seen.add(marker)
                    unique.append(point)
            result = tuple(unique[:max_points])
            self._cache_overview(signal, start, end, max_points, result)
            return result
        # Four source samples per bucket (first, last, minimum, maximum) keep
        # extrema and both edges without ever requiring a global slice.  The
        # previous implementation used half as many buckets and then sliced
        # the concatenated result, which discarded late intervals and could
        # leave points out of chronological order.
        bucket_count = max(1, max_points // 4)
        bucket_width = (end - start) / bucket_count
        buckets: dict[int, list[tuple[float, Any, float | None]]] = {}
        cursor = self._connection.execute(
            "SELECT timestamp, value, numeric FROM samples "
            "WHERE signal = ? AND timestamp BETWEEN ? AND ? ORDER BY timestamp",
            (signal, float(start), float(end)),
        )
        for timestamp, encoded, numeric in cursor:
            bucket = min(int((float(timestamp) - start) / bucket_width), bucket_count - 1)
            slot = buckets.setdefault(bucket, [])
            value = json.loads(encoded)
            sample = (float(timestamp), value, numeric)
            if not slot:
                slot.append(sample)
                continue
            first = slot[0]
            last = sample
            if numeric is None or slot[0][2] is None:
                # Non-numeric values have no extrema; retain edge changes.
                slot[:] = [first, last]
                continue
            minimum = min((slot[2] if len(slot) >= 3 else first, sample), key=lambda item: item[2])
            maximum = max((slot[3] if len(slot) >= 4 else first, sample), key=lambda item: item[2])
            slot[:] = [first, last, minimum, maximum]
        points: list[tuple[float, Any]] = []
        seen: set[tuple[float, str]] = set()
        for bucket in sorted(buckets):
            candidates = sorted(buckets[bucket], key=lambda item: item[0])
            for timestamp, value, _ in candidates:
                marker = (timestamp, json.dumps(value, sort_keys=True))
                if marker not in seen:
                    points.append((timestamp, value))
                    seen.add(marker)
        anchor_budget = max(4, max_points // 4)
        for timestamp, value in self._event_anchors(signal, start, end, limit=anchor_budget):
            marker = (timestamp, json.dumps(value, sort_keys=True))
            if marker not in seen:
                points.append((timestamp, value))
                seen.add(marker)
        points.sort(key=lambda item: item[0])
        result = tuple(points[:max_points])
        self._cache_overview(signal, start, end, max_points, result)
        return result

    def clear(self) -> None:
        # Reset must be atomic across raw samples, every summary level and the
        # overview cache: leaving any derived table populated let a cleared,
        # reused store still answer queries with the previous session's data.
        self._connection.execute("DELETE FROM samples")
        self._connection.execute("DELETE FROM summary")
        self._connection.execute("DELETE FROM overview_cache")
        self._connection.execute("DELETE FROM events")
        self._connection.execute("DELETE FROM signal_run_state")
        self._connection.commit()

    def close(self) -> None:
        if getattr(self, "_connection", None) is None:
            return
        self._connection.close()
        self._connection = None  # type: ignore[assignment]
        if self._owned_path:
            try:
                self._path.unlink(missing_ok=True)
            except PermissionError:
                # Windows can retain a short-lived SQLite file handle while
                # Qt drains a queued timer. The connection is already closed;
                # leaving this uniquely named temp file is safer than failing
                # window shutdown, and the OS temp lifecycle can reclaim it.
                pass

    def __enter__(self) -> HistoricalSignalStore:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
