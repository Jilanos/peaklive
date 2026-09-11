## req_025_restore_responsive_and_faithful_historical_graph_navigation - Restore responsive and faithful historical graph navigation
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Historical navigation responsiveness and fidelity
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-11 15:38:13

# AI Context
- Summary: Repair the measured synchronous historical scan and callback accumulation exposed by a 1.75-million-frame capture.
- Keywords: restore, responsive, faithful, historical, graph, navigation
- Use when: Planning the cross-layer historical zoom regression correction and its evidence.
- Skip when: Changing CAN transport, export formats or arbitrary late-selected signal decoding.

# Needs
- Restore usable zoom, pan and fit on large completed captures while retaining complete historical evidence.
- Stay within Python/PySide6/pyqtgraph and the existing SQLite history store; provide a measured, implementable correction.
- Correct overview coverage defects together with the scheduler and query costs so faster curves remain trustworthy.

# Context
- The private 195753923-byte capture contains 1755746 parsed CAN frames across 944.788905 seconds and 40 identifiers. Frequent identifiers each have about 94493 frames.
- On the local source checkout, an isolated raw-byte series with real capture timestamps requires 926.732-974.733 ms to build a 4000-point overview from 94493 rows. This is not a DBC reproduction of the operator's exact graph setup or a timing of the packaged executable.
- Thirty request_view_refresh calls produce thirty Qt callbacks, not one. history.overview scans and JSON-decodes all selected rows synchronously; bounds performs a covering-index scan.
- A 400-sample oscillating fixture with a 100-point budget ends at timestamp 193 instead of 399 and produces unsorted timestamps.
- The earlier multiresolution request is marked Done but the inspected code still lacks an asynchronous historical viewport worker and precomputed resolution hierarchy. This is a corrective follow-up, not permission to rewrite past proof.
- Scope and reproducible evidence, tradeoffs and proposed budgets are defined in logics/analysis/historical_zoom_diagnosis.md. The private capture is kept outside versioned documentation.

# Acceptance criteria
- AC1: With completed historical data and 1, 4 and 8 linked lanes, 100 mixed wheel/pan/fit gestures meet a 20 ms heartbeat p95 lateness <= 50 ms and maximum <= 150 ms on the recorded Windows reference machine. Warm final viewport latency <= 250 ms and cold indexed-query latency <= 1 s after settling; index construction is separately reported.
- AC2: Navigation has one owned restartable 75 ms timer, at most one active and one replaceable pending history request; duplicate linked-axis notifications coalesce. No historical SQL, full-history scan or JSON reduction executes on the GUI thread. Obsolete work cancels and stale results cannot install.
- AC3: Broad views use indexed precomputed resolution levels and cached bounds. Returned overview points per lane <= min(4000, max(256, 4 * viewport_width_px)); raw exact points <= 20000. Instrumented rows visited scale with viewport budget and hierarchy depth rather than raw-range sample count.
- AC4: Every overview preserves full interval coverage, first/last samples and per-bucket extrema including late spikes, emits stable chronological timestamps/sample identities, and never truncates later buckets to meet its budget. Exact results match original decoded samples and distinguish overflow, empty, missing, error and cancelled states.
- AC5: Fit, follow and range selection use one authoritative historical extent; density-aware exact selection replaces the fixed 8-percent duration heuristic. Overview/exact/loading/unavailable states are visible and accessible; previous valid data remains usable while waiting. Historical A/B results are exact for their requested range or explicitly unavailable/partial.
- AC6: Session, source/DBC revision, data revision, signal selection and viewport generation isolate caches and workers. Historical viewport caches are capped at 64 MiB total; queues and index resources have explicit bounds and cleanup. Replacement, cancellation, deselection, disk errors and shutdown cannot apply stale data or block the GUI.
- AC7: Deterministic long dense/irregular/oscillating fixtures, 10x source-length scaling, real event-loop measurements and an identifiable packaged Windows replay prove the correction. Existing live capture, replay backpressure, trace retention, exports and decode semantics retain their documented behavior; no raw history is discarded to achieve speed.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_024_peaklive_responsive_and_faithful_historical_navigation_correction`
- Architecture decision(s): (none yet)

# References
- logics/analysis/historical_zoom_diagnosis.md
- logics/analysis/zoom_diagnostic.py
- logics/request/req_023_deliver_multiresolution_trace_graphs_with_precise_on_demand_zoom_detail.md
- logics/tasks/task_023_deliver_bounded_multiresolution_overview_and_exact_zoom_detail_for_historical_traces.md
- src/peaklive/analysis/history.py
- src/peaklive/ui/panels/graph_history.py
- src/peaklive/ui/panels/graph_stack.py
- src/peaklive/ui/panels/graph_navigation.py
- src/peaklive/ui/panels/measurement.py
- src/peaklive/ui/workspace_center.py
- src/peaklive/ui/ingest_controller.py
- src/peaklive/ui/session_controller.py
- src/peaklive/ui/window_shutdown.py
- tests/test_history.py
- tests/test_graph_performance.py

# Backlog
- `item_117_coalesce_historical_viewport_requests_and_own_cancellable_background_reads`
- `item_118_serve_bounded_chronological_multiresolution_history_summaries`
- `item_119_align_historical_navigation_extents_and_measurement_truthfulness`
- `item_120_qualify_large_capture_navigation_with_event_loop_and_packaged_windows_evidence`
