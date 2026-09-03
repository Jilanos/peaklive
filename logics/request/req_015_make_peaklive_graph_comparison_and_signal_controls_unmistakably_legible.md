## req_015_make_peaklive_graph_comparison_and_signal_controls_unmistakably_legible - Make PeakLive graph comparison and signal controls unmistakably legible
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Graph comparison and signal-control legibility
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-03 14:53:23

# AI Context
- Summary: Make multi-signal graph comparison and the dark-theme signal-selection controls easy to identify, operate, and verify without changing CAN analysis.
- Keywords: peaklive, graph, comparison, signal, controls, unmistakably, legible
- Use when: Curves share an indistinguishable colour, graph fitting lacks explicit X/Y semantics, or the Signals tree and combo controls conceal their state on a dark surface.
- Skip when: The change alters decoded CAN values, acquisition lifecycle semantics, measurement mathematics, or export contents.

# Needs
- Give every visible signal graph a distinct, deterministic and accessible colour so simultaneous traces can be identified immediately.
- Make DBC and message expand/collapse affordances visible against the dark Signals tree, reclaim signal-name width, and replace per-row textual shown/favorite checkboxes with compact eye and star actions.
- Make every drop-down trigger explicit and visually intentional on the dark theme, rather than a confusing white square.
- Keep the Graphs/Trace title, view selection, empty-session state, zoom/resize actions, Play/Stop, cursor actions, and their timing readouts on one graph/trace header line; add explicit controls to fit X and Y together, fit only Y while preserving the current temporal zoom, and hide or restore cursor measurement values.
- Preserve decoding, acquisition lifecycle, signal selection, graph navigation, cursor calculations, accessibility, keyboard operation, and saved measurement setups.

# Context
- GraphStackPanel currently applies the single theme.CURVE pen to every pyqtgraph curve. Its existing Fit action adjusts the global X extent only; a separate Y-only fit is not implemented.
- The SignalExplorer tree currently uses a DBC > message > signal hierarchy, 14-pixel indentation, and two fixed 46-pixel shown/favorite checkbox columns. The checkbox indicators and QTreeView branches rely on the shared Qt stylesheet.
- The current dark theme explicitly styles a combo box down arrow, but user observation reports a white click target that is ambiguous; the implementation must verify the rendered Qt platform result instead of assuming the stylesheet is sufficient.
- The graph stack currently owns a compact navigation/display/cursor row; the workspace selector is reparented above it and Play/Stop live in the acquisition bar. The confirmed graph/trace header must bring together the Graphs/Trace title, view selection, no-sample state, zoom/resize controls, Play/Stop, cursor actions, and timing readouts on one line without changing lifecycle semantics.
- The A/B, count, min, max, mean, RMS, and standard-deviation values are rendered in MeasurementPanel below the graph. Hiding them is a persisted presentation preference only: cursor lines A/B remain visible and computation/export data are unchanged.
- Existing profiles persist shown and favorite signals and workspace layout. The delivery must add backward-compatible profile persistence for cursor-measurement-value visibility; curve colours remain deterministic rather than user-configured.

# Acceptance criteria
- AC1: Every simultaneously shown signal has a visually distinct, deterministic curve colour that remains stable while the graph is refreshed; colour use remains legible on the dark graph background and is exposed in an accessible non-colour-only form.
- AC2: In the Signals tree, DBC and message rows have a visible expanded/collapsed affordance in all enabled, hover, focus, and disabled states; it can be operated with mouse and keyboard.
- AC3: A signal row reserves no separate shown/favorite checkbox columns. Its name remains the primary flexible field, while two compact eye and star controls occupy the leading reserved space; selected state is filled or highlighted and unselected state remains visibly muted, with tooltips, accessible names, and keyboard operation.
- AC4: Signal search, shown-only, favorites-only, grouping, single-click show/hide, DBC enablement separation, and persisted shown/favorite selections retain their semantics after the compact tree redesign.
- AC5: Every QComboBox used by the application has a clearly recognizable, high-contrast drop-down affordance and a coherent hover, focus, disabled, and popup state on supported desktop platforms; it is not rendered as an unexplained white square.
- AC6: At 1024x768, 1280x720, and 1600x900, one horizontal graph/trace header contains the Graphs/Trace title, view selection (including Graphs only), empty-session state when applicable, zoom and resize controls, Play/Stop, cursor actions, and cursor timing readouts without wrapping, overlap, clipping, or inaccessible hidden actions.
- AC7: The graph offers separate explicit actions for fit X+Y across all shown graphs and fit Y only across all shown graphs while preserving the current visible X range. Both actions handle empty/no-sample state safely, are keyboard reachable, named, tooltip-backed, and do not alter retained samples or cursor positions.
- AC8: An explicit toggle hides and restores cursor measurement values (A, B, delta/count, min, max, mean, RMS, and standard deviation) without hiding A/B vertical cursor lines or changing cursor placement, computed values, graph navigation, or exports. The toggle state is visible, accessible, and persisted in the active measurement profile.
- AC9: Offscreen and focused UI regression tests cover colour assignment/stability, tree affordance contrast and compact geometry, shown/favorite interaction and persistence, combo-box trigger states, one-row control containment, fit semantics, measurement visibility, and preserved existing graph/signal workflows.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_015_peaklive_unmistakable_graph_comparison_and_signal_controls`
- Architecture decision(s): (none yet)

# References
- src/peaklive/ui/panels/graph_stack.py
- src/peaklive/ui/panels/graph_controls.py
- src/peaklive/ui/panels/graph_navigation.py
- src/peaklive/ui/panels/measurement.py
- src/peaklive/ui/panels/signal_explorer.py
- src/peaklive/ui/panels/acquisition_bar.py
- src/peaklive/ui/workspace_center.py
- src/peaklive/ui/theme.py
- src/peaklive/domain/models.py
- tests/test_ui_workspace_refinement.py
- tests/test_graph_navigation.py
- tests/test_ui_analyst.py

# Backlog
- `item_053_deliver_distinguishable_graph_traces_and_explicit_graph_fitting_controls`
- `item_054_deliver_a_compact_high_contrast_signals_tree_and_explicit_drop_down_affordances`
