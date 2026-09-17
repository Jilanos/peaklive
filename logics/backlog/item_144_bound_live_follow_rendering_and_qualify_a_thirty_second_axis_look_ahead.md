## item_144_bound_live_follow_rendering_and_qualify_a_thirty_second_axis_look_ahead - Bound live-follow rendering and qualify a thirty-second axis look-ahead
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 85%
> Complexity: High
> Theme: Live graph responsiveness
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-17 13:27:21

# AI Context
- Summary: Restore live-follow responsiveness and evaluate a 30-second stepped axis with continuously updated points.
- Keywords: bound, live, follow, rendering, qualify, thirty, second, axis, look, ahead
- Use when: Delivering or qualifying the consolidated replay and live-follow responsiveness correction.
- Skip when: Changing unrelated workspace cosmetics, adapters or recording formats.

# Problem
- The previous stop-focused experiment does not cover sustained live-follow responsiveness; axis changes can fan out into layout, viewport and measurement work.
- Moving only the axis every 30 seconds may reduce work, but delaying points, starving refresh, growing worker queues or hiding the latest data would not satisfy the operator need.

# Scope
- In:
  - Profile the actual acquisition and replay graph routes and their range-change callbacks; distinguish CPU-bound painting, historical reads, measurements and queue stalls.
  - Separate ingestion, incoming-point presentation and automatic axis movement; coalesce redundant presentation and range notifications at bounded cadence. Reuse existing viewport work where appropriate and avoid an unrelated scheduler rewrite.
  - Prototype full-mode [0, newest timestamp + 30 seconds] on enable and keep it fixed until data reaches the reserved edge, then advance directly to newest + 30 seconds. Drive boundaries from session data time, using monotonic time only for scheduling and latency. Idle acquisition does not fabricate data or advance the actual extent.
  - For trailing mode use the existing selected span W, with proposed look-ahead min(30 seconds, W/4), and right edge newest + look-ahead; keep W fixed. Advance at the right-edge boundary without clipping the newest sample. Operator answers can revise this provisional policy before implementation.
  - Handle large timestamp jumps in one update, never one catch-up iteration per missed interval. Reset reserved range on mode/session changes; re-enable catches up once and manual navigation cancels pending automatic moves.
  - Ensure actual history/sample bounds remain independent of display padding; A/B beyond the newest real sample must retain truthful no-data behavior, not extrapolation.
  - On Stop/final replay settle to the real final extent only if Follow remains enabled, retain the follow preference, preserve a manually chosen viewport, and stop periodic follow work.
  - Ship the prototype when measured effective; otherwise repair the measured bottleneck with a bounded alternative and record the decision, latency and range-work comparison.
- Out:
  - Freezing curves for 30 seconds, globally disabling Follow, altering capture timestamps or discarding acquisition data.
  - Silently widening a manually selected short trailing window.

# Acceptance criteria
- AC1: Reproducible off/full/trailing evidence isolates the dominant work and records whether turning Follow off removes the slowdown.
- AC2: The delivered policy meets 200 ms control feedback, 250 ms maximum heartbeat gap and 500 ms point freshness across ten real boundaries, with bounded queues and background work.
- AC3: An effective look-ahead implementation updates points between axis moves and covers short/long trailing spans, empty/first sample, idle gaps, jumps, toggles, manual zoom, Fit/Fit Y and finalization without false sample bounds.
- AC4: Before/after continuous-versus-stepwise evidence justifies the selected implementation; exact retained data, A/B values and historical event fidelity remain correct.

# AC Traceability
- request-AC1 -> This backlog slice. Proof deferred to slice closeout: matched before/after follow-mode and first-click measurements.
- request-AC4 -> This backlog slice. Proof deferred to slice closeout: sustained input latency, heartbeat and incoming-point freshness.
- request-AC5 -> This backlog slice. Proof deferred to slice closeout: measured continuous-versus-stepped policy decision.
- request-AC6 -> This backlog slice. Proof deferred to slice closeout: axis padding, short-window and manual-navigation semantics.
- request-AC7 -> This backlog slice. Proof deferred to slice closeout: retained data, recording and finalization integrity.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_031_responsive_live_graph_following_and_lossless_replay_presentation`
- Architecture decision(s): (none yet)
- Request: `req_034_restore_application_responsiveness_with_follow_live_and_nonblocking_replay_history`
- Primary task(s): `task_032_deliver_responsive_follow_live_and_complete_the_deferred_replay_handoff`

# Priority
- Priority: High
- Rationale: Enabling Follow live slows the entire application in the reported six-curve live session.
