## item_129_place_a_b_and_temporal_delta_readouts_in_the_shared_graph_command_row - Place A B and temporal delta readouts in the shared graph command row
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Compact cursor timing
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-13 15:32:01

# AI Context
- Summary: Move synchronized A/B and signed B-minus-A times beside graph commands with complete values and a same-row overflow policy.
- Keywords: place, temporal, delta, readouts, shared, graph, command, row
- Use when: Changing cursor formatting, command-row geometry, overflow behaviour, or supported-width qualification.
- Skip when: Changing cursor placement semantics or signal measurement algorithms.

# Problem
- cursor_summary stays in a separate GraphControlsBar row and reports only A/B. Moving it without a width policy would recreate the known clipping defect.

# Scope
- In:
  - Move the existing live cursor summary into WorkspaceHeaderBar beside fit/resize and Start/Stop, preserving a single source of cursor state and removing empty GraphControlsBar row height in the integrated window.
  - Render A, B, and delta B-A in seconds to three decimals from unrounded positions; independently represent unset values, support negative and zero delta, and avoid display negative zero.
  - Implement request AC8's same-row width policy: compact control presentation first, then accessible overflow for lower-frequency controls under side-panel pressure; keep A/B/delta and Start/Stop directly visible. Measure required center width and prevent unsupported narrowing from silently clipping timestamps.
  - Use font-metric sizing for long signed values and scalable controls. Preserve fit-all, fit-Y, Follow live, cursor placement, measurement visibility, mode access, keyboard actions, and standalone GraphStackPanel behaviour.
  - Update the workspace_center comment and affected item_055-related test expectations to reflect this new one-row contract; the cursor delta does not restore removed viewport readouts.
- Out:
  - Changing cursor positioning semantics, sample/value measurement algorithms, adding frequency readouts, or restoring removed zoom/grid controls.

# Acceptance criteria
- AC1: A/B/delta update on placement, dragging, restoration, and data initialization on the same row as fit and Start/Stop, with no residual second readout band.
- AC2: Formatting tests cover neither cursor, only A, only B, equal cursors, reversed cursors, negative timestamps, long recordings, and sub-millisecond values where rounding before subtraction would produce an incorrect delta.
- AC3: Qt geometry tests at all three benchmark window sizes prove complete A/B/delta plus required direct controls in graph-focused mode, and an accessible one-row overflow policy with expanded side panels; include the long values in request AC8.
- AC4: Windows 100%/150% visual evidence confirms readable timestamps and real plot-height gains; focused cursor/navigation/profile tests pass and any unavailable Windows qualification is explicitly recorded before closeout.

# AC Traceability
- request-AC7 -> This backlog slice. Proof: AC1: A/B/delta update on placement, dragging, restoration, and data initialization on the same row as fit and Start/Stop, with no residual second readout band.
- request-AC8 -> This backlog slice. Proof: AC2: Formatting tests cover neither cursor, only A, only B, equal cursors, reversed cursors, negative timestamps, long recordings, and sub-millisecond values where rounding before subtraction would produce an incorrect delta.
- request-AC9 -> This backlog slice. Proof: AC3: Qt geometry tests at all three benchmark window sizes prove complete A/B/delta plus required direct controls in graph-focused mode, and an accessible one-row overflow policy with expanded side panels; include the long values in request AC8.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_026_peaklive_predictable_and_space_efficient_measurement_workspace`
- Architecture decision(s): (none yet)
- Request: `req_027_restore_predictable_panel_geometry_and_reclaim_graph_workspace_space`
- Primary task(s): `task_027_deliver_stable_panel_restoration_and_a_space_efficient_graph_workspace`

# Priority
- Priority: Medium - the separate timestamp row wastes graph height and omits the requested direct time-difference readout.
- Rationale: Set by scaffold input or defaulted for grooming.
