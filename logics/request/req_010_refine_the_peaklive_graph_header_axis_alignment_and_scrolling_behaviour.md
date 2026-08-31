## req_010_refine_the_peaklive_graph_header_axis_alignment_and_scrolling_behaviour - Refine the PeakLive graph header, axis alignment, and scrolling behaviour
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Compact aligned graph presentation
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-08-31 16:11:36

# AI Context
- Summary: Define the compact graph toolbar and shared lane geometry that make simultaneous signals read as a single time-aligned measurement surface.
- Keywords: refine, peaklive, graph, header, axis, alignment, scrolling, behaviour
- Use when: Graph commands consume multiple rows, shown-signal lanes have unequal ViewBox bounds, or the graph canvas gains vertical scrolling, clipping, or unexplained whitespace.
- Skip when: The change concerns trace filtering, CAN data semantics, new analysis calculations, or a whole-workspace rebrand.

# Needs
- Present every graph command and live readout in one compact graph header, instead of splitting the toolbar into visually disconnected rows.
- Align the vertical axes, plot boundaries, and time-grid origin of every visible signal lane so stacked signals read as one coordinated instrument.
- Remove awkward graph-lane scrolling and clipping, giving the operator one stable time surface with predictable zoom, pan, and cursor interaction.
- Use the supplied target screenshot as a behavioural visual reference for density and hierarchy, without copying its external product identity or implementation.

# Context
- PeakLive is a native PySide6 CAN-analysis application. The current GraphStackPanel renders X-linked pyqtgraph PlotWidgets in a zero-spacing layout, but each lane sizes its own left axis and the graph commands are grouped in a wrapping FlowLayout above the canvas.
- The observed PeakLive screenshot shows a title/header row separate from navigation, display, and cursor groups. This consumes vertical space and creates an uneven toolbar hierarchy.
- The supplied target screenshot shows the desired direction: a single dense command header, vertically aligned signal lanes, a shared time-reading surface, and measurement content below it.
- Existing graph-centric work removed QScrollArea-driven plot cards and repeated visible X axes. This refinement must preserve that result while correcting remaining geometry and interaction roughness rather than reintroducing scrollable cards.
- PeakLive must retain shown-signal selection, individual Y-axis readability, shared A/B cursors, grid, fit, zoom, follow-live, range measurements, keyboard operation, profile persistence, trace mode, report mode, acquisition, decoding, and exports.
- The current repository has unrelated replay changes and user-supplied external artefacts; delivery must limit implementation edits to the graph presentation scope.

# Acceptance criteria
- AC1: At 1024x768, 1280x720, and 1600x900, the normal graph view exposes its view navigation, grid/follow options, cursor actions, live window/readout, and relevant graph actions in one compact header row with no overlap, clipping, or hidden command; compact icons may replace redundant text only when each action retains an accessible name and tooltip.
- AC2: With two or more shown signals, every lane's drawable plot rectangle starts at the same X coordinate and ends at the same X coordinate; left-axis columns, time-grid lines, A/B cursor lines, and the visible X range are visually aligned across the full graph stack.
- AC3: Each signal remains individually identifiable and its Y-scale remains readable without allowing a long signal name or Y-axis label to shift a neighbouring lane's plot origin.
- AC4: The normal graph surface has no nested or lane-by-lane vertical scrolling, no clipped lanes, and no unintended blank bands; it allocates the available graph height deterministically across visible lanes while the shared time range is navigated through the graph controls and pointer gestures.
- AC5: Fit, zoom, pointer pan, grid toggle, follow-live, A/B cursor placement and dragging, cursor measurements, Trace/Report access, and saved layout state retain their current semantics after the presentation refinement.
- AC6: Offscreen regression coverage proves header geometry and accessibility, aligned multi-lane axes and view ranges, absence of graph-scroll regressions, supported-resolution layout constraints, and the preserved interactions.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_010_peaklive_compact_aligned_measurement_graphs`
- Architecture decision(s): (none yet)

# References
- logics/external/Capture d'écran 2026-08-31 152034.png
- logics/external/Capture d'écran 2026-08-31 154323.png
- src/peaklive/ui/panels/graph_stack.py
- src/peaklive/ui/panels/graph_controls.py
- src/peaklive/ui/panels/graph_navigation.py
- src/peaklive/ui/workspace_center.py
- src/peaklive/ui/theme.py
- tests/test_ui_workspace_refinement.py
- tests/test_graph_navigation.py

# Backlog
- `item_039_deliver_a_compact_aligned_non_scrolling_peaklive_graph_surface`
