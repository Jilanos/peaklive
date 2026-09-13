## req_027_restore_predictable_panel_geometry_and_reclaim_graph_workspace_space - Restore predictable panel geometry and reclaim graph workspace space
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Stable panel geometry and compact measurement presentation
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-13 15:32:00

# AI Context
- Summary: Defines independent panel visibility and stable geometry plus in-plot titles and one-row A/B/delta, with explicit width-pressure and profile compatibility rules.
- Keywords: restore, predictable, panel, geometry, reclaim, graph, workspace, space
- Use when: Scoping the complete screen-space correction or resolving conflicts with earlier header requirements.
- Skip when: Changing data capture, decoding, retention, or historical curve fidelity.

# Needs
- Restore the operator's splitter positions when Signals, Graphs, or Inspector is reopened with + after being collapsed with -.
- Add independently checked panel-visibility options to the top View menu so a rarely used panel can disappear completely, including its collapsed rail.
- Overlay each signal title inside its own graph at the top, starting just to the right of the Y axis, to reclaim the separate grey title band.
- Display A and B time positions and their temporal delta on the same horizontal command row as fit/resize, Start, Stop, and the existing graph actions.

# Context
- The operator normally keeps Graphs open, often collapses Signals, and rarely uses Inspector. These are usage motivations, not a request to force different visibility defaults on existing profiles.
- The current native Qt shell has three horizontal CollapsiblePanel instances: signals_panel, trace_graph_panel, and inspector_panel. Graphs in this request means the existing central Graphs/Trace/Report container, not an individual plot lane or the workspace mode selector.
- WorkspaceReflow already stores expanded widths. Its center-collapsed branch shares remaining width equally, and _persist_layout calls _remember_panel_widths after reflow. This suggests automatic redistribution can overwrite operator geometry; prove the sequence with settled Qt geometry before changing the algorithm.
- Layout state already persists splitter_sizes, divider_sizes, panel_widths, and collapsed_panels per measurement profile. Additive visibility/preferred-geometry state must tolerate existing saved profiles without losing their settings.
- graph_lane_header.build_lane currently inserts a QLabel above each PlotWidget in a vertical layout. Retain its concise signal name, optional unit, curve colour, and deliberate technical-detail access while moving the title into the drawable area.
- workspace_center deliberately leaves cursor_summary in a separate GraphControlsBar row because of width pressure. This request overrides that implementation choice and narrows item_055 AC3 to one shared command row while preserving complete readable timestamps. The new delta is cursor B minus cursor A, not the previously removed viewport-duration or zoom readout.
- item_112 is still In progress and permits a title inside or above the lane; this follow-up requires inside only. Coordinate overlapping edits during implementation and preserve its other identity, colour, separator, and provenance guarantees. Do not close or rewrite the earlier task merely to scaffold this request.
- This is a new cross-panel space and restoration contract spanning existing presentation areas; the earlier compact-controls product brief is already Settled. Give this coherent follow-up its own brief and reference the earlier backlog requirements.
- No external screenshot is required: reproduce from current code and synthetic signal fixtures. Previously removed logics/external artefacts are not implementation dependencies.

