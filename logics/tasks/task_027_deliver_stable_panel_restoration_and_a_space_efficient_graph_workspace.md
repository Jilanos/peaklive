## task_027_deliver_stable_panel_restoration_and_a_space_efficient_graph_workspace - Deliver stable panel restoration and a space-efficient graph workspace
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 25%
> Complexity: High
> Theme: Stable panel geometry and compact measurement presentation
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-13 15:34:34
> Owner: maintainer@example.invalid

# AI Context
- Summary: Deliver four implementation waves with geometry and visibility first, then title overlays and compact cursor timing; require Qt and Windows evidence.
- Keywords: deliver, stable, panel, restoration, space, efficient, graph, workspace
- Use when: Implementing this request, sequencing its dependencies, and recording acceptance evidence for closeout.
- Skip when: Scaffolding unrelated features or closing earlier active graph work.

# Context
- Deliver the four linked implementation slices against request AC1-AC9. Geometry restoration precedes visibility; integrate title and toolbar changes with the existing lane identity and cursor contracts.

# Plan
- [x] 1. Wave 1 (High): Reproduce the toggle geometry defect at settled Qt event boundaries; implement and validate preferred-versus-allocated geometry, mixed collapse sequences, resizing, and profile round trips. Record tests and the chosen allocation policy in this task before committing the wave.
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
- Wave 1 (item_126) allocation policy: separated the single `_expanded_widths` store into a strict preferred-width cache that is only updated by an explicit operator action. `_remember_panel_widths(only=<panel>)` now scopes the capture to the one panel whose `collapsed_changed` signal actually fired (via `self.sender()`), never its siblings, and `_persist_layout()` no longer calls `_remember_panel_widths` at all — only `_splitter_dragged()` (wired to `QSplitter.splitterMoved`) and `_panel_collapse_changed()` do, each before any reflow runs. This stops two corruption paths: (a) `_persist_layout`'s old unconditional re-remember after `_reflow_workspace` had already applied an automatic equal-share split when the centre panel collapsed, and (b) a sibling panel's currently-allocated (not preferred) width being captured just because a different panel's collapse state changed, e.g. the sole remaining open side panel absorbing 100% of the released width and then having that absorbed value promoted to "preferred" when a third panel was reopened. `reflow_widths` itself (src/peaklive/ui/layout_reflow.py) is unchanged: hidden-panel concept is out of scope for Wave 1 (added in Wave 2/item_127); collapsed panels consume `RAIL_WIDTH`; open panels respect `MIN_SIDE_WIDTH`/`MIN_CENTER_WIDTH`; the centre absorbs released space.
- Wave 1 tests (all passing, `QT_QPA_PLATFORM=offscreen uv run pytest tests/test_ui_workspace_refinement.py tests/test_profiles.py tests/test_ui_compact_graph_and_signal_states.py tests/test_ui_graph_comparison.py tests/test_ui_analyst.py tests/test_graph_navigation.py tests/test_debounced_persistence.py tests/test_profile_save_as_ui.py -q`, 216 passed):
  - `test_collapsing_the_centre_panel_does_not_corrupt_side_panel_preferences` (new): reproduced item_126 AC1 (failed before the fix — signals/inspector width collapsed to the automatic equal split of ~607/607 instead of the dragged 340/240 after Graphs was reopened; passes after the fix, both within 2px).
  - `test_mixed_non_lifo_collapse_sequences_restore_each_panels_own_width` (new): reproduced the second corruption path (failed before the fix — reopening signals last returned 290 instead of the dragged 360, because inspector's automatically-absorbed width from an earlier reflow got laundered into "preferred" when a sibling toggled; passes after the fix).
  - `test_resize_small_then_expand_then_resize_back_keeps_allocation_sane` (new): item_126 AC2, no negative widths through a small/large/original resize cycle, allocation returns within 8px of the dragged widths.
  - `test_switching_profiles_preserves_each_profiles_own_widths` (new): item_126 AC3, two profiles keep independent widths across `_profile_changed`.
  - `test_a_malformed_partial_panel_widths_mapping_still_loads` (new): item_126 AC3/AC4, a `panel_widths` dict missing a key still loads and falls back to `MIN_SIDE_WIDTH`, reusing the existing `ProfileStore`/domain sanitisation already covered by `test_an_unusable_stored_width_falls_back_to_a_safe_default`.
  - Existing geometry tests (`test_expanding_restores_the_remembered_width_and_the_content`, `test_the_collapsed_state_and_remembered_width_persist_per_profile`, `tests/test_ui_analyst.py::test_layout_geometry_and_collapse_state_persist_across_a_restart`) updated to call the new `_splitter_dragged()` entry point instead of `_persist_layout()` directly to simulate an explicit drag, since `_persist_layout()` itself no longer remembers widths (see rationale above); behaviour asserted is unchanged.
- Lint: `uv run ruff check src/peaklive/ui/layout_reflow.py src/peaklive/ui/main_window.py src/peaklive/ui/profile_controller.py tests/test_ui_analyst.py tests/test_ui_workspace_refinement.py` — all checks passed.
- Not yet run: Wave 1 does not on its own require Windows visual qualification (task Plan item 7 covers the integrated result after all four waves); deferred to the final task-level closeout.

# Report
- Wave 1 (item_126) implemented and committed: `src/peaklive/ui/layout_reflow.py`, `src/peaklive/ui/main_window.py`, `src/peaklive/ui/profile_controller.py`, `tests/test_ui_workspace_refinement.py`, `tests/test_ui_analyst.py`. See Validation above for the allocation policy and test evidence. Waves 2-4 (item_127, item_128, item_129) not started.

# Links
- Request: `req_027_restore_predictable_panel_geometry_and_reclaim_graph_workspace_space`
- Product brief(s): `prod_026_peaklive_predictable_and_space_efficient_measurement_workspace`
- Architecture decision(s): (none yet)
