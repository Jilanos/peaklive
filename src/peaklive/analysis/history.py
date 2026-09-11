"""Bounded-memory historical signal storage for replay graph resolution.

The live graph keeps only a small ``SignalSeries`` projection.  This module
keeps the complete decoded history in a session-scoped SQLite file instead:
RAM contains only the cursor returned by a range query and the graph-sized
overview.  The same store can therefore serve a truthful overview and exact
samples for a narrow viewport without retaining every sample in Python.
"""

from __future__ import annotations

import json
import sqlite3
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def rows_to_summary(rows):
    for signal, timestamp, encoded, _numeric, unit in rows:
        yield signal, timestamp, json.loads(encoded), unit


class HistoricalSignalStore:
    """A temporary, indexed store of decoded signal samples."""

    def __init__(self, path: Path | None = None) -> None:
        self._owned_path = path is None
        if path is None:
            self._path = Path(tempfile.mkstemp(prefix="peaklive-history-", suffix=".sqlite3")[1])
        else:
            self._path = path
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
        for signal, timestamp, value, _unit in rows_to_summary(rows):
            encoded = json.dumps(value)
            numeric = isinstance(value, int | float) and not isinstance(value, bool)
            for level, width in enumerate((0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0)):
                bucket = int(float(timestamp) // width)
                existing = self._connection.execute(
                    "SELECT first_ts, first_value, last_ts, last_value, min_ts, min_value, "
                    "max_ts, max_value FROM summary WHERE signal=? AND level=? AND bucket=?",
                    (signal, level, bucket),
                ).fetchone()
                if existing is None:
                    self._connection.execute(
                        "INSERT INTO summary VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            signal,
                            level,
                            bucket,
                            timestamp,
                            encoded,
                            timestamp,
                            encoded,
                            timestamp if numeric else None,
                            encoded if numeric else None,
                            timestamp if numeric else None,
                            encoded if numeric else None,
                        ),
                    )
                    continue
                first_ts, first_value, last_ts, last_value, min_ts, min_value, max_ts, max_value = (
                    existing
                )
                if timestamp < first_ts:
                    first_ts, first_value = timestamp, encoded
                if timestamp >= last_ts:
                    last_ts, last_value = timestamp, encoded
                if numeric and (min_ts is None or float(value) < json.loads(min_value)):
                    min_ts, min_value = timestamp, encoded
                if numeric and (max_ts is None or float(value) > json.loads(max_value)):
                    max_ts, max_value = timestamp, encoded
                self._connection.execute(
                    "UPDATE summary SET first_ts=?, first_value=?, last_ts=?, last_value=?, "
                    "min_ts=?, min_value=?, max_ts=?, max_value=? WHERE signal=? AND level=? AND bucket=?",
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
        self._connection.executemany(
            "INSERT INTO samples(signal, timestamp, value, numeric, unit) VALUES (?, ?, ?, ?, ?)",
            rows,
        )
        self._connection.commit()
        return len(rows)

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
            result = tuple(sorted(set(points), key=lambda item: item[0]))[:max_points]
            self._connection.execute(
                "INSERT OR REPLACE INTO overview_cache VALUES (?, ?, ?, ?, ?)",
                (signal, float(start), float(end), int(max_points), json.dumps(result)),
            )
            self._connection.commit()
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
        for bucket in sorted(buckets):
            seen: set[tuple[float, str]] = set()
            candidates = sorted(buckets[bucket], key=lambda item: item[0])
            for timestamp, value, _ in candidates:
                marker = (timestamp, json.dumps(value, sort_keys=True))
                if marker not in seen:
                    points.append((timestamp, value))
                    seen.add(marker)
        result = tuple(points)
        self._connection.execute(
            "INSERT OR REPLACE INTO overview_cache(signal, start, end, max_points, payload) "
            "VALUES (?, ?, ?, ?, ?)",
            (signal, float(start), float(end), int(max_points), json.dumps(result)),
        )
        self._connection.commit()
        return result

    def clear(self) -> None:
        self._connection.execute("DELETE FROM samples")
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
