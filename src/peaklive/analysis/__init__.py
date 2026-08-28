"""Bounded decoding, measurement, and replay services independent from Qt."""

from .benchmark import (
    CAPTURE_PROFILES,
    CaptureProfile,
    synthetic_asc_lines,
    synthetic_dbc,
    write_synthetic_capture,
)
from .dbc import (
    AmbiguousMessageError,
    CatalogView,
    DbcCatalog,
    DbcConflict,
    DbcDefinition,
    DbcSignalReference,
    DecodedSignal,
)
from .export import ExportRow, export_csv, export_parquet, export_rows
from .frames import DEFAULT_FRAME_CACHE_CAPACITY, FrameCache
from .profiling import PROFILER, STAGES, StageProfile, StageProfiler
from .replay import TraceCursor, iter_trace
from .series import SeriesStore, SignalSeries
from .session import DbcSummary, ReportRenderer, SessionFacts, SessionReport
from .statistics import RangeStatistics, cursor_value, numeric_delta, range_statistics
from .trace import (
    DECODE_CONFLICT,
    DECODE_DECODED,
    DECODE_UNKNOWN,
    FilteredTrace,
    TraceBuffer,
    TraceRecord,
    cell_text,
    filter_records,
    matches,
)

__all__ = [
    "CAPTURE_PROFILES",
    "DECODE_CONFLICT",
    "DEFAULT_FRAME_CACHE_CAPACITY",
    "PROFILER",
    "STAGES",
    "DECODE_DECODED",
    "DECODE_UNKNOWN",
    "AmbiguousMessageError",
    "CaptureProfile",
    "CatalogView",
    "DbcCatalog",
    "DbcConflict",
    "DbcDefinition",
    "DbcSignalReference",
    "DbcSummary",
    "DecodedSignal",
    "ExportRow",
    "FrameCache",
    "FilteredTrace",
    "RangeStatistics",
    "ReportRenderer",
    "SeriesStore",
    "SessionFacts",
    "SessionReport",
    "SignalSeries",
    "StageProfile",
    "StageProfiler",
    "TraceCursor",
    "TraceBuffer",
    "TraceRecord",
    "cell_text",
    "cursor_value",
    "export_csv",
    "export_parquet",
    "export_rows",
    "filter_records",
    "iter_trace",
    "matches",
    "synthetic_asc_lines",
    "synthetic_dbc",
    "write_synthetic_capture",
    "numeric_delta",
    "range_statistics",
]
