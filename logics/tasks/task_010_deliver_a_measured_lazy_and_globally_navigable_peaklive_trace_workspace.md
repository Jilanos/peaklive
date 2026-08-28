## task_010_deliver_a_measured_lazy_and_globally_navigable_peaklive_trace_workspace - Deliver a measured, lazy, and globally navigable PeakLive trace workspace
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: rose@circle-mobility.com
> Indicators reviewed: 2026-08-28 20:14:23

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: deliver, measured, lazy, globally, navigable, peaklive, trace, workspace
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Baseline representative trace-load latency, UI responsiveness, memory retention, graph refresh cost, and current viewport behavior with sanitized fixtures.
- [x] 2. Implement bounded critical-path optimizations and stage-level regression budgets for parser, worker, projections, and graph/report updates.
- [x] 3. Implement bounded on-demand signal decoding from the loaded session so signal selection never requires reopening the trace.
- [x] 4. Implement full-capture replay fitting and zero-based expanding acquisition axes while preserving explicit tail-follow navigation.
- [x] 5. Run parser, worker, lazy-selection, viewport, UI responsiveness, full-suite, lint, and cross-platform validation; record evidence for every acceptance criterion.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_036_audit_and_optimize_the_peaklive_trace_loading_critical_path`
- `item_037_support_bounded_on_demand_signal_decoding_after_trace_load`
- `item_038_deliver_full_capture_replay_and_zero_based_live_time_navigation`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> This task. Proof: docs/trace-performance-audit.md records stage timings and a dominant-cost conclusion (trace_projection) for 2k/20k/200k captures, reproduced by scripts/audit_trace_performance.py; asserted by test_the_audit_attributes_a_representative_load_to_every_stage. Source: `1734008`
- request-AC2 -> This task. Proof: Budgets in analysis/profiling.py hold on every stage; worst event-loop pass fell from 4172 ms to 107 ms; asserted by test_the_event_loop_is_serviced_within_the_responsiveness_budget, test_one_coalesced_flush_projects_a_bounded_number_of_trace_rows, test_replay_progress_advances_with_the_consumed_source, test_a_stopped_replay_stops_within_a_bounded_number_of_batches. Source: `1734008`
- request-AC3 -> This task. Proof: A signal selected after the load is derived from the bounded FrameCache without a new replay generation; asserted by test_a_signal_selected_after_the_load_is_derived_from_the_loaded_session and test_repeated_selection_rebuilds_rather_than_duplicates_the_samples. Source: `1734008`
- request-AC4 -> This task. Proof: Backfill is snapshot-based, cancellable, generation-guarded, and reports unavailable or truncated retention; asserted by test_a_backfill_is_bounded_by_the_retained_frames, test_a_cancelled_backfill_installs_nothing, test_a_superseded_backfill_result_is_dropped_on_arrival, test_selecting_a_signal_with_no_retained_session_says_so_plainly. Source: `1734008`
- request-AC5 -> This task. Proof: A completed replay fits the whole capture extent, and the follow-tail checkbox stays the explicit control; asserted by test_a_completed_replay_opens_on_the_whole_capture, test_an_explicit_zoom_outranks_the_full_extent_on_completion, test_follow_tail_is_an_explicit_control_that_restores_the_extent. Source: `1734008`
- request-AC6 -> This task. Proof: A live session's extent starts at zero and expands monotonically even as bounded series age out; asserted by test_a_live_session_starts_its_axis_at_zero, test_a_live_extent_only_ever_grows, test_a_bounded_series_dropping_its_oldest_samples_never_shrinks_the_axis, test_a_live_acquisition_shows_a_zero_based_axis_end_to_end. Source: `1734008`
- request-AC7 -> This task. Proof: The full suite passes unchanged on Linux (QT_QPA_PLATFORM=offscreen uv run python -m pytest, 314 passed) and runs on the ubuntu/windows CI matrix in .github/workflows/ci.yml; retention bounds asserted by test_a_large_load_leaves_every_retained_store_inside_its_bound. Source: `1734008`
- request-AC8 -> This task. Proof: Evidence is machine-checkable and capture-free: tests/test_trace_performance.py, tests/test_lazy_signals.py, and tests/test_graph_navigation.py generate every capture from analysis/benchmark.py. Source: `1734008`
# Validation
- (no validation recorded yet)
- command: `QT_QPA_PLATFORM=offscreen uv run python -m pytest` | result: passed | date: 2026-08-28
- Finish workflow executed on 2026-08-28.
- Linked backlog/request close verification passed.

# Report
- Not started.
- Finished on 2026-08-28.
- Linked backlog item(s): `item_036_audit_and_optimize_the_peaklive_trace_loading_critical_path`, `item_037_support_bounded_on_demand_signal_decoding_after_trace_load`, `item_038_deliver_full_capture_replay_and_zero_based_live_time_navigation`
- Related request(s): `req_009_audit_peaklive_performance_and_make_trace_signal_exploration_and_time_navigation_complete`

# Links
- Request: `req_009_audit_peaklive_performance_and_make_trace_signal_exploration_and_time_navigation_complete`
- Product brief(s): `prod_009_peaklive_fast_explorable_and_globally_navigable_traces`
- Architecture decision(s): (none yet)
