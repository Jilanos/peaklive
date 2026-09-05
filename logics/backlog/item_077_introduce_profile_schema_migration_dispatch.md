## item_077_introduce_profile_schema_migration_dispatch - Introduce profile schema migration dispatch
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Low
> Theme: P1 profile evolution
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: introduce, profile, schema, migration, dispatch
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Migration is inferred from keys and ambiguous filter fields coexist.

# Scope
- In:
  - Read schema version.
  - Dispatch known migrations.
  - Clarify typed filter versus DBC state names.
- Out:
  - Changing persisted user semantics.

# Acceptance criteria
- Fixtures from supported schema versions migrate deterministically.
- Unknown future versions fail safely with an operator-visible outcome.

# AC Traceability
- request-AC9 -> This backlog slice. Proof: Fixtures from supported schema versions migrate deterministically.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - schema version is written but never read
- Rationale: Set by scaffold input or defaulted for grooming.
