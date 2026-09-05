## item_074_export_immutable_snapshots_with_efficient_row_serialization - Export immutable snapshots with efficient row serialization
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 39%
> Complexity: Medium
> Theme: P1 export performance
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: export, immutable, snapshots, efficient, row, serialization
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Tuple materialization and asdict deep-copy defeat streaming and stress the UI.

# Scope
- In:
  - Hand export an immutable snapshot.
  - Use direct csv row serialization.
  - Preserve cancellation and progress.
- Out:
  - New export formats.

# Acceptance criteria
- Large export starts without full UI-thread materialization.
- Output matches existing fixtures and is internally consistent during live acquisition.

# AC Traceability
- request-AC7 -> This backlog slice. Proof: Large export starts without full UI-thread materialization.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - export materializes and deep-copies all rows
- Rationale: Set by scaffold input or defaulted for grooming.
