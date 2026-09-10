## item_116_make_bounded_replay_backpressure_recoverable_and_truthful - Make bounded replay backpressure recoverable and truthful
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: High
> Theme: Replay reliability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-10 17:58:37

# AI Context
- Summary: Make bounded replay backpressure tolerate legitimate UI slowness without dropping frames or reporting a false acquisition failure.
- Keywords: bounded, replay, backpressure, recoverable, truthful
- Use when: A valid large trace stops because presentation acknowledgements miss the replay timeout while the UI is still processing batches.
- Skip when: The parser rejects the input, the adapter fails during live acquisition, or the issue is unrelated to replay handoff capacity.

# Problem
- ReplayWorker treats one 250 ms presentation acknowledgement delay as a terminal Replay backpressure timeout, even when the UI is still progressing through valid work.
- The UI performs decoding, projections, and historical persistence synchronously, so a legitimate batch can exceed the acknowledgement deadline under a large trace and populated DBC catalog.
- The resulting message is surfaced through the acquisition-error path, making a presentation throughput mismatch look like a bus or capture failure and leaving the session partially loaded.

# Scope
- In:
  - Define and implement a recoverable bounded handoff policy for replay batches, including explicit stop/cancel escape behavior.
  - Keep permit accounting exact across normal completion, recoverable waiting, cancellation, stale generations, and shutdown.
  - Ensure progress and replay completion are ordered after final presentation acknowledgement.
  - Expose sufficient diagnostics to distinguish parser failure, cancellation, and exhausted presentation capacity.
  - Add deterministic stress fixtures and headless tests for large replay, DBC decode, historical persistence, slow presentation, and cancellation.
- Out:
  - Dropping or sampling frames from the trace, series, frame cache, facts, or historical store.
  - Changing retention capacities or graph downsampling semantics unrelated to the handoff.
  - Adding hardware-only acceptance gates or changing CAN adapter contracts.

# Acceptance criteria
- AC1: A slow-but-progressing UI can complete a large replay without Replay backpressure timeout and without exceeding MAX_PENDING_BATCHES outstanding batches.
- AC2: Frame counts and all existing projections agree before and after the stress replay; no frame is hidden by the recovery policy.
- AC3: Stop, cancellation, and stale-generation abandonment release only permits actually held and finish within the documented bound.
- AC4: Progress remains monotonic, reaches 100% only after presentation drains, and the UI reports replay complete exactly once.
- AC5: Parser exceptions and explicit cancellation retain distinct, actionable messages and do not report success.
- AC6: Focused regression tests and the full CI-equivalent suite pass headlessly; packaging still succeeds.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: A slow-but-progressing UI can complete a large replay without Replay backpressure timeout and without exceeding MAX_PENDING_BATCHES outstanding batches.
- request-AC2 -> This backlog slice. Proof: AC2: Frame counts and all existing projections agree before and after the stress replay; no frame is hidden by the recovery policy.
- request-AC3 -> This backlog slice. Proof: AC3: Stop, cancellation, and stale-generation abandonment release only permits actually held and finish within the documented bound.
- request-AC4 -> This backlog slice. Proof: AC4: Progress remains monotonic, reaches 100% only after presentation drains, and the UI reports replay complete exactly once.
- request-AC5 -> This backlog slice. Proof: AC5: Parser exceptions and explicit cancellation retain distinct, actionable messages and do not report success.
- request-AC6 -> This backlog slice. Proof: AC6: Focused regression tests and the full CI-equivalent suite pass headlessly; packaging still succeeds.
- request-AC7 -> This backlog slice. Proof: AC6: Focused regression tests and the full CI-equivalent suite pass headlessly; packaging still succeeds.
> Shared proof: AC6, AC7

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_023_reliable_large_trace_replay_and_presentation_backpressure`
- Architecture decision(s): (none yet)
- Request: `req_024_prevent_long_trace_replay_from_aborting_on_false_backpressure_timeouts`
- Primary task(s): `task_024_deliver_recoverable_bounded_backpressure_for_large_trace_replay`

# Priority
- Priority: High - valid large traces currently stop part-way through loading and are reported as acquisition failures.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_024_deliver_recoverable_bounded_backpressure_for_large_trace_replay`

# Notes
- Task `task_024_deliver_recoverable_bounded_backpressure_for_large_trace_replay` was finished via `logics-manager flow finish task` on 2026-09-10.
