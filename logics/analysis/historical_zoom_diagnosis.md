# Historical zoom responsiveness diagnosis — 2026-09-11

The current historical graph path bounds its output size but not the work performed on the GUI thread. This explains why retaining complete history exposes severe zoom latency. The appropriate correction stays within Python, PySide6, pyqtgraph and the existing SQLite store: coalesce navigation, move historical requests to an owned worker, and serve precomputed resolution levels instead of rescanning raw samples for each viewport.

## Evidence and limits

The operator reports freezes with a local 195,753,923-byte ASC capture and packaged build `0.1.2+b202609101606`. Source inspected: `abafee872c1dffdbb1bc9da78265ca569829bdca`, version 0.1.2. The build metadata is available locally, but an exact executable-to-source mapping has not been independently proven. Measurements below exercise the repository code, not a profiler attached to that executable. The operator's selected signals, DBC selection and number of graph lanes are not known; do not infer their exact interaction latency from an isolated query.

The diagnostic script `logics/analysis/zoom_diagnostic.py` accepts the private capture as an argument, streams it through the application's parser, reports aggregate counts, and builds a temporary history for byte zero of the most frequent frame identifier. That probe uses real timestamps and sample density but is explicitly not a DBC-decoded signal. A deterministic oscillating signal checks overview correctness; an offscreen Qt probe checks callback accumulation. The capture and its payload are not copied into the corpus.

Reproduce in PowerShell from the repository with `$env:PYTHONPATH='src'`, then `.venv-win/Scripts/python.exe logics/analysis/zoom_diagnostic.py <local-capture.asc>`. Temporary databases use a dedicated temporary directory and are cleaned up. Measurements are local observations, not release performance guarantees.

### Local measurements

On Python 3.13.15 / SQLite 3.53.1, the parser counted 1,755,746 CAN frames, 40 identifiers, timestamps 0.002175 to 944.791080 s (944.788905 s duration), 991 bus-status records, 23 error-frame records and one replay anomaly. The eight most frequent identifiers each contain 94,492 or 94,493 frames. These aggregate event counts are parser results, not causes established for the zoom freeze.

| Isolated operation | Observed results |
| --- | --- |
| Full overview, 94,493 real-timestamp raw-byte samples, 4,000 output cap | 943.630 / 974.733 / 926.732 ms |
| Global bounds on that store | 16.021 / 19.084 / 19.034 ms |
| One-second exact range | 0.728 / 0.551 / 0.492 ms |
| 30 immediately queued refresh requests | 30 callbacks after Qt event processing |
| Oscillating 400-sample fixture, 100-point cap | Last output timestamp 193 instead of 399; timestamps not sorted |

SQLite EXPLAIN reports `SCAN samples USING COVERING INDEX samples_signal_time` for the global bounds query. The real raw-byte probe itself retained its endpoints and was sorted; the separate oscillating fixture proves the defect is data-dependent. The Qt probe emitted a missing-font-directory warning but completed its timer check; it does not validate visible rendering or packaged UI latency. Multi-lane latency is not measured here; multiplying the one-series cost is only an order-of-magnitude estimate, not an observed end-to-end result.

## Confirmed source-level causes

1. `workspace_center.py` connects `view_changed` to `request_view_refresh`. Every lane connects `sigXRangeChanged` to `_x_range_changed`. Each resulting request schedules a separate `QTimer.singleShot(75, refresh_data)` in `graph_stack.py`. This delays work but does not debounce it. Linked lanes can amplify events; each callback redraws all lanes and reads the latest viewport, repeating equivalent work rather than preserving useful intermediate frames.
2. `refresh_data -> curve_points -> historical_points -> history.overview` executes synchronously in the GUI thread. `overview` reads every matching SQLite row, JSON-decodes every value, and reduces buckets in Python. Its time is O(samples in the visible range), even when returning only 4,000 points. Zooming out makes it most expensive. The `(signal, timestamp)` index helps locate a range; it cannot eliminate visiting all rows selected by that range.
3. Every refresh also executes `history.bounds()`: `SELECT MIN(timestamp), MAX(timestamp) FROM samples`. Global bounds are not cached. This adds work across historical signals even for a narrow viewport.
4. Exact-mode selection uses 8% of total duration, independent of sample density or pixel width. A range exceeding 20,000 samples first fetches 20,001 records, then returns an empty tuple, then triggers the overview scan. Empty data and an over-budget exact request share the same result shape.
5. Graph data is recopied and `setData` is called for all curves on every scheduled refresh. Measurements are dirtied even by a pure viewport change. Existing 250 ms measurement throttling reduces frequency but does not eliminate unchanged or hidden-table work.

## Correctness defects that the correction must cover

`overview` allocates `max_points // 2` buckets but may emit four distinct points per bucket (first, last, minimum, maximum), then globally slices `points[:max_points]`. Oscillating data can therefore lose the latter part of the requested interval. Within a bucket, the first/last/min/max order is not chronological. Rendering and clip-to-view must receive stable chronological output; slicing must never discard late buckets.

`GraphNavigation.global_extent()` still uses the retained `SeriesStore` bounds, whereas the data refresh obtains historical bounds separately. Fit/follow and query extents can disagree after retention truncation. One authoritative historical extent is required.

