## task_027_deliver_stable_panel_restoration_and_a_space_efficient_graph_workspace - Deliver stable panel restoration and a space-efficient graph workspace
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Stable panel geometry and compact measurement presentation
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-13 15:32:01

# AI Context
- Summary: Deliver four implementation waves with geometry and visibility first, then title overlays and compact cursor timing; require Qt and Windows evidence.
- Keywords: deliver, stable, panel, restoration, space, efficient, graph, workspace
- Use when: Implementing this request, sequencing its dependencies, and recording acceptance evidence for closeout.
- Skip when: Scaffolding unrelated features or closing earlier active graph work.

# Context
- Deliver the four linked implementation slices against request AC1-AC9. Geometry restoration precedes visibility; integrate title and toolbar changes with the existing lane identity and cursor contracts.

# Plan
- [ ] 1. Wave 1 (High): Reproduce the toggle geometry defect at settled Qt event boundaries; implement and validate preferred-versus-allocated geometry, mixed collapse sequences, resizing, and profile round trips. Record tests and the chosen allocation policy in this task before committing the wave.
- [ ] 2. Wave 2 (High, depends on Wave 1): Add independent persistent visibility and synchronized View menu actions. Verify rail-space recovery, all-hidden recovery, keyboard reveal, acquisition availability, and preserved session state; record and commit the completed wave.
- [ ] 3. Wave 3 (Medium): Coordinate existing item_112 edits, move lane titles into the ViewBox, and verify anchoring, height gain, accessible identity, and gesture pass-through for 1/3/8 lanes. Record and commit the completed wave.
- [ ] 4. Wave 4 (Medium, integrate after Wave 2): Consolidate A/B/delta into the command row with the explicit width and overflow policy. Validate numerical edge cases, supported resolutions, side-panel pressure, and absence of a second row; record and commit the completed wave.
- [ ] 5. Before new user-facing labels, run logics-manager i18n status and follow the existing translation contract; validate i18n after copy changes. Use synthetic fixtures and avoid dependencies on removed external artefacts.
- [ ] 6. Run QT_QPA_PLATFORM=offscreen pytest tests/test_ui_workspace_refinement.py tests/test_ui_compact_graph_and_signal_states.py tests/test_ui_graph_comparison.py tests/test_ui_analyst.py tests/test_profiles.py tests/test_graph_navigation.py plus new focused tests in the project environment. Run the repository lint and required CI checks in proportion to changed modules.
- [ ] 7. Qualify the integrated Windows application at 1024x768, 1280x720, and 1600x900 with 100%/150% scaling where feasible. Record actual logical viewport, splitter positions before/after, title/plot bounds, toolbar containment, screenshots with synthetic data, and any unavailable platform checks; offscreen tests alone do not prove Windows visual acceptance.
- [ ] 8. Map every request AC to concrete test/visual evidence, run Logics lint and audit, and use flow closeout only when implemented and qualified. This scaffold is planning only; do not start or finish implementation tasks during corpus creation.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Commit each completed meaningful wave with implementation, regression coverage, and updated Logics evidence as required by the repository instructions.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_126_restore_operator_splitter_geometry_across_panel_collapse_and_expansion`
- `item_127_add_persistent_full_panel_visibility_actions_to_the_view_menu`
- `item_128_overlay_signal_lane_titles_inside_the_drawable_graphs`
- `item_129_place_a_b_and_temporal_delta_readouts_in_the_shared_graph_command_row`

# Definition of Done (DoD)
- [ ] All four slices are implemented and request AC1-AC9 have concrete evidence.
- [ ] Geometry round trips, mixed hide/collapse states, all-hidden recovery, and legacy profile round trips pass.
- [ ] In-plot titles reclaim height, preserve accessible identity, and pass through graph gestures.
- [ ] Complete A/B/delta share the command row, with tested formatting and width-pressure behaviour.
- [ ] Focused Qt regressions, required repository checks, and Windows visual qualification pass; unavailable qualification is recorded and prevents claiming full completion.
- [ ] Meaningful waves follow ADR 009 with updated docs and commits; context pack and acceptance traceability reflect the delivered state.

# AC Traceability
- request-AC1 -> `item_126_restore_operator_splitter_geometry_across_panel_collapse_and_expansion`. Proof deferred to slice closeout.
- request-AC2 -> `item_126_restore_operator_splitter_geometry_across_panel_collapse_and_expansion`. Proof deferred to slice closeout.
- request-AC9 -> `item_126_restore_operator_splitter_geometry_across_panel_collapse_and_expansion`. Proof deferred to slice closeout.
- request-AC2 -> `item_127_add_persistent_full_panel_visibility_actions_to_the_view_menu`. Proof deferred to slice closeout.
- request-AC3 -> `item_127_add_persistent_full_panel_visibility_actions_to_the_view_menu`. Proof deferred to slice closeout.
- request-AC4 -> `item_127_add_persistent_full_panel_visibility_actions_to_the_view_menu`. Proof deferred to slice closeout.
- request-AC9 -> `item_127_add_persistent_full_panel_visibility_actions_to_the_view_menu`. Proof deferred to slice closeout.
- request-AC5 -> `item_128_overlay_signal_lane_titles_inside_the_drawable_graphs`. Proof deferred to slice closeout.
- request-AC6 -> `item_128_overlay_signal_lane_titles_inside_the_drawable_graphs`. Proof deferred to slice closeout.
- request-AC9 -> `item_128_overlay_signal_lane_titles_inside_the_drawable_graphs`. Proof deferred to slice closeout.
- request-AC7 -> `item_129_place_a_b_and_temporal_delta_readouts_in_the_shared_graph_command_row`. Proof deferred to slice closeout.
- request-AC8 -> `item_129_place_a_b_and_temporal_delta_readouts_in_the_shared_graph_command_row`. Proof deferred to slice closeout.
- request-AC9 -> `item_129_place_a_b_and_temporal_delta_readouts_in_the_shared_graph_command_row`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_027_restore_predictable_panel_geometry_and_reclaim_graph_workspace_space`
- Product brief(s): `prod_026_peaklive_predictable_and_space_efficient_measurement_workspace`
- Architecture decision(s): (none yet)
