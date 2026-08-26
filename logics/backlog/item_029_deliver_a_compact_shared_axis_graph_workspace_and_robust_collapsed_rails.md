## item_029_deliver_a_compact_shared_axis_graph_workspace_and_robust_collapsed_rails - Deliver a compact shared-axis graph workspace and robust collapsed rails
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: High
> Theme: Graph-centric responsive workspace
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-26 18:38:12

# AI Context
- Summary: Deliver one compact graph surface and reliable compact side-panel rails without changing data or measurement semantics.
- Keywords: deliver, compact, shared, axis, graph, workspace, robust, collapsed, rails
- Use when: The implementation must improve graph density, shared time navigation, or collapsed rail geometry in the existing native workspace.
- Skip when: The work belongs to Trace filter responsiveness, new analysis capability, acquisition, decode, or export scope.

# Problem
- The plus control in a collapsed Signals or Inspector rail is too large for its constrained geometry and can be obscured, which makes restoring a panel unreliable.
- Each plotted signal is an independent scrolling card with its own title and X axis. The resulting gaps and repeated labels fragment the measurement view and leave too little area for data.
- Graph controls and supporting workspace modes need a more compact hierarchy so the graph area retains priority at bench-screen resolutions.

# Scope
- In:
  - Introduce a compact collapsed-rail header or control geometry that guarantees an unobstructed, centred expand affordance for both side panels.
  - Recompose the selected-signal rendering into a compact shared-time graph surface or linked plot layout with only one visible X axis and no vertical graph scroll in the normal graph view.
  - Keep each signal identifiable through a compact label, lane, or legend and retain readable per-signal Y-scale information.
  - Preserve A/B cursors, grid, zoom, fit, follow-live, measurements, keyboard access, and profile persistence.
  - Compact the graph controls and workspace mode affordances so data keeps priority at 1024x768, 1280x720, and 1600x900.
  - Add offscreen regression tests for rail affordance geometry, shared-axis graph structure, and responsive workspace geometry.
- Out:
  - Changing Trace filter-bar layout, which belongs to req_004.
  - Changing sampling, decoding, acquisition, trace filtering, or export behaviour.
  - Adding graph calculations, protocol features, multi-window docking, or a visual rebrand.

# Acceptance criteria
- AC1: Both collapsed side panels expose a compact expand control fully inside their rails, centred without clipping or overlap, and restore their existing state.
- AC2: With multiple selected signals, the normal graph workspace has no QScrollArea-driven vertical plot scrolling, no white bands between signal lanes, and one visible shared X axis.
- AC3: Every selected signal has a readable identity and curve; all curve lanes share the same time view and show aligned A/B cursors.
- AC4: Zoom, fit, grid, follow-live, cursor placement, and measurement readouts remain operational and compact without clipping at the supported resolutions.
- AC5: The graph-first workspace retains direct access to Trace and Report and preserves saved splitter and collapsed-panel layout state.
- AC6: Offscreen tests demonstrate the compact rail geometry, shared graph structure, preserved interactions, and no overflow at the supported resolutions.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Both collapsed side panels expose a compact expand control fully inside their rails, centred without clipping or overlap, and restore their existing state.
- request-AC2 -> This backlog slice. Proof: AC2: With multiple selected signals, the normal graph workspace has no QScrollArea-driven vertical plot scrolling, no white bands between signal lanes, and one visible shared X axis.
- request-AC3 -> This backlog slice. Proof: AC3: Every selected signal has a readable identity and curve; all curve lanes share the same time view and show aligned A/B cursors.
- request-AC4 -> This backlog slice. Proof: AC4: Zoom, fit, grid, follow-live, cursor placement, and measurement readouts remain operational and compact without clipping at the supported resolutions.
- request-AC5 -> This backlog slice. Proof: AC5: The graph-first workspace retains direct access to Trace and Report and preserves saved splitter and collapsed-panel layout state.
- request-AC6 -> This backlog slice. Proof: AC6: Offscreen tests demonstrate the compact rail geometry, shared graph structure, preserved interactions, and no overflow at the supported resolutions.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_005_peaklive_graph_centric_diagnostic_workspace`
- Architecture decision(s): (none yet)
- Request: `req_005_make_the_peaklive_workspace_graph_centric_and_compact`
- Primary task(s): `task_005_implement_the_peaklive_graph_centric_compact_workspace`

# Priority
- Priority: High - live plotting is the primary analyst activity and the current structure wastes central space while hiding the collapsed-panel recovery affordance.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_005_implement_the_peaklive_graph_centric_compact_workspace`

# Notes
- Task `task_005_implement_the_peaklive_graph_centric_compact_workspace` was finished via `logics-manager flow finish task` on 2026-08-26.