Measurements still use the 20,000-sample live projection. Showing historical curves does not make A/B calculations historically complete. A correction must use exact historical data for such calculations or clearly mark them unavailable/partial. Late signal selection also backfills from the 50,000-frame cache and does not populate full history; missing history must be explicit. Full arbitrary-signal re-decoding is a separate capability and must not be accidentally promised by this performance repair.

The earlier request `req_023_deliver_multiresolution_trace_graphs_with_precise_on_demand_zoom_detail` is marked Done, but the inspected path does not implement its asynchronous viewport decoder or precomputed multiresolution levels. Existing history tests cover a monotonic signal and point count, which misses oscillating-data truncation and event-loop starvation. This new corpus records the observed gap without rewriting prior completion evidence.

## Correction design and alternatives

| Change | Purpose | Limitation / decision |
| --- | --- | --- |
| One owned restartable 75 ms single-shot timer, one pending viewport | Collapse bursts and linked-axis duplicates | Necessary, but alone leaves each query blocking |
| One history request worker, latest request wins | Keep SQLite and historical preparation off the GUI thread | Thread ownership, cancellation and bounded work still required |
| Cached global/signal bounds and viewport results | Avoid unchanged queries and curve uploads | Invalidate by session, DBC, signal and data revision; cap bytes |
| Indexed multiresolution first/min/max/last summaries | Bound broad-view work by display resolution | Build once in background; preserve original timestamps and extrema |
| Indexed exact queries with density-aware selection | Preserve original detail in narrow windows | Explicit overflow/empty/error states; keep a raw point cap |
| SQL aggregation on the raw table | Possible transitional reduction in Python overhead | Still scans raw range; does not meet the final broad-view complexity contract |
| More pyqtgraph downsampling, GPU/OpenGL, or larger RAM buffers | May affect painting only | Does not remove synchronous DB scans or callback accumulation; not the primary remedy |
| Move to another database, web UI or C++ renderer | Potential later redesign | No evidence justifies the migration cost for this defect |

Retain SQLite exact samples. Build a disk-backed hierarchy with deterministic first/min/max/last source records and counts; choose a level by viewport width and density, then merge only bounded edge/detail data. Allocate at most four output slots per bucket, deduplicate by stable sample identity and sort by `(timestamp, sample_id)`. Preserve both viewport ends, gaps and late extrema. Avoid false continuity across gaps and arbitrary zero values for nonnumeric data.

Qt objects and SQLite connections have explicit owners. Create the read connection inside the worker; do not pass the GUI connection into a QThread or disable thread checks as a substitute for ownership. Return immutable bounded arrays via signals and update widgets on the GUI thread. A running request plus a replaceable pending request is sufficient. Cancellation must interrupt obsolete SQL or check bounded work chunks; stale-result rejection alone does not stop CPU consumption. Keys include session generation, DBC revision, signal selection, data revision, viewport and resolution. Keep the previous valid curve visible while pending, with an accessible overview/exact/loading/unavailable state.

For completed replay, a dedicated reader can use committed data. If index creation overlaps writes, choose a dedicated writer and short transactions; evaluate WAL only when concurrent readers are needed, with checkpoint and cleanup limits. Keep the database on local temporary storage. Moving Python's entire raw-row loop to a thread is only an intermediate measure: it still consumes CPU and can contend for the GIL, hence preaggregation is required. See the official [Qt timer contract](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QTimer.html), [Qt thread ownership](https://doc.qt.io/qtforpython-6.10/overviews/qtdoc-threads-qobject.html), and [SQLite WAL concurrency and limits](https://www.sqlite.org/wal.html).

## Delivery budgets and validation

Proposed acceptance targets, to measure on a recorded Windows reference machine: 20 ms heartbeat p95 lateness <= 50 ms and maximum <= 150 ms during 100 mixed zoom/pan/fit actions with 1, 4 and 8 lanes; no historical SQL/JSON reduction on the GUI thread; final viewport installed <= 250 ms warm and <= 1 s cold after gesture settling on the qualification fixture. Record hardware, versions, display width, warm/cold conditions and raw distributions. Cold-index construction is separately timed, cancellable and visibly reported; it must not masquerade as interactive cold-query latency.

Overview budget per lane: `min(4000, max(256, 4 * viewport_width_px))`; exact cap 20,000 samples per lane. Summary records visited per query should scale with that budget and hierarchy depth, not raw capture length. Initial cache ceiling 64 MiB for all historical viewport results, one active/one pending request, no cache growth beyond the cap over 1,000 gestures. At 8 lanes each lane still has its own point limit and the aggregate must be recorded. Resource limits are implementation contracts, not measured baseline facts; index footprint and construction throughput require recorded evidence and an explicit disk-full policy.

Use deterministic 100 Hz and 1 kHz fixtures, at least 1 million total historical samples and 10x-length scaling checks. Cover spikes in every capture quarter, first/last values, descending extrema order, duplicate timestamps, empty ranges, gaps, enumerations, irregular density, exact overflow, signal selection, DBC replacement, replay cancellation/replacement and shutdown with pending work. Compare exact points against an independent source-derived oracle. Measure real Qt event-loop latency, not just total pytest duration or pyqtgraph option flags. Re-run the private capture locally when available, then qualify an identifiable packaged Windows executable. Do not close the task on unit tests alone.
