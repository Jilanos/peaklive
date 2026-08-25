## item_020_deliver_configurable_bounded_trace_columns_and_paging - Deliver configurable, bounded trace columns and paging
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Trace view
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-25 12:29:44

# AI Context
- Summary: Replaces the six hard-coded trace columns with a configurable, per-profile column set (visibility, order, width, time/hex/dec/bin/status formats) and replaces the quadratic per-row 5000-row pruning with a constant-time bounded model plus navigation off the live tail.
- Keywords: trace columns, column order, value formats, hex dec bin, bounded pruning, ring buffer
- Use when: Changing the trace table model, column configuration or its persistence, value formatting of trace cells, or the retention and pruning strategy of displayed rows.
- Skip when: Keyset pagination over the recorded ASC file, column grouping or freezing, and sorting a chronological trace by column.

# Problem
- The trace table has six hard-coded columns with no visibility, order, width, or format control.
- The 5000-row cap is enforced by removing the first row repeatedly, which is quadratic and stalls the UI under sustained load.

# Scope
- In:
  - Add a column configuration dialog covering visibility, order, width, and value format (time, hexadecimal, decimal, binary, status).
  - Persist the column configuration per measurement profile.
  - Replace the per-row pruning with a bounded ring-style model so the displayed window stays constant-time under load.
  - Add navigation across the retained buffer so the operator can move away from the live tail and back.
  - Keep the trace view responsive with a sustained high-rate fixture.
- Out:
  - Server-side or file-backed keyset pagination over the recorded ASC file.
  - Column grouping, freezing, or pivoting.
  - Per-column sorting of a chronological trace.

# Acceptance criteria
- AC1: Column visibility, order, width, and format can be changed and take effect immediately.
- AC2: The column configuration persists across an application restart on the same profile.
- AC3: Each supported format renders the same underlying value correctly, including hexadecimal, decimal, and binary payload views.
- AC4: Sustained ingestion beyond the retained window keeps memory bounded without per-row removal, verified by a timing or operation-count assertion.
- AC5: The operator can navigate away from the live tail and return to it.
- AC6: Headless offscreen tests cover the dialog, persistence, formats, and bounded pruning.

# AC Traceability
- request-AC5 -> This backlog slice. Proof: AC1: Column visibility, order, width, and format can be changed and take effect immediately.
- request-AC12 -> This backlog slice. Proof: AC2: The column configuration persists across an application restart on the same profile.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_003_peaklive_analyst_measurement_and_reporting_workspace`
- Architecture decision(s): (none yet)
- Request: `req_002_complete_the_peaklive_analyst_workspace_to_cantracediag_parity`
- Primary task(s): `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Priority
- Priority: Medium - column control and bounded pruning make repeated inspection sessions practical.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Notes
- Task `task_003_deliver_the_peaklive_analyst_workspace_parity_wave` was finished via `logics-manager flow finish task` on 2026-08-25.
