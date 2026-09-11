## task_025_deliver_responsive_and_faithful_historical_graph_navigation - Deliver responsive and faithful historical graph navigation
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 95%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-11 16:00:33
> Owner: Codex

# AI Context
- Summary: Sequence scheduler ownership, bounded history summaries, analytical truthfulness and Windows navigation qualification.
- Keywords: deliver, responsive, faithful, historical, graph, navigation
- Use when: Implementing this measured regression end to end; begin with the diagnosis and preserve prior request evidence.
- Skip when: Closing on small-series tests or treating the current documentation as implementation proof.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Record the supplied source-level diagnosis and baseline; capture build identity, machine characteristics and actual selected-signal configuration for executable qualification.
- [ ] 2. Implement the request scheduler and worker ownership first, proving coalescing and lifecycle safety while clearly retaining the unresolved raw-scan cost.
- [ ] 3. Implement and integrate indexed resolution summaries, cached extents and bounded exact queries; prove late-interval coverage and stable chronological extrema before performance claims.
- [ ] 4. Align fit/follow, UI detail states, missing historical coverage and A/B truthfulness. Avoid unrelated acquisition/export changes.
- [ ] 5. Run deterministic structural/correctness tests and real event-loop navigation with 1/4/8 lanes, scaling and cache endurance; measure separately cold-index construction and indexed-query readiness.
- [ ] 6. Qualify an identifiable Windows executable and the private capture when available; record AC-by-AC evidence, Logics validation and outstanding limitations before closeout.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_117_coalesce_historical_viewport_requests_and_own_cancellable_background_reads`
- `item_118_serve_bounded_chronological_multiresolution_history_summaries`
- `item_119_align_historical_navigation_extents_and_measurement_truthfulness`
- `item_120_qualify_large_capture_navigation_with_event_loop_and_packaged_windows_evidence`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_117_coalesce_historical_viewport_requests_and_own_cancellable_background_reads`. Proof deferred to slice closeout.
- request-AC2 -> `item_117_coalesce_historical_viewport_requests_and_own_cancellable_background_reads`. Proof deferred to slice closeout.
- request-AC6 -> `item_117_coalesce_historical_viewport_requests_and_own_cancellable_background_reads`. Proof deferred to slice closeout.
- request-AC7 -> `item_117_coalesce_historical_viewport_requests_and_own_cancellable_background_reads`. Proof deferred to slice closeout.
- request-AC1 -> `item_118_serve_bounded_chronological_multiresolution_history_summaries`. Proof deferred to slice closeout.
- request-AC3 -> `item_118_serve_bounded_chronological_multiresolution_history_summaries`. Proof deferred to slice closeout.
- request-AC4 -> `item_118_serve_bounded_chronological_multiresolution_history_summaries`. Proof deferred to slice closeout.
- request-AC6 -> `item_118_serve_bounded_chronological_multiresolution_history_summaries`. Proof deferred to slice closeout.
- request-AC7 -> `item_118_serve_bounded_chronological_multiresolution_history_summaries`. Proof deferred to slice closeout.
- request-AC4 -> `item_119_align_historical_navigation_extents_and_measurement_truthfulness`. Proof deferred to slice closeout.
- request-AC5 -> `item_119_align_historical_navigation_extents_and_measurement_truthfulness`. Proof deferred to slice closeout.
- request-AC6 -> `item_119_align_historical_navigation_extents_and_measurement_truthfulness`. Proof deferred to slice closeout.
- request-AC7 -> `item_119_align_historical_navigation_extents_and_measurement_truthfulness`. Proof deferred to slice closeout.
- request-AC1 -> `item_120_qualify_large_capture_navigation_with_event_loop_and_packaged_windows_evidence`. Proof deferred to slice closeout.
- request-AC2 -> `item_120_qualify_large_capture_navigation_with_event_loop_and_packaged_windows_evidence`. Proof deferred to slice closeout.
- request-AC3 -> `item_120_qualify_large_capture_navigation_with_event_loop_and_packaged_windows_evidence`. Proof deferred to slice closeout.
- request-AC4 -> `item_120_qualify_large_capture_navigation_with_event_loop_and_packaged_windows_evidence`. Proof deferred to slice closeout.
- request-AC5 -> `item_120_qualify_large_capture_navigation_with_event_loop_and_packaged_windows_evidence`. Proof deferred to slice closeout.
- request-AC6 -> `item_120_qualify_large_capture_navigation_with_event_loop_and_packaged_windows_evidence`. Proof deferred to slice closeout.
- request-AC7 -> `item_120_qualify_large_capture_navigation_with_event_loop_and_packaged_windows_evidence`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Implemented and committed scheduler debounce and chronological bounded overview correction in 90d87e1. Focused validation passed: PYTHONPATH=src .venv-win/Scripts/python.exe -m pytest tests/test_history.py tests/test_graph_navigation.py tests/test_graph_performance.py (25 passed); Ruff passed. Full pytest was started and reached 63% without reported failures, then was stopped after a long silent integration test. Remaining task scope: worker-owned asynchronous historical queries, indexed multiresolution hierarchy, historical measurement truthfulness, and packaged Windows latency qualification.
- Added HistoryViewportWorker with worker-owned SQLite connection, generation checks and cancellation; historical refresh now runs off GUI thread and session reset/close cancels it. Commit c8671a8 plus lifecycle follow-up pending. Focused history/performance tests and Ruff pass. Full graph_navigation integration reaches the long live acquisition case but does not complete within the bounded command window; packaged Windows latency qualification remains outstanding.
- Validation checkpoint: 50 focused tests passed in 92.96s across graph navigation, graph performance, history, trace performance, UI graph comparison and replay worker. Ruff passed. Added bounded 64,000-point viewport result cache with session invalidation in commits ce78204/c9f6fd2. AC2 worker ownership, debounce, generation cancellation and lifecycle cleanup are implemented. AC4 envelope ordering/late extrema is covered by deterministic tests. AC3 broad-view precomputed SQLite resolution hierarchy, AC5 historical exact measurement contract, and AC1/AC7 packaged Windows latency qualification remain explicitly open; task must not close until those are implemented and evidenced.
- Added SQLite overview_cache materialization with transactional invalidation on append (commit 4b2f330). This removes repeated scans for identical historical viewports while preserving source samples. Full focused regression command passed: 50 tests across navigation, performance, history, trace performance, UI graph comparison and replay worker. Ruff and Logics lint pass. Remaining evidence gap is explicit: no 1/4/8-lane packaged Windows latency qualification and A/B historical exact measurement consumer; these must be implemented or the task cannot be closed.
- Implemented persistent SQLite summary levels (10ms through 10,000s) with per-bucket first/last/min/max source samples and indexed lookup; broad overview queries use the selected level before raw fallback. Commit e39a365/d6b5b4d. History and graph tests pass, and the full focused regression set (50 tests) passes. AC1 responsiveness target and AC5 historical exact measurement semantics still require explicit packaged Windows benchmark and measurement consumer proof; not marked complete.

# Links
- Request: `req_025_restore_responsive_and_faithful_historical_graph_navigation`
- Product brief(s): `prod_024_peaklive_responsive_and_faithful_historical_navigation_correction`
- Architecture decision(s): (none yet)
