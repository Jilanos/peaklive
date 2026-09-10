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


class HistoricalSignalStore:
    """A temporary, indexed store of decoded signal samples."""

    def __init__(self, path: Path | None = None) -> None:
        self._owned_path = path is None
        if path is None:
            self._path = Path(
                tempfile.mkstemp(prefix="peaklive-history-", suffix=".sqlite3")[1]
            )
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
            "CREATE INDEX IF NOT EXISTS samples_signal_time "
            "ON samples(signal, timestamp)"
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
        bucket_width = (end - start) / max(1, max_points // 2)
        buckets: dict[int, list[tuple[float, Any, float | None]]] = {}
        cursor = self._connection.execute(
            "SELECT timestamp, value, numeric FROM samples "
            "WHERE signal = ? AND timestamp BETWEEN ? AND ? ORDER BY timestamp",
            (signal, float(start), float(end)),
        )
        for timestamp, encoded, numeric in cursor:
            bucket = min(int((float(timestamp) - start) / bucket_width), max_points // 2 - 1)
            slot = buckets.setdefault(bucket, [])
            value = json.loads(encoded)
            sample = (float(timestamp), value, numeric)
            if not slot:
                slot.append(sample)
                continue
            first = slot[0]
            last = sample
            if numeric is None or slot[0][2] is None:
                slot[:] = [first, last]
                continue
            minimum = min((slot[-1], sample), key=lambda item: item[2])
            maximum = max((slot[-1], sample), key=lambda item: item[2])
            # slot is [first, last, min, max].  Keeping four records makes
            # memory independent of the source sample count while retaining
            # real timestamps for both extrema.
            if len(slot) >= 3:
                minimum = min((slot[2], sample), key=lambda item: item[2])
            if len(slot) >= 4:
                maximum = max((slot[3], sample), key=lambda item: item[2])
            slot[:] = [first, last, minimum, maximum]
        points: list[tuple[float, Any]] = []
        for bucket in sorted(buckets):
            seen: set[tuple[float, str]] = set()
            for timestamp, value, _ in buckets[bucket]:
                marker = (timestamp, json.dumps(value, sort_keys=True))
                if marker not in seen:
                    points.append((timestamp, value))
                    seen.add(marker)
        return tuple(points[:max_points])

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
