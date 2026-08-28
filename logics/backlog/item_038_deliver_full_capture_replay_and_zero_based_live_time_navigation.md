## item_038_deliver_full_capture_replay_and_zero_based_live_time_navigation - Deliver full-capture replay and zero-based live time navigation
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 10%
> Complexity: Medium
> Theme: Global X-axis and analyst viewport semantics
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-28 19:31:55

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: deliver, full, capture, replay, zero, based, live, time, navigation
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Completed trace graphs follow the newest data and commonly show only the last few seconds instead of the full capture extent.
- Live acquisition does not consistently expose a stable X-axis origin at zero while the session grows.
- Tail-follow, fit-to-data, and global extent are not expressed as distinct operator choices, making navigation behavior surprising.

# Scope
- In:
  - Separate full-capture fit, global zero-based live extent, and optional follow-tail behavior in the graph navigation model.
  - Make completed replay default to the full available time span and acquisition expand its right bound monotonically from zero.
  - Preserve explicit zoom, cursor, filtering, signal-selection, and follow controls without forcing a disruptive reset on ordinary updates.
  - Add UI tests for short/long traces, sparse timestamps, live growth, and mode transitions.
- Out:
  - Changing sample retention capacity or plot rendering libraries.
  - Playback timing simulation or trace editing.

# Acceptance criteria
- AC5: Completed replay opens with the entire retained capture extent visible, with an explicit control to follow the tail.
- AC6: Acquisition starts at X=0 and expands its global extent monotonically while preserving optional tail-follow navigation.
- AC7: Existing graph controls, cursors, filters, reports, and acquisition lifecycle behavior remain correct.
- AC8: Offscreen tests assert full-extent and live-axis semantics for representative and synthetic traces.

# AC Traceability
- request-AC5 -> This backlog slice. Proof: AC5: Completed replay opens with the entire retained capture extent visible, with an explicit control to follow the tail.
- request-AC6 -> This backlog slice. Proof: AC6: Acquisition starts at X=0 and expands its global extent monotonically while preserving optional tail-follow navigation.
- request-AC7 -> This backlog slice. Proof: AC7: Existing graph controls, cursors, filters, reports, and acquisition lifecycle behavior remain correct.
- request-AC8 -> This backlog slice. Proof: AC8: Offscreen tests assert full-extent and live-axis semantics for representative and synthetic traces.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_009_peaklive_fast_explorable_and_globally_navigable_traces`
- Architecture decision(s): (none yet)
- Request: `req_009_audit_peaklive_performance_and_make_trace_signal_exploration_and_time_navigation_complete`
- Primary task(s): `task_010_deliver_a_measured_lazy_and_globally_navigable_peaklive_trace_workspace`

# Priority
- Priority: High - the current tail-focused viewport hides most of a loaded signal and obscures acquisition history.
- Rationale: Set by scaffold input or defaulted for grooming.
