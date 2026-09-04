## item_066_make_profile_writes_durable_and_multi_instance_safe - Make profile writes durable and multi-instance safe
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Low
> Theme: P0 profile integrity
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: profile, writes, durable, multi, instance, safe
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- A fixed temporary name and no fsync make profile writes vulnerable to interruption and concurrent instances.

# Scope
- In:
  - Use unique temporary names.
  - Flush and fsync before replace.
  - Test failure and collision paths.
- Out:
  - Cross-machine profile sync.

# Acceptance criteria
- Concurrent stores never share a temporary filename.
- Successful writes fsync before replace and failed writes preserve a readable prior file.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: Concurrent stores never share a temporary filename.
- request-AC5 -> This backlog slice. Proof: Successful writes fsync before replace and failed writes preserve a readable prior file.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: High - atomic replace alone can lose or collide with profile data
- Rationale: Set by scaffold input or defaulted for grooming.
