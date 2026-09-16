## req_033_take_historical_write_backpressure_off_the_gui_thread_during_trace_replay - Take historical write backpressure off the GUI thread during trace replay
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 85
> Confidence: 80
> Complexity: Medium
> Theme: Replay responsiveness

# AI Context
- Summary: Replay still blocks the GUI thread inside `HistoryWriter.submit` when the disk is slow; apply the same non-blocking backpressure the acquisition wind-down already uses.
- Keywords: replay, backpressure, history writer, gui thread, queue wait, responsiveness
- Use when: Working on trace replay responsiveness, historical persistence backpressure, or the `queue_wait` profiling budget.
- Skip when: Changing acquisition stop behaviour (already delivered by task_031), decoding, or recording formats.

# Needs
- Stop the GUI thread from waiting inside `HistoryWriter.submit` while a trace replay ingests, the way `task_031` already stopped it for the acquisition wind-down. Loading a capture onto a slow disk must not cost the operator a frozen window.

# Context
- The acquisition half of this defect was fixed by `task_031`'s stop-stall slice, for live acquisition only. `WorkspaceStopFinalization._presentation_ready` declines a live presentation tick while the writer's bounded queue is full, so the frames stay in the handoff queue and the event loop keeps painting. The replay path (`_drain_replay_batch` -> `_ingest_frames` -> `writer.submit`) was deliberately left unchanged, so it still blocks on the same bounded queue.
- Found while investigating a Windows CI failure on the replay audit in `tests/test_trace_performance.py`. The overrun is `queue_wait`, which is exactly the GUI thread parked in `submit()`.
- Measured evidence that this is a pre-existing gap and not a `task_031` regression - the same audit, same machine, same fixture, on `task_031`'s HEAD and on the commit before it:

| Tree | `queue_wait` | `history_write` | submit calls |
| --- | --- | --- | --- |
| `81f3cae` (after task_031) | 0.49 ms/1k | 21.8 ms/1k | 16 |
| `0630033` (before task_031) | 0.48 ms/1k | 20.3 ms/1k | 16 |

- On the hosted Windows runner the same audit measured `history_write` at 367 ms/1k - within its 400 ms/1k product budget - while `queue_wait` reached 322 ms/1k against a 200 ms/1k CI tolerance. The writer was legally slow; the GUI thread paid for it. Widening that tolerance was considered and rejected: it would hide this defect rather than record it.
- The acquisition-side gate also owns a stall budget (`QUEUE_STALL_TIMEOUT_S`) so a writer that never drains is still failed explicitly instead of deferring forever. Any replay-side equivalent needs the same property, and replay already has its own bounded batch permit contract (`ReplayWorker.MAX_PENDING_BATCHES`) to reconcile with.

# Acceptance criteria
- AC1: Ingesting a replay batch never blocks the GUI thread on historical-write backpressure. Under a fixture whose per-batch write cost is deliberately inflated, a 50 ms GUI heartbeat has no gap above 250 ms for the whole load, and `queue_wait` stays within its product budget rather than a CI tolerance.
- AC2: No accepted frame, sample or bus event is dropped, reordered or double-counted by the deferral; a completed replay still reports the same frame count, trace window, series extent and historical bounds as before.
- AC3: A writer that genuinely never drains is still surfaced as an explicit historical-persistence failure within a bounded budget, with the existing containment (`_fail_history`) and the existing stop/abandon of the replay worker unchanged.
- AC4: The Windows CI tolerance for `queue_wait` in the trace-performance audit is removed or reduced rather than widened, and the audit passes on a hosted runner without it.
- AC5: Before/after evidence records the GUI heartbeat, `queue_wait` and `history_write` for the same synthetic capture, and states any remaining reproduction limit.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Scope
- In:
  - The replay ingestion path's interaction with `HistoryWriter.submit`, and whatever bounded buffer lets a declined tick retry without dropping or reordering records.
  - Reconciling that deferral with `ReplayWorker`'s existing batch-permit backpressure, so the two bounds do not fight or deadlock.
  - The `queue_wait` CI tolerance in the trace-performance audit.
- Out:
  - Acquisition stop behaviour, already delivered by `task_031`.
  - Changing `HistoryWriter`'s own SQL, batching or disk-admission contract.
  - Raising any performance budget to make CI pass.

# Companion docs
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)

# References
- src/peaklive/ui/stop_finalization.py
- src/peaklive/ui/ingest_controller.py
- src/peaklive/ui/session_controller.py
- src/peaklive/services/history_writer.py
- src/peaklive/services/replay_worker.py
- tests/test_trace_performance.py
- tests/test_stop_responsiveness.py
- logics/tasks/task_031_deliver_responsive_stop_and_polished_measurement_workspace_controls.md
- logics/backlog/item_139_diagnose_and_repair_acquisition_stop_stalls_with_follow_live.md (the acquisition half of this defect)

# Backlog
- none
