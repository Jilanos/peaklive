"""Streaming decoded-signal exports."""

from __future__ import annotations

import csv
import heapq
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from peaklive.analysis.series import SeriesStore


@dataclass(frozen=True, slots=True)
class ExportRow:
    timestamp: float
    message: str
    signal: str
    value: Any
    unit: str | None


def export_csv(path: Path, rows: Iterable[ExportRow]) -> int:
    count = 0
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["timestamp", "message", "signal", "value", "unit"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
            count += 1
    return count


def export_parquet(path: Path, rows: Iterable[ExportRow], batch_size: int = 10_000) -> int:
    schema = pa.schema(
        [
            ("timestamp", pa.float64()),
            ("message", pa.string()),
            ("signal", pa.string()),
            ("value", pa.string()),
            ("unit", pa.string()),
        ]
    )
    count = 0
    writer = pq.ParquetWriter(path, schema)
    try:
        batch: list[dict[str, Any]] = []
        for row in rows:
            batch.append(
                {
                    "timestamp": row.timestamp,
                    "message": row.message,
                    "signal": row.signal,
                    "value": str(row.value),
                    "unit": row.unit,
                }
            )
            count += 1
            if len(batch) == batch_size:
                writer.write_table(pa.Table.from_pylist(batch, schema=schema))
                batch.clear()
        if batch:
            writer.write_table(pa.Table.from_pylist(batch, schema=schema))
    finally:
        writer.close()
    return count


def export_rows(
    store: SeriesStore,
    signal_names: Sequence[str],
    start: float | None = None,
    end: float | None = None,
) -> Iterator[ExportRow]:
    """Stream the retained samples of the selected signals over a time range.

    Each signal is walked lazily and the per-signal streams are merged on
    timestamp, so the output reads like the trace while only one sample per
    signal is held at a time. Combined with the batched writers, a full-buffer
    export never materializes the whole range.
    """
    streams = [
        _signal_rows(store, name, start, end)
        for name in signal_names
        if store.series(name) is not None
    ]
    yield from heapq.merge(*streams, key=lambda row: (row.timestamp, row.message, row.signal))


def _signal_rows(
    store: SeriesStore,
    name: str,
    start: float | None,
    end: float | None,
) -> Iterator[ExportRow]:
    series = store.series(name)
    if series is None:
        return
    message, _, signal = name.partition(".")
    if start is None or end is None:
        times, values = series.times, series.values
    else:
        times, values = series.slice(start, end)
    for timestamp, value in zip(times, values, strict=True):
        yield ExportRow(timestamp, message or name, signal or name, value, series.unit)
