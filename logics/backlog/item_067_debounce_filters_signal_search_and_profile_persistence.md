## item_067_debounce_filters_signal_search_and_profile_persistence - Debounce filters, signal search, and profile persistence
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Low
> Theme: P1 responsiveness
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: debounce, filters, signal, search, profile, persistence
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Each keystroke or pointer event triggers expensive reconstruction and a profile write.

# Scope
- In:
  - Use documented single-shot coalescing for filters, signal search, measurements, and save.
  - Flush pending save on switch and close.
- Out:
  - Trace table virtualization.

# Acceptance criteria
- Burst input causes at most one expensive projection and save per window.
- Lightweight feedback remains immediate and final state is persisted.

# AC Traceability
- request-AC7 -> This backlog slice. Proof: Burst input causes at most one expensive projection and save per window.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - routine typing and dragging rebuild too much work
- Rationale: Set by scaffold input or defaulted for grooming.
