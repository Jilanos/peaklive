## item_061_own_export_workers_independently_of_transient_dialogs - Own export workers independently of transient dialogs
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Low
> Theme: P0 export lifecycle
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: own, export, workers, independently, transient, dialogs
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- A running QThread is owned by its dialog and is destroyed with the window.

# Scope
- In:
  - Create export workers without dialog ownership.
  - Track them at window level.
  - Show a waiting dialog on close with explicit force-close confirmation.
- Out:
  - New export formats.

# Acceptance criteria
- Close during export waits visibly, can be explicitly forced, and never destroys a running QThread.
- Interrupted output is marked incomplete or removed.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: Close during export waits visibly, can be explicitly forced, and never destroys a running QThread.
- request-AC5 -> This backlog slice. Proof: Interrupted output is marked incomplete or removed.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: High - closing during export can abort the process
- Rationale: Set by scaffold input or defaulted for grooming.
