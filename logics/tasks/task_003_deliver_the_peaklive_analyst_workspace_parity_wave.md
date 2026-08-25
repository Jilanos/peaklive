## task_003_deliver_the_peaklive_analyst_workspace_parity_wave - Deliver the PeakLive analyst workspace parity wave
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 75%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-08-25 11:43:05
> Owner: Claude

# AI Context
- Summary: Orchestrates the ten backlog slices of the second parity wave in dependency order: decompose the monolithic main window first behind a parity regression suite, then fix the inspector and cursor defects, then build measurement, trace, export, report, feedback and ergonomics on top.
- Keywords: orchestration, sequencing, decompose first, offscreen qt validation, bounded pcan smoke
- Use when: Sequencing, tracking or closing out the req_002 analyst workspace parity wave, or deciding which slice to pick up next.
- Skip when: Implementing a single slice in isolation - read that backlog item instead - or any work belonging to the closed req_000 MVP or the closed req_001 parity wave.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Confirm the delta baseline against docs/cantracediag-ux-delta.md and the sibling CanTraceDiag checkout, then refresh the stale logics index.
- [ ] 2. Decompose src/peaklive/ui/main_window.py into focused modules first, behind a regression suite pinning the delivered req_001 parity behaviors, so every later slice lands in a small module instead of the monolith.
- [ ] 3. Fix the two functional defects next: make the inspector selection-driven, and stop the graph refresh from re-pinning operator-placed cursors.
- [ ] 4. Build the analysis primitives - nearest-sample cursor lookup, bounded range statistics, and enum distributions - and render the measurement table on top of them.
- [ ] 5. Deliver the trace view work as one slice: display-only filters with removable chips, then configurable columns with bounded constant-time pruning.
- [ ] 6. Expose the existing CSV and Parquet writers through an export dialog with the A-B, visible-window, and full-buffer scopes, streamed, progress-reporting, and cancellable.
- [ ] 7. Add session fact collection and the diagnostic report view, reusing the anomaly sources already produced by the DBC catalog, the replay reader, and the recorder.
- [ ] 8. Add the bus-state indicator and the explicit empty, error, and loading states across every panel, with progress and cancellation for DBC loading and replay import.
- [ ] 9. Close with ergonomics: shortcuts, tooltips, accessible names, tab order, menu bar, fullscreen, resizable divider, persisted geometry, and the three verified viewport sizes.
- [ ] 10. Validate headless under QT_QPA_PLATFORM=offscreen across the full suite, run ruff, update the architecture and delta documents, then optionally take a PCAN smoke run capped at 2 minutes and close out with Logics lint and audit.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_016_make_the_frame_inspector_selection_driven`
- `item_017_stabilize_a_b_cursors_and_add_graph_time_navigation`
- `item_018_deliver_the_range_measurement_table`
- `item_019_deliver_display_only_trace_filtering_with_active_filter_chips`
- `item_020_deliver_configurable_bounded_trace_columns_and_paging`
- `item_021_expose_streamed_csv_and_parquet_export_from_the_workspace`
- `item_022_deliver_the_session_diagnostic_report`
- `item_023_deliver_bus_state_error_and_loading_feedback`
- `item_024_deliver_keyboard_accessibility_menus_and_layout_persistence`
- `item_025_decompose_the_workspace_ui_into_modules_with_parity_regression_coverage`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_016_make_the_frame_inspector_selection_driven`. Proof deferred to slice closeout.
- request-AC8 -> `item_016_make_the_frame_inspector_selection_driven`. Proof deferred to slice closeout.
- request-AC12 -> `item_016_make_the_frame_inspector_selection_driven`. Proof deferred to slice closeout.
- request-AC2 -> `item_017_stabilize_a_b_cursors_and_add_graph_time_navigation`. Proof deferred to slice closeout.
- request-AC12 -> `item_017_stabilize_a_b_cursors_and_add_graph_time_navigation`. Proof deferred to slice closeout.
- request-AC3 -> `item_018_deliver_the_range_measurement_table`. Proof deferred to slice closeout.
- request-AC12 -> `item_018_deliver_the_range_measurement_table`. Proof deferred to slice closeout.
- request-AC4 -> `item_019_deliver_display_only_trace_filtering_with_active_filter_chips`. Proof deferred to slice closeout.
- request-AC12 -> `item_019_deliver_display_only_trace_filtering_with_active_filter_chips`. Proof deferred to slice closeout.
- request-AC5 -> `item_020_deliver_configurable_bounded_trace_columns_and_paging`. Proof deferred to slice closeout.
- request-AC12 -> `item_020_deliver_configurable_bounded_trace_columns_and_paging`. Proof deferred to slice closeout.
- request-AC6 -> `item_021_expose_streamed_csv_and_parquet_export_from_the_workspace`. Proof deferred to slice closeout.
- request-AC12 -> `item_021_expose_streamed_csv_and_parquet_export_from_the_workspace`. Proof deferred to slice closeout.
- request-AC7 -> `item_022_deliver_the_session_diagnostic_report`. Proof deferred to slice closeout.
- request-AC12 -> `item_022_deliver_the_session_diagnostic_report`. Proof deferred to slice closeout.
- request-AC8 -> `item_023_deliver_bus_state_error_and_loading_feedback`. Proof deferred to slice closeout.
- request-AC12 -> `item_023_deliver_bus_state_error_and_loading_feedback`. Proof deferred to slice closeout.
- request-AC9 -> `item_024_deliver_keyboard_accessibility_menus_and_layout_persistence`. Proof deferred to slice closeout.
- request-AC10 -> `item_024_deliver_keyboard_accessibility_menus_and_layout_persistence`. Proof deferred to slice closeout.
- request-AC12 -> `item_024_deliver_keyboard_accessibility_menus_and_layout_persistence`. Proof deferred to slice closeout.
- request-AC11 -> `item_025_decompose_the_workspace_ui_into_modules_with_parity_regression_coverage`. Proof deferred to slice closeout.
- request-AC12 -> `item_025_decompose_the_workspace_ui_into_modules_with_parity_regression_coverage`. Proof deferred to slice closeout.
- request-AC13 -> `item_025_decompose_the_workspace_ui_into_modules_with_parity_regression_coverage`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_002_complete_the_peaklive_analyst_workspace_to_cantracediag_parity`
- Product brief(s): `prod_003_peaklive_analyst_measurement_and_reporting_workspace`
- Architecture decision(s): (none yet)
