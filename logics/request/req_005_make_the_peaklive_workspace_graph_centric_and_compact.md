## req_005_make_the_peaklive_workspace_graph_centric_and_compact - Make the PeakLive workspace graph-centric and compact
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Graph-centric desktop workspace
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-08-26 18:38:11

# AI Context
- Summary: Replace fragmented scrollable plot cards with a shared-time graph workspace, while making collapsed side-panel recovery controls fit their rails.
- Keywords: peaklive, workspace, graph, centric, compact
- Use when: Live-signal analysis is visually fragmented or cannot reclaim sufficient central workspace at supported desktop resolutions.
- Skip when: The requested work changes trace filtering, decoding, acquisition, exports, or analytical meaning rather than desktop graph presentation.

# Needs
- Make collapsed Signals and Inspector rails robust: their compact expand affordance must stay unobstructed, smaller, centred, and easy to activate.
- Replace the vertically scrolling stack of separately framed plots with a compact shared-time graph workspace that removes white gaps and repeated X axes.
- Give live plots priority over supporting controls while keeping graph navigation, cursor placement, measurements, Trace, and Report discoverable and operable.
- Make the graph workspace visually and spatially coherent at supported desktop resolutions without changing signal data, cursor, filtering, or acquisition semantics.

# Context
- PeakLive is a native PySide6 desktop CAN-analysis application. Its central workspace holds graph, trace, and report modes, while Signals and Inspector sit in collapsible splitter panels.
- The current collapsed side-panel rail is 34 px wide and uses the same header toggle after its body and heading disappear. On Windows, the plus affordance is partly occluded in the compact rail.
- GraphStackPanel currently creates one independent pyqtgraph PlotWidget per selected signal in a QScrollArea. Each plot owns an X axis and title, producing repeated axes, white inter-plot gaps, and vertical scrolling that competes with graph reading.
- CanTraceDiag's measurement workspace demonstrates the intended hierarchy: a single dense plot surface, one shared time axis, compact navigation and cursor controls, and explicit workspace modes that keep plots central.
- The earlier responsive Trace filter request remains separately tracked as req_004_make_trace_filtering_responsive_at_1024_px_workspace_width; this work must not duplicate or widen that scope.
- The change must preserve profile layout persistence, shown-signal selection, A/B cursor semantics, follow-live behaviour, measurements, trace selection, keyboard access, and headless offscreen UI coverage.

# Acceptance criteria
- AC1: When Signals or Inspector is collapsed, its rail has an unobstructed, centred, compact expand button with an accessible name and tooltip; it restores the panel without losing state.
- AC2: Selected signals render in a compact graph workspace with a shared navigation domain and one visible time axis; there are no white inter-plot bands or per-plot vertical scrolling in the normal graph view.
- AC3: Each selected signal remains individually identifiable and readable, and shared A/B cursor lines, grid, fit, zoom, and follow-live behaviour remain correct across every rendered signal.
- AC4: The default workspace at 1024x768, 1280x720, and 1600x900 gives the graph surface priority while retaining compact, non-overlapping controls, reachable Trace and Report modes, and splitter persistence.
- AC5: The implementation preserves display-only Trace filtering, acquisition, decoding, exports, profile persistence, and measurement semantics; req_004 remains the sole scope for Trace filter-header responsiveness.
- AC6: Headless regression tests cover collapsed-rail geometry, graph geometry and shared-axis structure, interactive controls, cursor/navigation behaviour, and supported-resolution layout constraints.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_005_peaklive_graph_centric_diagnostic_workspace`
- Architecture decision(s): (none yet)

# References
- docs/cantracediag-ux-delta.md
- src/peaklive/ui/widgets.py
- src/peaklive/ui/panels/graph_stack.py
- src/peaklive/ui/panels/graph_controls.py
- src/peaklive/ui/workspace_center.py
- src/peaklive/ui/main_window.py
- src/peaklive/ui/theme.py
- tests/test_ui_workspace_refinement.py

# Backlog
- `item_029_deliver_a_compact_shared_axis_graph_workspace_and_robust_collapsed_rails`
