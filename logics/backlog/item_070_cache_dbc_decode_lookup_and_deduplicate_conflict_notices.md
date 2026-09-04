## item_070_cache_dbc_decode_lookup_and_deduplicate_conflict_notices - Cache DBC decode lookup and deduplicate conflict notices
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: P1 decoding performance
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: cache, dbc, decode, lookup, deduplicate, conflict, notices
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- DBC candidates are rebuilt per frame and one conflict can restyle UI per frame.

# Scope
- In:
  - Cache active decode lookup by identifier.
  - Avoid exception-led unknown-ID flow.
  - Report each conflict once per session.
- Out:
  - Changing DBC conflict policy.

# Acceptance criteria
- Repeated unknown IDs avoid repeated exception work.
- A sustained conflict produces one visible report per identifier/session.

# AC Traceability
- request-AC7 -> This backlog slice. Proof: Repeated unknown IDs avoid repeated exception work.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - repeated lookup and style repolish are per-frame costs
- Rationale: Set by scaffold input or defaulted for grooming.
