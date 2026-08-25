## item_016_make_the_frame_inspector_selection_driven - Make the frame inspector selection-driven
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Trace inspection
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-25 12:29:44

# AI Context
- Summary: Replaces the inspector QLabel that is overwritten from inside the frame-render loop with a panel driven by the operator's trace-row selection, showing frame identity, raw payload, resolved message and source DBC, decode status, and every decoded physical signal.
- Keywords: inspector, trace selection, raw payload, decode status, decoded signals, empty state
- Use when: Touching the inspector panel, the trace-row selection handler, or the mapping from a displayed trace row back to its retained frame or bus event.
- Skip when: Working on the graph stack, on trace filtering or columns, or on anything that would let the inspector retransmit or mutate the inspected frame.

# Problem
- The inspector is a QLabel overwritten from inside the frame-render loop with whichever decoded signal streamed past last.
- There is no trace selection handler, so clicking a trace row produces no inspection at all and the operator cannot answer 'what was in that frame'.

# Scope
- In:
  - Add a trace row selection handler that resolves the selected row back to its retained frame or bus event.
  - Render frame identity: timestamp, arbitration ID with extended flag, DLC, channel, and direction.
  - Render the raw payload as a hexadecimal string and as a per-byte breakdown.
  - Render the resolved message name with its source DBC, the decode status, and every decoded physical signal with raw value, physical value, and unit.
  - Render bus events with their kind and message when the selected row is an event rather than a frame.
  - Keep the inspector correct during live acquisition, during replay, and after the trace view prunes older rows.
  - Give the inspector an explicit empty state and an explicit undecodable state.
- Out:
  - Editing or retransmitting the inspected frame.
  - Bit-level graphical payload layout rendering.
  - Cross-frame diffing or sequence analysis.

# Acceptance criteria
- AC1: Selecting a trace row populates the inspector with that frame's identity, raw payload, resolved message, decode status, and decoded signals.
- AC2: Selecting a bus event row shows the event kind and message instead of frame fields.
- AC3: The inspector no longer changes as a side effect of incoming frames when a row is selected.
- AC4: With no selection the inspector shows an explicit empty state, and an undecodable frame shows the raw payload with a stated reason.
- AC5: Headless offscreen tests cover frame selection, event selection, undecodable frames, and selection surviving trace pruning.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Selecting a trace row populates the inspector with that frame's identity, raw payload, resolved message, decode status, and decoded signals.
- request-AC8 -> This backlog slice. Proof: AC2: Selecting a bus event row shows the event kind and message instead of frame fields.
- request-AC12 -> This backlog slice. Proof: AC3: The inspector no longer changes as a side effect of incoming frames when a row is selected.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_003_peaklive_analyst_measurement_and_reporting_workspace`
- Architecture decision(s): (none yet)
- Request: `req_002_complete_the_peaklive_analyst_workspace_to_cantracediag_parity`
- Primary task(s): `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Priority
- Priority: High - the inspector is currently non-functional and blocks any real frame-level analysis.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Notes
- Task `task_003_deliver_the_peaklive_analyst_workspace_parity_wave` was finished via `logics-manager flow finish task` on 2026-08-25.
