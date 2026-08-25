## item_017_stabilize_a_b_cursors_and_add_graph_time_navigation - Stabilize A/B cursors and add graph time navigation
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Graph measurement
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-25 12:29:44

# AI Context
- Summary: Fixes the graph refresh path that re-pins cursor A to the first sample and cursor B to the last sample on every incoming batch, then adds zoom, pan, fit-to-extent, grid, a shared time axis across stacked plots, and a follow-live mode that yields to operator navigation.
- Keywords: cursor persistence, linked time axis, zoom, pan, fit, grid, follow live
- Use when: Changing cursor lifecycle, plot view ranges, axis linking between stacked plots, or the live-tail follow behavior.
- Skip when: Computing values or statistics at the cursors (that is the measurement table slice), overlaying several signals on one plot, or Y-axis autoscale policy beyond keeping placed cursors valid.

# Problem
- The graph refresh path re-pins cursor A to the first sample and cursor B to the last sample on every incoming batch, so a placed measurement is destroyed during live acquisition.
- The graph stack offers no explicit zoom, pan, fit, or grid control, no shared time axis across stacked plots, and no readout of the visible window or zoom factor.

# Scope
- In:
  - Separate cursor initialization from cursor refresh so operator-placed cursors are never overwritten by incoming data.
  - Persist cursor positions per profile and restore them on reload and on view switching.
  - Link the time axis across the stacked plots so pan and zoom apply coherently to all shown signals.
  - Add explicit zoom in, zoom out, fit-to-extent, and grid toggle controls, plus a visible time window and zoom-factor readout.
  - Add a follow-live mode that tracks the newest samples and yields as soon as the operator pans or zooms.
  - Keep the bounded per-signal sample buffers and the raw-byte preview fallback behavior intact.
- Out:
  - Y-axis autoscale policies beyond what is needed to keep placed cursors valid.
  - Multi-signal overlay on a single plot.
  - Annotation or bookmark persistence on the time axis.

# Acceptance criteria
- AC1: A cursor moved by the operator keeps its position across at least ten subsequent data batches.
- AC2: Cursor positions survive a profile reload and a workspace view switch.
- AC3: Pan and zoom on one plot apply the same time window to every other shown plot.
- AC4: Zoom in, zoom out, fit, and grid controls are present and change the rendered window or grid state.
- AC5: The readout shows the visible time window and the zoom factor relative to the full extent.
- AC6: Follow-live mode tracks new samples and disengages on operator pan or zoom.
- AC7: Headless offscreen tests cover cursor persistence, axis linking, and the navigation controls.

# AC Traceability
- request-AC2 -> This backlog slice. Proof: AC1: A cursor moved by the operator keeps its position across at least ten subsequent data batches.
- request-AC12 -> This backlog slice. Proof: AC2: Cursor positions survive a profile reload and a workspace view switch.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_003_peaklive_analyst_measurement_and_reporting_workspace`
- Architecture decision(s): (none yet)
- Request: `req_002_complete_the_peaklive_analyst_workspace_to_cantracediag_parity`
- Primary task(s): `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Priority
- Priority: High - a measurement that resets on every data batch cannot be used live.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Notes
- Task `task_003_deliver_the_peaklive_analyst_workspace_parity_wave` was finished via `logics-manager flow finish task` on 2026-08-25.
