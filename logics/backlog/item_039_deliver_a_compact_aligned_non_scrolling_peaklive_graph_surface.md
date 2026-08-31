## item_039_deliver_a_compact_aligned_non_scrolling_peaklive_graph_surface - Deliver a compact, aligned, non-scrolling PeakLive graph surface
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 60%
> Complexity: High
> Theme: Graph presentation geometry
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-31 16:02:46

# AI Context
- Summary: Deliver one dense command header and one time-aligned lane stack, using a shared axis gutter and an explicit no-scroll height policy.
- Keywords: deliver, compact, aligned, non, scrolling, peaklive, graph, surface
- Use when: Implementing or testing GraphControlsBar, GraphStackPanel, pyqtgraph axis/ViewBox geometry, or graph viewport overflow at the supported desktop sizes.
- Skip when: The work changes trace-table layout, signal decoding or sampling, export contents, or cursor/range calculation rules.

# Problem
- Graph commands are split between a workspace header and wrapping control clusters, so the full command set takes disproportionate height and does not read as one tool surface.
- Independently sized pyqtgraph left axes can shift each lane's drawable rectangle, leaving grid lines and vertical cursor positions visually uncoordinated between signals.
- The remaining graph composition does not specify a deterministic lane-height and overflow policy, leaving scrolling, clipping, or blank-space regressions possible as shown-signal count changes.

# Scope
- In:
  - Recompose the graph header and GraphControlsBar into one compact, single-row command surface that keeps all existing graph actions and state readouts available at the supported resolutions.
  - Define a shared left-axis/gutter width and apply it after plot labels, tick widths, and signal identity are known, so all PlotWidgets expose identical drawable X bounds and linked time geometry.
  - Give lanes a deliberate constrained-height policy that fills the graph viewport without QScrollArea or per-lane scrollbars, repeated X axes, clipped active lanes, or arbitrary inter-lane gaps.
  - Retain a single visible time axis and keep signal labels and per-lane Y-scale information legible through bounded elision, tooltips, and accessible names where necessary.
  - Preserve and test existing navigation, cursor, grid, follow-live, measurement, mode-switching, keyboard, and persisted-layout behaviours.
  - Add stable offscreen structural and geometry tests, plus targeted visual-regression assertions where deterministic pixels are appropriate.
- Out:
  - Changing graph data retention, resampling, CAN acquisition, decoding, filtering, export, or measurement mathematics.
  - Replicating the target application's branding, exact palette, proprietary controls, or implementation.
  - New analysis tools, floating/docked graph panels, or unrelated Trace filter changes.

# Acceptance criteria
- AC1: All graph commands and state readouts are wholly contained in one compact header row with no overlap, clipping, or wrapping at 1024x768, 1280x720, and 1600x900; each icon-only control remains keyboard reachable, named, and tooltip-backed.
- AC2: A multi-signal graph has equal left and right drawable bounds for every lane; the time grid and A/B cursor lines line up across lane boundaries to within the device-pixel tolerance defined by the UI tests.
- AC3: Signal identity and per-lane Y values remain distinguishable, and pathological label/tick widths cannot move one lane's time origin independently of the others.
- AC4: The graph canvas remains a single non-scrolling surface with one visible time axis. Adding shown signals follows the documented lane-height policy and never introduces nested, per-lane, or accidental vertical scrolling.
- AC5: Existing fit, zoom, pan, grid, follow-live, cursor, measurement, Trace/Report, persistence, acquisition, decoding, and export tests still pass unchanged unless a presentation-only expectation is intentionally updated.
- AC6: New offscreen tests cover the three benchmark viewports, full header containment, aligned ViewBox and axis geometry, scroll-bar absence, label stress cases, and retained graph interactions.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: All graph commands and state readouts are wholly contained in one compact header row with no overlap, clipping, or wrapping at 1024x768, 1280x720, and 1600x900; each icon-only control remains keyboard reachable, named, and tooltip-backed.
- request-AC2 -> This backlog slice. Proof: AC2: A multi-signal graph has equal left and right drawable bounds for every lane; the time grid and A/B cursor lines line up across lane boundaries to within the device-pixel tolerance defined by the UI tests.
- request-AC3 -> This backlog slice. Proof: AC3: Signal identity and per-lane Y values remain distinguishable, and pathological label/tick widths cannot move one lane's time origin independently of the others.
- request-AC4 -> This backlog slice. Proof: AC4: The graph canvas remains a single non-scrolling surface with one visible time axis. Adding shown signals follows the documented lane-height policy and never introduces nested, per-lane, or accidental vertical scrolling.
- request-AC5 -> This backlog slice. Proof: AC5: Existing fit, zoom, pan, grid, follow-live, cursor, measurement, Trace/Report, persistence, acquisition, decoding, and export tests still pass unchanged unless a presentation-only expectation is intentionally updated.
- request-AC6 -> This backlog slice. Proof: AC6: New offscreen tests cover the three benchmark viewports, full header containment, aligned ViewBox and axis geometry, scroll-bar absence, label stress cases, and retained graph interactions.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_010_peaklive_compact_aligned_measurement_graphs`
- Architecture decision(s): (none yet)
- Request: `req_010_refine_the_peaklive_graph_header_axis_alignment_and_scrolling_behaviour`
- Primary task(s): `task_011_implement_the_compact_aligned_peaklive_graph_presentation`

# Priority
- Priority: High - graph comparison is a core analyst workflow, and the current header density, lane geometry, and scrolling make it harder to read and operate.
- Rationale: Set by scaffold input or defaulted for grooming.
