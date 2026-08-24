## item_013_deliver_multi_graph_measurements_and_configurable_workspace_panels - Deliver multi-graph measurements and configurable workspace panels
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 95%
> Confidence: 90%
> Progress: 100%
> Complexity: High
> Theme: Plots and workspace layout
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-24 14:43:19

# AI Context
- Summary: Adds multiple simultaneous graph tracks, A/B cursors, measurement readouts, graph/trace workspace modes, and independently collapsible panels.
- Keywords: deliver, multi, graph, measurements, configurable, workspace, panels
- Use when: Working on graph selection, multi-plot rendering, cursor interactions, graph/trace combo modes, panel collapse/restore, or layout persistence.
- Skip when: Changing DBC library management, acquisition setup semantics, or visual styling that does not affect graph and workspace layout behavior.

# Problem
- PeakLive currently offers a single preview plot and fixed panels, while operators need several simultaneous graphs, cursors, and configurable views.
- Trace, graphs, inspector, and signal navigation compete for space during live analysis.

# Scope
- In:
  - Support multiple simultaneous graph tracks or graph panels selected from plotted signals.
  - Add A/B cursors, delta time, and per-signal delta/value readouts.
  - Provide graph-only, trace-only, graph+trace combo, and full workspace configurations.
  - Make signals, inspector, graph area, and trace area independently collapsible with state restoration.
  - Keep bounded memory and rendering cadence for live updates and replay-derived plots.
  - Ensure cursor and graph interactions are testable without live hardware using fake/replay data.
- Out:
  - Dashboard gauges, alarm rules, scripting, or arbitrary user-authored graph widgets.
  - 3D rendering or browser-only fullscreen APIs.
  - Making a long live CAN run part of acceptance.

# Acceptance criteria
- AC1: Operators can display multiple graph tracks at the same time and remove/reorder visible signals without losing DBC selection state.
- AC2: A/B cursors can be placed and moved, and readouts show delta time plus values or deltas for plotted signals.
- AC3: Workspace configurations toggle graph, trace, combo, inspector, and signal panels without corrupting acquisition, replay, or selected plots.
- AC4: Collapsed panels restore from the profile and remain keyboard-operable.
- AC5: Tests cover multi-graph rendering state, cursor readouts, view configuration, panel collapse/restore, and bounded buffer behavior.

# AC Traceability
- request-AC5 -> This backlog slice. Proof: AC1: Operators can display multiple graph tracks at the same time and remove/reorder visible signals without losing DBC selection state.
- request-AC6 -> This backlog slice. Proof: AC2: A/B cursors can be placed and moved, and readouts show delta time plus values or deltas for plotted signals.
- request-AC7 -> This backlog slice. Proof: AC3: Workspace configurations toggle graph, trace, combo, inspector, and signal panels without corrupting acquisition, replay, or selected plots.
- request-AC8 -> This backlog slice. Proof: AC4: Collapsed panels restore from the profile and remain keyboard-operable.
- request-AC9 -> This backlog slice. Proof: AC5: Tests cover multi-graph rendering state, cursor readouts, view configuration, panel collapse/restore, and bounded buffer behavior.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_002_peaklive_cantracediag_grade_diagnostic_workspace`
- Architecture decision(s): (none yet)
- Request: `req_001_bring_peaklive_ux_to_cantracediag_parity`
- Primary task(s): `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta`

# Priority
- Priority: Medium - graph and layout depth depends on the DBC and signal workflow.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta`

# Notes
- Task `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta` was finished via `logics-manager flow finish task` on 2026-08-24.
