## req_023_deliver_multiresolution_trace_graphs_with_precise_on_demand_zoom_detail - Deliver multiresolution trace graphs with precise on-demand zoom detail
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Multiresolution historical signal exploration
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-10 13:19:29

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: deliver, multiresolution, trace, graphs, precise, demand, zoom, detail
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Needs
- An analyst must be able to inspect the entire duration of a large recorded trace without silently losing early high-rate signal values.
- When the visible time range is broad, graph rendering must use a bounded downsampled representation that preserves meaningful extrema and keeps interaction responsive.
- When the analyst zooms into a smaller range, the graph must replace the overview with exact decoded source samples for that visible interval, without reopening the session or corrupting measurements.
- The application must make the current overview-versus-exact detail state understandable and must never present approximated values as exact samples.

# Context
- The current SignalSeries has a fixed 20,000-sample retention bound. In a 944-second trace where Ecran1 and DCDC messages arrive at about 100 Hz, it drops their history before approximately 744 seconds even though the source trace contains those frames.
- The current FrameCache retains only the last 50,000 raw frames, so a signal selected after replay can be decoded only from the final portion of a high-volume capture.
- The replay parser already streams ASC and text TRC records, supports progress and cancellation, and the graph stack already clips and downsample-renders its retained curve. Those display optimizations cannot recover samples discarded by bounded session retention.
- The delivered design must retain bounded RAM usage. The authoritative historical source may remain the selected trace file plus a compact, validated, seekable index; it must not become an unbounded in-memory raw-frame or decoded-series cache.
- Replay replacement, trace deletion or modification, DBC conflicts, deferred signal selection, graph cursors, measurements, export, and session cancellation already have defined lifecycle semantics that the new detail loader must respect.

# Acceptance criteria
- AC1: For a completed supported trace, every selected supported signal can be represented across the full source time span even when its raw sample count exceeds the current per-series retention limit; no early interval is silently omitted from the overview.
- AC2: At a full-capture or otherwise broad viewport, each graph renders a bounded multiresolution downsampled overview whose sample count scales with the viewport budget rather than source-frame count and that preserves visible min/max excursions per bucket.
- AC3: After a pan, wheel zoom, cursor-driven range action, or fit action makes an interval sufficiently narrow, PeakLive asynchronously obtains and displays the exact decoded samples for the visible range plus a documented guard band. The result is generation-safe, cancellable, and never blocks the UI event loop beyond the documented responsiveness budget.
- AC4: Exact-detail samples are decoded from the authoritative capture source and active DBC definitions, retain their original timestamps and values, and are not fabricated by interpolation or derived from the overview buckets.
- AC5: Switching between overview and exact detail is visibly and accessibly communicated. While exact detail is loading or unavailable, the last valid overview remains usable and the operator receives an actionable, non-modal explanation.
- AC6: Memory, worker queues, disk-index size, decode work, and graph point counts have explicit bounds. Repeated navigation across a long high-rate trace neither accumulates unbounded state nor applies stale detail results after trace replacement, signal deselection, or a newer viewport request.
- AC7: Cursors, measurements, trace table, exports, existing live acquisition behavior, DBC conflict handling, and replay cancellation retain documented semantics. Any calculation labelled exact uses exact samples for its requested range or explicitly reports that exact detail is unavailable.
- AC8: Deterministic synthetic and sanitized replay fixtures prove complete-history overview, extremum preservation, exact zoomed values and timestamps, viewport-driven cancellation, source-change failure handling, retention bounds, and responsive offscreen UI behavior on Windows and Linux CI.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_022_peaklive_multiresolution_lossless_historical_trace_detail`
- Architecture decision(s): (none yet)

# References
- src/peaklive/analysis/replay.py
- src/peaklive/analysis/frames.py
- src/peaklive/analysis/series.py
- src/peaklive/services/replay_worker.py
- src/peaklive/services/signal_decode_worker.py
- src/peaklive/ui/ingest_controller.py
- src/peaklive/ui/session_controller.py
- src/peaklive/ui/panels/graph_stack.py
- src/peaklive/ui/panels/graph_navigation.py
- tests/test_lazy_signals.py
- tests/test_graph_performance.py
- tests/test_replay_worker.py

# Backlog
- `item_114_create_a_bounded_indexed_historical_signal_source_for_complete_trace_overview`
- `item_115_deliver_cancellable_viewport_driven_exact_graph_detail`
