## item_143_complete_nonblocking_ordered_replay_admission_to_historical_persistence - Complete nonblocking ordered replay admission to historical persistence
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 65%
> Complexity: High
> Theme: Replay backpressure and integrity
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-17 13:27:21

# AI Context
- Summary: Complete req_033 with nonblocking, ordered and bounded replay history admission.
- Keywords: complete, nonblocking, ordered, replay, admission, historical, persistence
- Use when: Delivering or qualifying the consolidated replay and live-follow responsiveness correction.
- Skip when: Changing unrelated workspace cosmetics, adapters or recording formats.

# Problem
- The replay consumer removes a batch before calling a potentially blocking writer submit, so a valid slow disk still stalls the GUI.
- Mixed event/frame groups can produce multiple submissions per replay batch; naive whole-batch retries duplicate already applied projections.

# Scope
- In:
  - Implement nonblocking admission and resumable ordered consumption with explicit ownership of deferred records/samples; choose the smallest safe approach from measured code paths.
  - Document hard bounds for deferred work, the writer queue and replay permits, including at most one extra bounded in-flight projection if needed; never acknowledge before ownership has safely transferred.
  - Track actual writer progress for timeout detection without GUI waits, busy retry loops or unbounded timer events; preserve error cause, containment and generation fencing.
  - Keep source-consumed, projected and durably-persisted milestones distinct and final completion truthful.
  - Carry forward req_033 AC1-AC5 without weakening them: heartbeat, integrity, stuck-writer containment, Windows queue_wait audit and before/after evidence.
- Out:
  - Changing SQL summary algorithms, on-disk formats or disk admission rules.
  - Assuming replay repair alone fixes live-follow rendering.

# Acceptance criteria
- AC1: Slow persistence saturates the bounded queue without any GUI-thread capacity wait; heartbeat maximum is 250 ms and queue_wait meets the unchanged 50 ms/1k product budget.
- AC2: Interleaved frame/event records, full queues and repeated retries preserve exact order/counts, sample bounds and permit ownership, with no premature durable completion.
- AC3: Never-draining writer, writer failure between admission and submission, cancellation, stale completion and restart terminate safely; a progressing load longer than five seconds remains valid.
- AC4: Existing replay/integrity/stop tests plus a regression exposing the original block pass; same-fixture before/after queue_wait/history_write and revised Windows audit are recorded.

# AC Traceability
- request-AC2 -> This backlog slice. Proof deferred to slice closeout: nonblocking replay heartbeat and exact ordered consumption.
- request-AC3 -> This backlog slice. Proof deferred to slice closeout: bounded stalled-writer containment and generation-safe cancellation.
- request-AC7 -> This backlog slice. Proof deferred to slice closeout: retained data, recording and finalization integrity.
- request-AC8 -> This backlog slice. Proof deferred to slice closeout: regression results and hosted/packaged Windows evidence.

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
- Rationale: The last development explicitly deferred a GUI-blocking replay path and Windows audit gap.
