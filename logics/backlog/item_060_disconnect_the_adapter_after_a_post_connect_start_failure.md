## item_060_disconnect_the_adapter_after_a_post_connect_start_failure - Disconnect the adapter after a post-connect start failure
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Low
> Theme: P0 lifecycle integrity
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: disconnect, adapter, after, post, connect, start, failure
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Failure reserving or opening a recording after connect leaks the adapter handle.

# Scope
- In:
  - Disconnect on every failure after connect.
  - Record the connected state early enough for shutdown cleanup.
  - Test inaccessible target and recorder-start failure.
- Out:
  - New adapter vendors.

# Acceptance criteria
- A failed start disconnects exactly once and a later start can reconnect.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: A failed start disconnects exactly once and a later start can reconnect.
- request-AC5 -> This backlog slice. Proof: A failed start disconnects exactly once and a later start can reconnect.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: High - otherwise the CAN channel is unusable until restart
- Rationale: Set by scaffold input or defaulted for grooming.
