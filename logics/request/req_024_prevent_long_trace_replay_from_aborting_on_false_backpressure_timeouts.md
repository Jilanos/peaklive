## req_024_prevent_long_trace_replay_from_aborting_on_false_backpressure_timeouts - Prevent long trace replay from aborting on false backpressure timeouts
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Reliable bounded trace replay
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-10 17:58:36

# AI Context
- Summary: Make replay presentation backpressure recoverable for valid large traces while keeping queue bounds, cancellation, and frame integrity explicit.
- Keywords: prevent, long, trace, replay, aborting, false, backpressure, timeouts
- Use when: A valid ASC/TRC replay stops part-way through with `Replay backpressure timeout` while the UI is still processing batches.
- Skip when: The capture is malformed, the parser raises an error before presentation begins, or the issue concerns live adapter transport rather than replay handoff.

# Needs
- Allow a large ASC or TRC trace to finish loading when UI ingestion temporarily falls behind parsing.
- Keep replay memory and event-loop work bounded without treating a transient presentation delay as a fatal acquisition error.
- Preserve every parsed frame and keep progress, completion, cancellation, and failure states truthful.

# Context
- Opening the existing large trace can stop after about 36.7 seconds with 'Acquisition error: Replay backpressure timeout'.
- ReplayWorker dispatches batches of 256 frames and permits only MAX_PENDING_BATCHES (currently four) outstanding batches.
- The worker waits ACKNOWLEDGEMENT_TIMEOUT_S (currently 0.25 seconds) for the UI to acknowledge a batch; failure emits Replay backpressure timeout and returns before replay completion.
- The UI drains one replay batch per timer turn and performs DBC decoding, trace projection, series projection, session facts, and historical SQLite writes on the UI thread.
- A 182 MB trace is present in the external fixtures and can expose the mismatch between parser throughput and UI ingestion cost; the existing focused regression test intentionally verifies timeout when acknowledgements never arrive.
- The previous bounded-ingestion work fixed permit accounting and event-loop bounds, but its finite acknowledgement timeout remains too strict for a legitimate slow batch and currently surfaces as a generic acquisition failure.

# Acceptance criteria
- AC1: A deterministic large-trace replay whose UI presentation is slower than parsing completes successfully without emitting Replay backpressure timeout, while the number of dispatched but unrendered batches never exceeds the documented bound.
- AC2: Every parsed frame still reaches the trace buffer, frame cache, series store, session facts, and historical signal store according to the existing replay contract; no silent frame dropping is introduced to hide backpressure.
- AC3: Replay cancellation and window shutdown remain bounded and cannot wait forever for a presentation acknowledgement; abandoned generations cannot release permits or deliver stale batches into a newer session.
- AC4: Progress is monotonic and reaches the source size only after the final batch has been acknowledged; replay completion is announced only after all queued presentation work has been consumed.
- AC5: A genuine parser or decode failure remains visible as a failure with its original cause, while a recoverable presentation delay is not mislabeled as an acquisition or bus error.
- AC6: Headless tests cover a deliberately slow UI, a large capture with selected DBC signals and historical persistence, cancellation during backlog, exact permit accounting, frame-count integrity, progress monotonicity, and successful completion; existing intentional no-ack timeout coverage is updated to distinguish unrecoverable abandonment from recoverable slowness.
- AC7: Ruff and the complete CI test suite pass under QT_QPA_PLATFORM=offscreen, and the Windows packaging path remains valid.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_023_reliable_large_trace_replay_and_presentation_backpressure`
- Architecture decision(s): (none yet)

# References
- src/peaklive/services/replay_worker.py
- src/peaklive/ui/session_controller.py
- src/peaklive/ui/ingest_controller.py
- src/peaklive/analysis/history.py
- tests/test_replay_worker.py
- tests/test_replay_integrity.py
- tests/test_trace_performance.py
- logics/backlog/item_043_make_the_replay_and_ingestion_bounds_hold_in_practice.md
- logics/request/req_011_eliminate_the_remaining_peaklive_freezes_dead_ends_and_silent_failures_found_by_the_ui_audit.md

# Backlog
- `item_116_make_bounded_replay_backpressure_recoverable_and_truthful`
- `item_043_make_the_replay_and_ingestion_bounds_hold_in_practice` (predecessor implementation and constraint)
