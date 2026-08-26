## task_004_deliver_the_peaklive_visual_usability_and_responsive_workspace_refinement - Deliver the PeakLive visual usability and responsive workspace refinement
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-08-26 16:24:36
> Owner: rose@circle-mobility.com

# AI Context
- Summary: Deliver the three coordinated usability slices while preserving current DBC, signal, cursor, trace, and profile behavior.
- Keywords: deliver, peaklive, visual, usability, responsive, workspace, refinement
- Use when: Implementing the ready visual-usability request from shared theme rules through responsive workspace regression coverage.
- Skip when: Implementing unrelated acquisition, decoding, reporting, or export capabilities.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Establish the shared contrast and control-state contract, then implement and test the name-first signal explorer without changing DBC semantics.
- [ ] 2. Implement the selected collapsed-panel interaction and migrate splitter persistence so collapsed panels reclaim space safely.
- [ ] 3. Recompose graph controls and graph/trace/report defaults around responsive geometry, preserving all existing measurement behaviors.
- [ ] 4. Run offscreen regression coverage, Logics validation, lint, and audit; record task-closeout evidence only when implementation is complete.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_026_make_signal_selection_compact_name_first_and_state_legible`
- `item_027_restore_full_dark_theme_control_and_menu_legibility`
- `item_028_reclaim_collapsed_panel_space_and_reorganize_graph_workspace_controls`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_026_make_signal_selection_compact_name_first_and_state_legible`. Proof deferred to slice closeout.
- request-AC2 -> `item_026_make_signal_selection_compact_name_first_and_state_legible`. Proof deferred to slice closeout.
- request-AC3 -> `item_026_make_signal_selection_compact_name_first_and_state_legible`. Proof deferred to slice closeout.
- request-AC7 -> `item_026_make_signal_selection_compact_name_first_and_state_legible`. Proof deferred to slice closeout.
- request-AC8 -> `item_026_make_signal_selection_compact_name_first_and_state_legible`. Proof deferred to slice closeout.
- request-AC3 -> `item_027_restore_full_dark_theme_control_and_menu_legibility`. Proof deferred to slice closeout.
- request-AC7 -> `item_027_restore_full_dark_theme_control_and_menu_legibility`. Proof deferred to slice closeout.
- request-AC8 -> `item_027_restore_full_dark_theme_control_and_menu_legibility`. Proof deferred to slice closeout.
- request-AC4 -> `item_028_reclaim_collapsed_panel_space_and_reorganize_graph_workspace_controls`. Proof deferred to slice closeout.
- request-AC5 -> `item_028_reclaim_collapsed_panel_space_and_reorganize_graph_workspace_controls`. Proof deferred to slice closeout.
- request-AC6 -> `item_028_reclaim_collapsed_panel_space_and_reorganize_graph_workspace_controls`. Proof deferred to slice closeout.
- request-AC7 -> `item_028_reclaim_collapsed_panel_space_and_reorganize_graph_workspace_controls`. Proof deferred to slice closeout.
- request-AC8 -> `item_028_reclaim_collapsed_panel_space_and_reorganize_graph_workspace_controls`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_003_improve_peaklive_workspace_visual_usability_and_panel_density`
- Product brief(s): `prod_004_peaklive_dense_and_legible_diagnostic_workspace`
- Architecture decision(s): (none yet)
