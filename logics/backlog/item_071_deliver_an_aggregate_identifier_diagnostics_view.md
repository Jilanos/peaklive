## item_071_deliver_an_aggregate_identifier_diagnostics_view - Deliver an aggregate identifier diagnostics view
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: P1 CAN diagnostics
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: deliver, aggregate, identifier, diagnostics, view
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- No view aggregates identifiers, period, delta-t, or counts.

# Scope
- In:
  - Add an O(1)-updated aggregate model.
  - Show ID, latest frame, count, mean period, delta-t, load contribution when known, and decode status by default.
  - Keep it correct for live and replay.
- Out:
  - CAN transmit.

# Acceptance criteria
- Each identifier has one updating row with the specified fields.
- Counts and period metrics match deterministic fixtures.

# AC Traceability
- request-AC8 -> This backlog slice. Proof: Each identifier has one updating row with the specified fields.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - chronological trace alone cannot diagnose a loaded bus
- Rationale: Set by scaffold input or defaulted for grooming.