# Acceptance criteria
- AC1: At unchanged window size, a collapse/expand round trip restores all horizontal splitter positions within 2 logical pixels of the last operator layout. Cover Signals, Graphs, Inspector, repeated cycles, and multiple panels collapsed then reopened in either order. Automatic reflow must not become the new preferred layout; genuine splitter drags do update the affected layout preferences.
- AC2: After resize while panels are collapsed or hidden, restoration is deterministic, respects current available width and feasible widget minimums, and retains preferred geometry so it can be restored when space returns. Profile switches and restart preserve preferences without cross-profile leakage; temporary zero/rail geometry during Qt layout settling cannot overwrite them.
- AC3: View offers three keyboard-accessible checked visibility actions for Signals, Graphs/Trace, and Inspector. Unchecking removes the whole panel, including its rail and unused splitter handle space; checking restores its previous expanded/collapsed state and preferred geometry. Collapse remains distinct from hiding. All panels may be hidden and remain recoverable from the top menu.
- AC4: Panel visibility persists per profile; old profiles default to all three panels visible while retaining existing collapse states. Hiding/showing preserves signal selection, graph range, cursors, trace/report mode, Inspector contents, and acquisition state; it neither recreates the analysis session nor changes Start/Stop semantics.
- AC5: Every lane has one concise, curve-coloured title with its optional unit overlaid inside the drawable graph, anchored 2-6 logical pixels from its top-left corner, immediately right of the Y-axis region. There is no dedicated title row, full-width grey band, added top margin, or range padding to accommodate it. The title stays anchored during pan, zoom, resize, and signal-list changes; shared axes and a subtle inter-lane boundary remain aligned.
- AC6: Overlay titles remain legible against traces, keep Y ticks readable, and do not intercept pan, zoom, or A/B dragging beneath them. Long titles are bounded to the lane and may elide with complete identity available by accessible detail/tooltip; default graph hover still omits technical hashes. Cover duplicate display names, units, the raw preview, and dense stacks.
- AC7: The single graph command row shows complete A, B, and signed delta timestamps beside the retained fit/resize, Start/Stop, Follow live, cursor-placement, and measurement-visibility controls. Delta is calculated as B minus A from the unrounded cursor positions; all three values use seconds with three decimal places, normalize display negative zero, update together, and show an explicit unavailable marker independently when a needed cursor is unset.
- AC8: At 1024x768, 1280x720, and 1600x900, the graph-focused workspace with Signals and Inspector hidden displays the command row without clipping, overlap, wrapping, tooltip-only timestamp fallback, or a second readout row, including A=86400.123s and B=86412.468s. When side panels leave insufficient center width, keep A/B/delta and Start/Stop visible and expose lower-frequency commands in an accessible same-row overflow menu; compact labels/icons retain names and tooltips. Report measured minimum center width and handle narrower-than-supported space explicitly rather than silently truncating values.
- AC9: Focused Qt interaction/geometry tests and a Windows visual pass at 100% and 150% scaling demonstrate the reclaimed panel/plot space, restoration and menu recovery, anchored overlay interactions, and synchronized cursor readouts. Existing profile, navigation, measurements, trace/report, acquisition, and historical-curve behaviour remains intact; delivery evidence records the tested configurations and any qualification still outstanding.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_026_peaklive_predictable_and_space_efficient_measurement_workspace`
- Architecture decision(s): (none yet)

# References
- src/peaklive/ui/layout_reflow.py
- src/peaklive/ui/widgets.py
- src/peaklive/ui/main_window.py
- src/peaklive/ui/profile_controller.py
- src/peaklive/ui/actions.py
- src/peaklive/ui/workspace_center.py
- src/peaklive/ui/panels/workspace_header.py
- src/peaklive/ui/panels/graph_lane_header.py
- src/peaklive/ui/panels/graph_controls.py
- src/peaklive/ui/panels/graph_stack.py
- src/peaklive/domain/models.py
- src/peaklive/ui/theme.py
- src/peaklive/i18n/en.json
- tests/test_ui_workspace_refinement.py
- tests/test_ui_compact_graph_and_signal_states.py
- tests/test_ui_graph_comparison.py
- tests/test_ui_analyst.py
- tests/test_profiles.py
- tests/test_graph_navigation.py
- logics/backlog/item_055_simplify_and_make_the_peaklive_graph_command_row_legible.md
- logics/backlog/item_112_render_concise_coloured_graph_lane_titles_with_subtle_lane_separation.md

# Backlog
- `item_126_restore_operator_splitter_geometry_across_panel_collapse_and_expansion`
- `item_127_add_persistent_full_panel_visibility_actions_to_the_view_menu`
- `item_128_overlay_signal_lane_titles_inside_the_drawable_graphs`
- `item_129_place_a_b_and_temporal_delta_readouts_in_the_shared_graph_command_row`
