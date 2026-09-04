## item_058_recover_safely_from_a_corrupt_profile_store - Recover safely from a corrupt profile store
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Low
> Theme: P0 profile recovery
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: recover, safely, corrupt, profile, store
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Unreadable or invalid profiles.json crashes before the window exists.

# Scope
- In:
  - Catch parse, I/O, and invalid-value errors.
  - Rename the source to a timestamped corrupt backup.
  - Start with defaults and show an English warning dialog.
- Out:
  - Automatic profile repair.

# Acceptance criteria
- Corrupt JSON, invalid controller mode, and invalid bitrate start the application on defaults.
- The backup path is logged and the operator sees a warning.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: Corrupt JSON, invalid controller mode, and invalid bitrate start the application on defaults.
- request-AC5 -> This backlog slice. Proof: The backup path is logged and the operator sees a warning.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: High - prevents application startup
- Rationale: Set by scaffold input or defaulted for grooming.
