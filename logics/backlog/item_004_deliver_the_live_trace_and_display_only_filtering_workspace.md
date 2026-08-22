## item_004_deliver_the_live_trace_and_display_only_filtering_workspace - Deliver the live trace and display-only filtering workspace
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 50%
> Complexity: Medium
> Theme: Live trace
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-22 12:10:33

# AI Context
- Summary: Provides a responsive chronological trace, inspection, bus health, and persisted filters that never alter active recording contents.
- Keywords: deliver, live, trace, display, only, filtering, workspace
- Use when: Implementing batched trace models, raw columns, follow-tail/pause, filtering, highlighting, counters, inspection, or trace layout persistence.
- Skip when: Changing recorder inclusion rules, hardware acquisition, DBC catalog semantics, signal plots, or offline export.

# Problem
- A chronological high-rate trace can overwhelm desktop models if each frame is rendered individually.

# Scope
- In:
  - Batched bounded chronological trace model, pause/follow-tail, row inspection, counters, and bus-health strip.
  - Filters for identifiers, ranges, frame type, payload patterns, channel/state, and decoded text where available.
  - Column visibility, ordering, sizing, hexadecimal formatting, change highlighting, and persisted views.
  - Clear indication that filters affect display only.
- Out:
  - Editing or transmitting frames and unbounded retention in the UI model.

# Acceptance criteria
- AC1: The trace shows the required raw columns and applies frame batches at a controlled UI cadence.
- AC2: Applying, clearing, pausing, or changing a display filter does not alter recorder input or active capture counts.
- AC3: Error and state rows are distinguishable, inspectable, and linked to current bus health.
- AC4: The bounded trace window evicts presentation rows predictably while preserving total counters and saved evidence.
- AC5: Layout and filter settings restore locally without initiating a hardware connection.

# AC Traceability
- request-AC4 -> This backlog slice. Proof: AC1: The trace shows the required raw columns and applies frame batches at a controlled UI cadence.
- request-AC7 -> This backlog slice. Proof: AC2: Applying, clearing, pausing, or changing a display filter does not alter recorder input or active capture counts.
- request-AC12 -> This backlog slice. Proof: AC3: Error and state rows are distinguishable, inspectable, and linked to current bus health.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_001_peaklive_windows_can_workstation`
- Architecture decision(s): (none yet)
- Request: `req_000_deliver_the_peaklive_windows_can_workstation_mvp`
- Primary task(s): `task_001_orchestrate_the_peaklive_windows_can_workstation_mvp`

# Priority
- Priority: High — engineers need an immediately usable view of raw bus activity while capture remains independent.
- Rationale: Set by scaffold input or defaulted for grooming.
