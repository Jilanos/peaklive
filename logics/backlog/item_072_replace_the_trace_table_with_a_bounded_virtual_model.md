## item_072_replace_the_trace_table_with_a_bounded_virtual_model - Replace the trace table with a bounded virtual model
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 39%
> Complexity: High
> Theme: P1 trace performance
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: replace, trace, table, bounded, virtual, model
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- QTableWidget reconstructs 5000 by 8 cells and blocks the event loop.

# Scope
- In:
  - Use QTableView and QAbstractTableModel over the existing bounded buffer.
  - Preserve filtering, selection, formatting, and column configuration.
- Out:
  - Unbounded trace retention.

# Acceptance criteria
- Refresh does not create one Qt item per cell.
- Existing trace behaviours remain covered and 5000-row updates meet the documented Linux baseline.

# AC Traceability
- request-AC7 -> This backlog slice. Proof: Refresh does not create one Qt item per cell.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - the widget rebuild creates tens of thousands of items
- Rationale: Set by scaffold input or defaulted for grooming.
