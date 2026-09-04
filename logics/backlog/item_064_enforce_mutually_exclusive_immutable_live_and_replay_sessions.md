## item_064_enforce_mutually_exclusive_immutable_live_and_replay_sessions - Enforce mutually exclusive immutable live and replay sessions
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Low
> Theme: P0 session isolation
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: enforce, mutually, exclusive, immutable, live, replay, sessions
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Live and replay can write the same buffers and live profile edits cross a thread boundary.

# Scope
- In:
  - Refuse starting the other source with an alert while a session is active.
  - Disable conflicting actions and shortcuts.
  - Pass workers a profile copy.
  - Validate recording templates before persistence.
- Out:
  - Stopping one mode automatically to start another.

# Acceptance criteria
- Live and replay never share a session buffer.
- Mid-session settings edits cannot mutate a worker profile.
- Invalid templates are neither saved nor used.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: Live and replay never share a session buffer.
- request-AC3 -> This backlog slice. Proof: Mid-session settings edits cannot mutate a worker profile.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: High - mixing sources makes measurement state incoherent
- Rationale: Set by scaffold input or defaulted for grooming.
