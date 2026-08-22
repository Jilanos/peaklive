"""Streaming decoded-signal exports."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq


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
