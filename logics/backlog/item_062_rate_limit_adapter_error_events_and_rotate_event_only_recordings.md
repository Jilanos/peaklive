## item_062_rate_limit_adapter_error_events_and_rotate_event_only_recordings - Rate-limit adapter error events and rotate event-only recordings
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: P0 adapter recovery
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: rate, limit, adapter, error, events, rotate, event, only, recordings
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Persistent driver errors spin hot, queue unlimited signals, and grow event-only recordings without rotation.

# Scope
- In:
  - Deduplicate and rate-limit identical error events.
  - Back off receive after errors.
  - Rotate after event writes.
  - Implement bounded automatic reconnect with visible alert.
- Out:
  - Hardware certification.

# Acceptance criteria
- Persistent error has bounded signal and recording rate.
- Automatic reconnect attempts are bounded and alerted.
- Fatal adapter absence reaches a restartable error state.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: Persistent error has bounded signal and recording rate.
- request-AC4 -> This backlog slice. Proof: Automatic reconnect attempts are bounded and alerted.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: High - a disconnected device can flood UI and disk
- Rationale: Set by scaffold input or defaulted for grooming.
