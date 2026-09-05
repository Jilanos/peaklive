## item_063_bound_malformed_replay_diagnostics_and_prevent_false_success - Bound malformed replay diagnostics and prevent false success
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: P0 replay integrity
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-05 10:41:26

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: bound, malformed, replay, diagnostics, prevent, false, success
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Line-numbered anomaly keys defeat aggregation and unhandled worker failures still announce success.

# Scope
- In:
  - Aggregate on stable anomaly codes.
  - Limit anomaly keys and line length.
  - Reject implausible input after a documented threshold.
  - Catch worker exceptions and gate success on actual completion.
- Out:
  - Supporting additional trace formats.

# Acceptance criteria
- Millions of invalid lines yield bounded events and memory.
- Binary-like input fails visibly and never reports replay complete.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: Millions of invalid lines yield bounded events and memory.
- request-AC5 -> This backlog slice. Proof: Binary-like input fails visibly and never reports replay complete.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: High - malformed input can flood the UI and claim completion
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Notes
- Task `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone` was finished via `logics-manager flow finish task` on 2026-09-05.
