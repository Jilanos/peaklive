## item_043_make_the_replay_and_ingestion_bounds_hold_in_practice - Make the replay and ingestion bounds hold in practice
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Enforced ingestion backpressure
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: Fixes the replay semaphore permit accounting that silently disables MAX_PENDING_BATCHES, bounds decode cost per event-loop turn, and reuses one replay presentation timer instead of one per opened trace.
- Keywords: replay, ingestion, bounds, hold, practice
- Use when: Working on replay dispatch, backpressure, the ingest path's per-turn cost, or the timers and threads a replay session owns.
- Skip when: Allowing a frame to skip the trace buffer, series store, frame cache or session facts, or changing the retention capacities and coalescing intervals that already hold.

# Problem
- services/replay_worker.py:107 ignores the result of acquire(timeout=0.25) and dispatches anyway, while the UI releases a permit for that batch through batch_rendered(), so the semaphore gains a permit permanently on every timeout and MAX_PENDING_BATCHES stops bounding anything. request_stop() releases a further MAX_PENDING_BATCHES permits with no accounting.
- ui/ingest_controller.py:303-343 runs decode, trace projection, series projection and session facts entirely on the UI thread, one whole batch per tick, so a tick is not preemptible and the floor on click latency is the cost of a batch: measured at about 15 ms per 512-frame replay batch before real DBC decode.
- ui/session_controller.py:168 creates a new QTimer per opened trace and never destroys the previous one, so a component whose every other retention is bounded grows for the session.

# Scope
- In:
  - Permit-accurate backpressure: track the permits actually held, release only for a permit taken, and account for the stop-time release.
  - Bounding decode cost per event-loop turn, by moving decode to the worker where the frames already cross a thread, or by sizing the unit of work to the responsiveness budget.
  - One long-lived replay presentation timer created with the session state, like the graph and presentation timers.
  - Tests that assert the pending-batch bound directly against a deliberately slowed UI, that assert per-turn cost against the responsiveness budget, and that assert timer and thread counts are stable across repeated trace opens.
- Out:
  - Changing the replay batch semantics so that a frame can be skipped: every frame must still reach the trace buffer, the series store, the frame cache, and the session facts.
  - Changing the bounded retention capacities or the coalescing intervals that already hold.
  - Replacing pyqtgraph or the curve refresh strategy.

# Acceptance criteria
- AC1: With the UI deliberately slowed below the parse rate for a whole replay, the number of dispatched but unrendered batches never exceeds the documented bound, asserted directly rather than inferred from wall time.
- AC2: The permit accounting is exact: after a completed replay and after a stopped replay, the semaphore holds exactly its initial count.
- AC3: One event-loop turn of ingestion stays inside the documented responsiveness budget for both replay and acquisition, and the existing per-stage budgets in analysis/profiling.py remain met.
- AC4: Every frame still reaches the trace buffer, the series store, the frame cache, and the session facts; existing replay, anomaly, and report coverage remains valid.
- AC5: Repeated trace opens leave a stable count of timers, threads, and connections.

# AC Traceability
- request-AC9 -> This backlog slice. Proof: AC1: With the UI deliberately slowed below the parse rate for a whole replay, the number of dispatched but unrendered batches never exceeds the documented bound, asserted directly rather than inferred from wall time.
- request-AC10 -> This backlog slice. Proof: AC2: The permit accounting is exact: after a completed replay and after a stopped replay, the semaphore holds exactly its initial count.
- request-AC14 -> This backlog slice. Proof: AC3: One event-loop turn of ingestion stays inside the documented responsiveness budget for both replay and acquisition, and the existing per-stage budgets in analysis/profiling.py remain met.
- request-AC15 -> This backlog slice. Proof: AC4: Every frame still reaches the trace buffer, the series store, the frame cache, and the session facts; existing replay, anomaly, and report coverage remains valid.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_011_peaklive_freeze_free_and_self_diagnosing_workstation`
- Architecture decision(s): (none yet)
- Request: `req_011_eliminate_the_remaining_peaklive_freezes_dead_ends_and_silent_failures_found_by_the_ui_thread_audit`
- Primary task(s): `task_012_deliver_a_freeze_free_self_diagnosing_peaklive_runtime`

# Priority
- Priority: High - the backpressure bound the design documents stops applying after the first UI slowdown, which is what makes a long replay progressively unresponsive.
- Rationale: Set by scaffold input or defaulted for grooming.
