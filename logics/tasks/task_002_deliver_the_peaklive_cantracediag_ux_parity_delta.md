## task_002_deliver_the_peaklive_cantracediag_ux_parity_delta - Deliver the PeakLive CanTraceDiag UX parity delta
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 95%
> Confidence: 90%
> Progress: 70%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: codex
> Indicators reviewed: 2026-08-24 14:35:25

# AI Context
- Summary: Orchestrates the PeakLive CanTraceDiag UX parity request from delta analysis through DBC, acquisition, signal, graph, layout, visual, and validation slices.
- Keywords: deliver, peaklive, cantracediag, parity, delta
- Use when: Coordinating or implementing the UX parity delivery and deciding which ready backlog slice should run next.
- Skip when: Working on unrelated PeakLive maintenance, low-level driver fixes, or long hardware qualification outside the bounded UX validation scope.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Capture the CanTraceDiag-to-PeakLive UX delta and convert it into a Qt-specific implementation and validation map.
- [ ] 2. Implement multi-DBC library, parsing diagnostics, DBC enable/remove state, and conflict resolution first because the signal explorer depends on it.
- [ ] 3. Add the acquisition setup panel with bitrate and controller-mode semantics while preserving the application receive-only MVP boundary.
- [ ] 4. Implement the DBC/message-grouped signal explorer with search, favorites, shown filtering, and clickable plot selection.
- [ ] 5. Add multi-graph rendering, A/B cursors, readouts, graph/trace combo configurations, and collapsible panels.
- [ ] 6. Apply the CanTraceDiag-aligned instrument visual system across the refined workspace.
- [ ] 7. Validate with fake/replay/fixture automation and, if useful, an optional PCAN smoke test capped at 2 minutes; then close out with Logics lint and audit.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_009_analyze_the_cantracediag_to_peaklive_ux_delta`
- `item_010_deliver_multi_dbc_library_and_conflict_management`
- `item_011_upgrade_acquisition_setup_controls`
- `item_012_bring_the_signal_explorer_to_cantracediag_parity`
- `item_013_deliver_multi_graph_measurements_and_configurable_workspace_panels`
- `item_014_apply_the_cantracediag_instrument_visual_system_to_peaklive`
- `item_015_validate_the_ux_parity_delivery_with_bounded_hardware_evidence`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_009_analyze_the_cantracediag_to_peaklive_ux_delta`. Proof deferred to slice closeout.
- request-AC7 -> `item_009_analyze_the_cantracediag_to_peaklive_ux_delta`. Proof deferred to slice closeout.
- request-AC8 -> `item_009_analyze_the_cantracediag_to_peaklive_ux_delta`. Proof deferred to slice closeout.
- request-AC9 -> `item_009_analyze_the_cantracediag_to_peaklive_ux_delta`. Proof deferred to slice closeout.
- request-AC2 -> `item_010_deliver_multi_dbc_library_and_conflict_management`. Proof deferred to slice closeout.
- request-AC4 -> `item_010_deliver_multi_dbc_library_and_conflict_management`. Proof deferred to slice closeout.
- request-AC8 -> `item_010_deliver_multi_dbc_library_and_conflict_management`. Proof deferred to slice closeout.
- request-AC9 -> `item_010_deliver_multi_dbc_library_and_conflict_management`. Proof deferred to slice closeout.
- request-AC3 -> `item_011_upgrade_acquisition_setup_controls`. Proof deferred to slice closeout.
- request-AC6 -> `item_011_upgrade_acquisition_setup_controls`. Proof deferred to slice closeout.
- request-AC8 -> `item_011_upgrade_acquisition_setup_controls`. Proof deferred to slice closeout.
- request-AC9 -> `item_011_upgrade_acquisition_setup_controls`. Proof deferred to slice closeout.
- request-AC4 -> `item_012_bring_the_signal_explorer_to_cantracediag_parity`. Proof deferred to slice closeout.
- request-AC6 -> `item_012_bring_the_signal_explorer_to_cantracediag_parity`. Proof deferred to slice closeout.
- request-AC7 -> `item_012_bring_the_signal_explorer_to_cantracediag_parity`. Proof deferred to slice closeout.
- request-AC8 -> `item_012_bring_the_signal_explorer_to_cantracediag_parity`. Proof deferred to slice closeout.
- request-AC9 -> `item_012_bring_the_signal_explorer_to_cantracediag_parity`. Proof deferred to slice closeout.
- request-AC5 -> `item_013_deliver_multi_graph_measurements_and_configurable_workspace_panels`. Proof deferred to slice closeout.
- request-AC6 -> `item_013_deliver_multi_graph_measurements_and_configurable_workspace_panels`. Proof deferred to slice closeout.
- request-AC7 -> `item_013_deliver_multi_graph_measurements_and_configurable_workspace_panels`. Proof deferred to slice closeout.
- request-AC8 -> `item_013_deliver_multi_graph_measurements_and_configurable_workspace_panels`. Proof deferred to slice closeout.
- request-AC9 -> `item_013_deliver_multi_graph_measurements_and_configurable_workspace_panels`. Proof deferred to slice closeout.
- request-AC1 -> `item_014_apply_the_cantracediag_instrument_visual_system_to_peaklive`. Proof deferred to slice closeout.
- request-AC7 -> `item_014_apply_the_cantracediag_instrument_visual_system_to_peaklive`. Proof deferred to slice closeout.
- request-AC8 -> `item_014_apply_the_cantracediag_instrument_visual_system_to_peaklive`. Proof deferred to slice closeout.
- request-AC8 -> `item_015_validate_the_ux_parity_delivery_with_bounded_hardware_evidence`. Proof deferred to slice closeout.
- request-AC9 -> `item_015_validate_the_ux_parity_delivery_with_bounded_hardware_evidence`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_001_bring_peaklive_ux_to_cantracediag_parity`
- Product brief(s): `prod_002_peaklive_cantracediag_grade_diagnostic_workspace`
- Architecture decision(s): (none yet)
