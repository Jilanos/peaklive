# Trace loading performance audit

This is the evidence behind the trace-loading work in `req_009`. It records how
the cost of opening a capture is distributed across the ingest path, what was
changed as a result, and the budgets a future change has to stay inside.

## How to reproduce

```bash
QT_QPA_PLATFORM=offscreen uv run python scripts/audit_trace_performance.py
```

The script generates its own captures from `peaklive.analysis.benchmark`, so
no recorded trace is committed and the measurement is identical on any machine.
`tests/test_trace_performance.py` runs the same instrumentation as a regression
test.

## What is measured

`peaklive.analysis.profiling` times seven stages, in the order a frame passes
through them. The profiler is disabled by default: an inactive stage returns a
shared no-op context, so the instrumentation stays on the shipped hot path
without costing anything.

| Stage | What it covers |
| --- | --- |
| `parse` | Streaming ASC/TRC normalization in `iter_trace` |
| `dispatch` | Handing a parsed batch from the worker to the UI thread |
| `decode` | DBC decoding of one frame |
| `trace_projection` | Trace buffer append, session facts, and table rows |
| `series_projection` | Bounded per-signal sample buffers |
| `graph_refresh` | Redrawing every curve from the retained samples |
| `report_refresh` | Rendering the session report |

## Measured profile

Three volumes at 1 kHz over eight decoded messages, after the changes below.
Times are milliseconds per thousand frames; the share column is of measured
time.

| Stage | small (2k) | medium (20k) | large (200k) | Share (large) |
| --- | --- | --- | --- | --- |
| `parse` | 7.14 | 6.00 | 6.06 | 28.9% |
| `dispatch` | 0.38 | 1.79 | 1.87 | 8.9% |
| `decode` | 4.02 | 4.17 | 4.01 | 19.1% |
| `trace_projection` | 20.80 | 10.32 | 7.10 | 33.9% |
| `series_projection` | 0.42 | 0.64 | 0.48 | 2.3% |
| `graph_refresh` | 0.85 | 0.94 | 1.45 | 6.9% |
| `report_refresh` | 0.21 | 0.02 | 0.00 | 0.0% |

**Dominant cost: `trace_projection`** at every volume, followed by `parse` and
`decode`. File IO is not the bottleneck; presentation is.

## What the audit found, and what changed

1. **Presentation, not IO, dominated.** Building `QTableWidgetItem`s and
   redrawing curves accounted for roughly three quarters of a large load.
   - Graph refreshes are coalesced onto a 50 ms timer instead of running once
     per ingested batch: a 200k-frame load now repaints 88 times, not 391.
   - Trace rows are coalesced too, and one flush projects at most
     `MAX_ROWS_PER_FLUSH` rows. A row superseded before it can be drawn is not
     drawn; one bounded refresh when ingestion settles makes the window
     authoritative again. `trace_projection` fell from 30.8 to 7.1 ms per
     thousand frames.

2. **The parser outran the display without limit.** Batches were emitted as
   fast as the disk allowed, so one event-loop pass had to render every batch
   queued behind it — the slowest measured pass was **4172 ms**, and Stop sat
   behind all of it. The worker now holds itself to `MAX_PENDING_BATCHES`
   batches ahead of the UI, which acknowledges each batch as it lands. The
   slowest pass is now **107 ms**, inside the 250 ms responsiveness budget, and
   cancellation is serviced within a bounded number of batches.

3. **Progress was never truthful.** `ReplayWorker` reported completion from the
   source file's own size, which does not change during a replay, so the bar
   read 100% from the first batch. A `TraceCursor` now reports consumed source
   bytes, and progress is emitted at most every 50 ms.

4. **Repeated full copies of bounded buffers.** Every graph refresh copied each
   signal's whole deque twice per curve. `SignalSeries` now caches its list
   snapshots and invalidates them on append. `TraceBuffer.record()` was a linear
   scan run once per ingested batch; it is now constant time.

Net effect on the 200k-frame capture: **8.9 s to 4.1 s wall clock**, and a
worst-case event-loop pass **39× shorter**.

## Budgets

`peaklive.analysis.profiling` owns these as code, and
`tests/test_trace_performance.py` enforces them.

| Bound | Value |
| --- | --- |
| `parse` | 40 ms / 1k frames |
| `dispatch` | 20 ms / 1k frames |
| `decode` | 30 ms / 1k frames |
| `trace_projection` | 150 ms / 1k frames |
| `series_projection` | 10 ms / 1k frames |
| `graph_refresh` | 30 ms / 1k frames |
| `report_refresh` | 10 ms / 1k frames |
| Event-loop responsiveness | 250 ms |
| Batches the parser may lead the display by | 4 |

The budgets carry roughly four times the measured headroom on purpose: they are
a regression alarm that has to hold on the slowest CI runner, not a score.

## Retention

Nothing here relaxes a bound. The trace buffer keeps 5 000 records, each signal
series keeps 20 000 samples, and the frame cache behind on-demand signal
decoding keeps 50 000 frames and reports when it has dropped older ones.
