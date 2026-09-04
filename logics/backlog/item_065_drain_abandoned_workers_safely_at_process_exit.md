## item_065_drain_abandoned_workers_safely_at_process_exit - Drain abandoned workers safely at process exit
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: P0 shutdown integrity
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: drain, abandoned, workers, safely, process, exit
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- The abandoned-worker collection can retain active threads until interpreter teardown.

# Scope
- In:
  - Attach completion cleanup without race.
  - Log identity and phase at exit.
  - Apply the global close budget and explicit forced-close flow.
- Out:
  - Forcing a stuck vendor driver to return.

# Acceptance criteria
- Completed abandoned workers are removed.
- Active workers at forced exit are reported with evidence and no Qt destruction crash occurs.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: Completed abandoned workers are removed.
- request-AC5 -> This backlog slice. Proof: Active workers at forced exit are reported with evidence and no Qt destruction crash occurs.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: High - abandoned workers currently remain unmanaged
- Rationale: Set by scaffold input or defaulted for grooming.
