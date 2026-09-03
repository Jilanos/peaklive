## item_053_deliver_distinguishable_graph_traces_and_explicit_graph_fitting_controls - Deliver distinguishable graph traces and explicit graph fitting controls
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: High
> Theme: Graph comparison controls
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-03 15:40:00

# AI Context
- Summary: Give each shown graph an identifiable stable colour and make full-axis fit, Y-only fit, and cursor-measurement visibility deliberate graph controls.
- Keywords: deliver, distinguishable, graph, traces, explicit, fitting, controls
- Use when: An operator cannot distinguish concurrent curves, needs to rescale amplitudes after time zooming, or needs to declutter cursor data.
- Skip when: The request changes signal decoding, captures, numeric statistics, or exported data.

# Problem
- Every curve uses one cyan pen, so overlapping or adjacent signals cannot be rapidly distinguished.
- The current Fit action restores the full X extent but does not express fitting every displayed Y range nor fitting Y while retaining a temporal zoom.
- The cursor measurement table is permanently visible even when its A/B and range statistics distract from graph reading, and its visibility is not stored in a measurement profile.

# Scope
- In:
  - Define a deterministic, colour-blind-considered palette and stable signal-to-colour mapping for simultaneously shown curves, with a non-colour identity fallback in accessible text and tooltips.
  - Add explicit fit-all-axes and fit-Y-only graph actions. Fit-all-axes sets the session X extent and recalculates each shown lane Y range; fit-Y-only recalculates only each shown lane Y range within the present visible X window.
  - Add a compact, accessible measurement-visibility control that hides/restores the values/statistics presentation but leaves A/B vertical cursor lines visible and does not affect calculations or data. Persist this preference in the active measurement profile with a backward-compatible default.
  - Place the Graphs/Trace title, view selection, no-sample state, zoom/resize controls, existing Play/Stop, cursor actions, and timing readouts on one header row, including supported viewport layout tests.
  - Preserve shared X links, cursor positions and lines, follow-live semantics, grid, existing zoom/pan behavior, acquisition lifecycle semantics, profile compatibility, and existing UI tests.
  - Add focused regression tests for colour stability, axis-fit semantics, cursor preservation, control accessibility, compact geometry, and measurement visibility.
- Out:
  - Changing data acquisition, decoding, retention, measurement formulas, exported records, or numeric precision.
  - Implementing manual curve-colour customization or per-signal colour persistence.
  - Changing acquisition lifecycle semantics while moving the existing Play/Stop controls into the graph/trace header.

# Acceptance criteria
- AC1: Every simultaneously shown signal has a visually distinct, deterministic curve colour that remains stable while the graph is refreshed; colour use remains legible on the dark graph background and is exposed in an accessible non-colour-only form.
- AC6: At 1024x768, 1280x720, and 1600x900, one horizontal graph/trace header contains the Graphs/Trace title, view selection (including Graphs only), empty-session state when applicable, zoom and resize controls, Play/Stop, cursor actions, and cursor timing readouts without wrapping, overlap, clipping, or inaccessible hidden actions.
- AC7: The graph offers separate explicit actions for fit X+Y across all shown graphs and fit Y only across all shown graphs while preserving the current visible X range. Both actions handle empty/no-sample state safely, are keyboard reachable, named, tooltip-backed, and do not alter retained samples or cursor positions.
- AC8: An explicit toggle hides and restores cursor measurement values (A, B, delta/count, min, max, mean, RMS, and standard deviation) without hiding A/B vertical cursor lines or changing cursor placement, computed values, graph navigation, or exports. The toggle state is visible, accessible, and persisted in the active measurement profile.
- AC9: Offscreen and focused UI regression tests cover colour assignment/stability, tree affordance contrast and compact geometry, shown/favorite interaction and persistence, combo-box trigger states, one-row control containment, fit semantics, measurement visibility, and preserved existing graph/signal workflows.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: `GraphStackPanel.sync()` assigns each shown curve's pen from `theme.TRACE_PALETTE` by its sorted position in the shown set, recomputed only on shown-set change so colour is stable across `refresh_data()`; each plot carries the signal name as its axis label plus a colour-naming tooltip as the non-colour fallback. Covered by `tests/test_ui_graph_comparison.py::test_simultaneously_shown_signals_get_distinct_stable_colours` and `::test_the_curve_colour_is_named_outside_colour_alone`.
- request-AC6 -> This backlog slice. Proof: new `WorkspaceHeaderBar` (`src/peaklive/ui/panels/workspace_header.py`) composes the title, mode selector, empty-state readout, zoom/fit, reparented Play/Stop, cursor actions, and cursor-summary readout on one row inside `trace_graph_panel`'s own header. Covered at all three bench viewports by `tests/test_ui_workspace_refinement.py::test_the_one_line_graphs_trace_header_stays_readable_at_the_bench_viewports`.
- request-AC7 -> This backlog slice. Proof: `GraphNavigation.fit()` now also calls `enableAutoRange(y=True)` on every shown plot after setting X; new `fit_y()` autoranges Y only, leaving the visible X window untouched; both guard on no plots/extent. Covered by `tests/test_ui_graph_comparison.py::test_fit_y_only_rescales_y_and_preserves_the_visible_x_window`, `::test_fit_x_and_y_resets_the_full_extent`, `::test_fit_actions_handle_the_empty_session_safely`.
- request-AC8 -> This backlog slice. Proof: `MeasurementPanel.set_values_visible()` hides only its own `range_label`/`table`, never `GraphStackPanel`'s A/B `InfiniteLine`s; a new checkable `measurement_visibility_button` drives it and persists via the new `MeasurementProfile.measurement_values_visible` field (default `True`). Covered by `tests/test_ui_graph_comparison.py::test_the_measurement_toggle_hides_values_but_keeps_cursor_lines`, `::test_the_measurement_toggle_state_persists_in_the_profile`, `::test_the_measurement_toggle_defaults_to_visible_for_backward_compatibility`, `::test_the_toggle_is_accessible_and_keyboard_reachable`.
- request-AC9 -> This backlog slice. Proof: `tests/test_ui_graph_comparison.py` (9 tests) and `tests/test_ui_signal_affordances.py` (7 tests) added; existing `tests/test_ui_workspace_refinement.py`, `tests/test_graph_navigation.py` suites updated and green. Full suite green, `ruff check .` clean.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_015_peaklive_unmistakable_graph_comparison_and_signal_controls`
- Architecture decision(s): (none yet)
- Request: `req_015_make_peaklive_graph_comparison_and_signal_controls_unmistakably_legible`
- Primary task(s): `task_016_implement_legible_peaklive_graph_comparison_and_signal_controls`

# Priority
- Priority: High - comparing multiple signals and controlling their viewport are core diagnostic actions, and ambiguous traces or hidden fitting semantics directly obstruct analysis.
- Rationale: Set by scaffold input or defaulted for grooming.
