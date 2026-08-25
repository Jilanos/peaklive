## task_003_deliver_the_peaklive_analyst_workspace_parity_wave - Deliver the PeakLive analyst workspace parity wave
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-08-25 12:29:44
> Owner: Claude

# AI Context
- Summary: Orchestrates the ten backlog slices of the second parity wave in dependency order: decompose the monolithic main window first behind a parity regression suite, then fix the inspector and cursor defects, then build measurement, trace, export, report, feedback and ergonomics on top.
- Keywords: orchestration, sequencing, decompose first, offscreen qt validation, bounded pcan smoke
- Use when: Sequencing, tracking or closing out the req_002 analyst workspace parity wave, or deciding which slice to pick up next.
- Skip when: Implementing a single slice in isolation - read that backlog item instead - or any work belonging to the closed req_000 MVP or the closed req_001 parity wave.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Confirm the delta baseline against docs/cantracediag-ux-delta.md and the sibling CanTraceDiag checkout, then refresh the stale logics index.
- [x] 2. Decompose src/peaklive/ui/main_window.py into focused modules first, behind a regression suite pinning the delivered req_001 parity behaviors, so every later slice lands in a small module instead of the monolith.
- [x] 3. Fix the two functional defects next: make the inspector selection-driven, and stop the graph refresh from re-pinning operator-placed cursors.
- [x] 4. Build the analysis primitives - nearest-sample cursor lookup, bounded range statistics, and enum distributions - and render the measurement table on top of them.
- [x] 5. Deliver the trace view work as one slice: display-only filters with removable chips, then configurable columns with bounded constant-time pruning.
- [x] 6. Expose the existing CSV and Parquet writers through an export dialog with the A-B, visible-window, and full-buffer scopes, streamed, progress-reporting, and cancellable.
- [x] 7. Add session fact collection and the diagnostic report view, reusing the anomaly sources already produced by the DBC catalog, the replay reader, and the recorder.
- [x] 8. Add the bus-state indicator and the explicit empty, error, and loading states across every panel, with progress and cancellation for DBC loading and replay import.
- [x] 9. Close with ergonomics: shortcuts, tooltips, accessible names, tab order, menu bar, fullscreen, resizable divider, persisted geometry, and the three verified viewport sizes.
- [x] 10. Validate headless under QT_QPA_PLATFORM=offscreen across the full suite, run ruff, update the architecture and delta documents, then optionally take a PCAN smoke run capped at 2 minutes and close out with Logics lint and audit.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

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
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC8 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC12 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC2 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC12 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC3 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC12 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC4 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC12 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC5 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC12 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC6 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC12 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC7 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC12 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC8 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC12 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC9 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC10 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC12 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC11 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC12 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`
- request-AC13 -> This task. Proof: Implemented across f5b7038 (analysis primitives), 0876927 (UI decomposition), 162a6c6 (analyst workspace), 4953082 (filter bar + i18n), ab20feb (docs); validated headless with QT_QPA_PLATFORM=offscreen uv run pytest (148 passed) and uv run ruff check . Source: `36c68d8`

# Validation
- (no validation recorded yet)
- command: `QT_QPA_PLATFORM=offscreen uv run pytest && uv run ruff check .` | result: passed | date: 2026-08-25
- Finish workflow executed on 2026-08-25.
- Linked backlog/request close verification passed.

# Report
- Not started.
- Finished on 2026-08-25.
- Linked backlog item(s): `item_016_make_the_frame_inspector_selection_driven`, `item_017_stabilize_a_b_cursors_and_add_graph_time_navigation`, `item_018_deliver_the_range_measurement_table`, `item_019_deliver_display_only_trace_filtering_with_active_filter_chips`, `item_020_deliver_configurable_bounded_trace_columns_and_paging`, `item_021_expose_streamed_csv_and_parquet_export_from_the_workspace`, `item_022_deliver_the_session_diagnostic_report`, `item_023_deliver_bus_state_error_and_loading_feedback`, `item_024_deliver_keyboard_accessibility_menus_and_layout_persistence`, `item_025_decompose_the_workspace_ui_into_modules_with_parity_regression_coverage`
- Related request(s): `req_002_complete_the_peaklive_analyst_workspace_to_cantracediag_parity`

# Links
- Request: `req_002_complete_the_peaklive_analyst_workspace_to_cantracediag_parity`
- Product brief(s): `prod_003_peaklive_analyst_measurement_and_reporting_workspace`
- Architecture decision(s): (none yet)
