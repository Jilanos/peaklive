## item_023_deliver_bus_state_error_and_loading_feedback - Deliver bus-state, error, and loading feedback
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Operator feedback
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-25 12:29:44

# AI Context
- Summary: Replaces transient status-bar messaging with visible state: a bus-state indicator covering idle through bus-off, persistent panel-local DBC parse and conflict errors, explicit empty/error/loading states in every panel, progress and cancellation for DBC loading and replay import, and visible recording disk warnings.
- Keywords: bus state indicator, empty state, error state, loading progress, cancellation, disk warning
- Use when: Adding or changing any operator-facing state affordance - connection state, panel empty or error states, progress indicators, cancellation, or recording warnings.
- Skip when: Notification centre or persisted alert log, sound or tray alerts, and changing the recorder's own disk threshold policy.

# Problem
- The only status affordance is the controller-mode pill; bus events land in the trace table and DBC conflicts appear as a transient status-bar message the operator will miss.
- There is no progress or cancel affordance for DBC loading or replay import, and no explicit empty, error, or loading state in any panel.

# Scope
- In:
  - Add a bus-state indicator with a colored state marker and a text label covering idle, connecting, running, reconnecting, bus error, bus-off, and stopped.
  - Surface DBC parse and conflict errors as persistent panel-local messages in the DBC library instead of transient status-bar text.
  - Add explicit empty, error, and loading states for the trace view, the graph stack, the inspector, the report, and the export flow.
  - Add a progress indicator with cancellation for multi-DBC loading and for replay import.
  - Surface recording disk warnings and the stop threshold from RecordingSettings as visible operator warnings.
  - Keep every state string routed through the i18n layer.
- Out:
  - Notification centre, toast history, or persisted alert log.
  - Changing the recorder's disk threshold policy itself.
  - Sound or system-tray alerts.

# Acceptance criteria
- AC1: The bus-state indicator reflects each of the seven states and is driven by real acquisition and adapter events.
- AC2: A DBC parse failure or unresolved conflict shows a persistent message in the DBC library panel that survives further frame traffic.
- AC3: The trace view, graph stack, inspector, report, and export flow each show a distinct empty, error, and loading state.
- AC4: Loading several DBC files and importing a replay file both show progress and can be cancelled.
- AC5: A recording disk warning and a recording stop threshold both surface as visible operator warnings.
- AC6: Every state string resolves through the i18n layer with no bare literal.
- AC7: Headless offscreen tests cover each state transition using fake adapters and fixtures.

# AC Traceability
- request-AC8 -> This backlog slice. Proof: AC1: The bus-state indicator reflects each of the seven states and is driven by real acquisition and adapter events.
- request-AC12 -> This backlog slice. Proof: AC2: A DBC parse failure or unresolved conflict shows a persistent message in the DBC library panel that survives further frame traffic.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_003_peaklive_analyst_measurement_and_reporting_workspace`
- Architecture decision(s): (none yet)
- Request: `req_002_complete_the_peaklive_analyst_workspace_to_cantracediag_parity`
- Primary task(s): `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Priority
- Priority: High - a live acquisition tool must make its connection and failure states unmissable.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Notes
- Task `task_003_deliver_the_peaklive_analyst_workspace_parity_wave` was finished via `logics-manager flow finish task` on 2026-08-25.
