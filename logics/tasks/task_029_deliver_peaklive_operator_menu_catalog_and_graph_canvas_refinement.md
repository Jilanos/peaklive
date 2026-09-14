## task_029_deliver_peaklive_operator_menu_catalog_and_graph_canvas_refinement - Deliver PeakLive operator menu, catalog, and graph-canvas refinement
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: deliver, peaklive, operator, menu, catalog, graph, canvas, refinement
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Confirm the semantic mapping of Save measurement setup to the existing profile save-as flow and define any migration/shortcut decision before moving commands.
- [ ] 2. Deliver the Recording and Setup menu ownership wave, including safe cascading setting menus, recording-format relocation, lifecycle synchronization, i18n, and regression coverage.
- [ ] 3. Deliver the DBC menu and displayed-signal summary wave while preserving asynchronous catalog ownership and source-of-truth value semantics.
- [ ] 4. Deliver shared graph X-range clamping, full-extent Follow live, fit-control regrouping, and measured gutter reduction without taking over active historical/workspace scope.
- [ ] 5. Run focused and full headless suites, Windows offscreen UI coverage, Ruff, i18n validation, Logics validation, lint, and audit. Record each completed wave with the evidence actually run; this corpus creation does not start implementation.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_135_organize_recording_and_setup_commands_around_safe_profile_ownership`
- `item_136_move_dbc_management_to_its_own_menu_and_summarize_displayed_signals`
- `item_137_bound_graph_time_navigation_and_reclaim_safe_graph_canvas_width`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_135_organize_recording_and_setup_commands_around_safe_profile_ownership`. Proof deferred to slice closeout.
- request-AC2 -> `item_135_organize_recording_and_setup_commands_around_safe_profile_ownership`. Proof deferred to slice closeout.
- request-AC3 -> `item_135_organize_recording_and_setup_commands_around_safe_profile_ownership`. Proof deferred to slice closeout.
- request-AC9 -> `item_135_organize_recording_and_setup_commands_around_safe_profile_ownership`. Proof deferred to slice closeout.
- request-AC4 -> `item_136_move_dbc_management_to_its_own_menu_and_summarize_displayed_signals`. Proof deferred to slice closeout.
- request-AC5 -> `item_136_move_dbc_management_to_its_own_menu_and_summarize_displayed_signals`. Proof deferred to slice closeout.
- request-AC9 -> `item_136_move_dbc_management_to_its_own_menu_and_summarize_displayed_signals`. Proof deferred to slice closeout.
- request-AC6 -> `item_137_bound_graph_time_navigation_and_reclaim_safe_graph_canvas_width`. Proof deferred to slice closeout.
- request-AC7 -> `item_137_bound_graph_time_navigation_and_reclaim_safe_graph_canvas_width`. Proof deferred to slice closeout.
- request-AC8 -> `item_137_bound_graph_time_navigation_and_reclaim_safe_graph_canvas_width`. Proof deferred to slice closeout.
- request-AC9 -> `item_137_bound_graph_time_navigation_and_reclaim_safe_graph_canvas_width`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_030_refine_peaklive_operator_menus_catalog_access_and_graph_navigation`
- Product brief(s): `prod_028_peaklive_focused_operator_controls_and_bounded_measurement_canvas`
- Architecture decision(s): (none yet)
