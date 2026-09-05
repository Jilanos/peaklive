## item_078_inject_a_recorder_factory_into_acquisition_workers - Inject a recorder factory into acquisition workers
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Low
> Theme: P1 testability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: inject, recorder, factory, acquisition, workers
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Worker constructs the recorder directly despite existing injectable seams.

# Scope
- In:
  - Inject a recorder factory and free-space probe.
  - Add worker-level disk threshold and rotation tests.
- Out:
  - New recording formats.

# Acceptance criteria
- Worker tests deterministically simulate disk conditions and rotation.

# AC Traceability
- request-AC7 -> This backlog slice. Proof: Worker tests deterministically simulate disk conditions and rotation.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - worker seams cannot test disk and rotation behaviour
- Rationale: Set by scaffold input or defaulted for grooming.
