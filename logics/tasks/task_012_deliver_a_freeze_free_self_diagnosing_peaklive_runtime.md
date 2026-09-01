## task_012_deliver_a_freeze_free_self_diagnosing_peaklive_runtime - Deliver a freeze-free, self-diagnosing PeakLive runtime
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 55%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: Codex
> Indicators reviewed: 2026-09-01 11:40:43

# AI Context
- Summary: Orchestrates the seven-phase delivery of req_011: reproduce each audit finding as a failing test, then land observability, the bounded UI thread, the recoverable timeout, enforced replay bounds, input coalescing, and the thread-safe export and recording paths.
- Keywords: deliver, freeze, free, self, diagnosing, peaklive, runtime
- Use when: Implementing or sequencing any part of the freeze-free runtime work, or checking what the next phase is and what evidence the previous one owed.
- Skip when: Picking up a single unrelated defect; the phases are ordered because each makes the next verifiable.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Reproduce the audit findings as failing tests first: controllably slow catalog preparation, a non-returning connect, a UI slowed below the replay parse rate, synthetic input bursts, an export during live acquisition, and a slow free-space probe. Establish the diagnostic log and the exception hooks so every later phase has evidence, then land the observability item.
- [ ] 2. Remove the unbounded catalog wait and the serialized close chain: route profile restore and single-path DBC loading through the existing operation queue with generation-guarded commit, replace the four-wait close with one global budget, and report any worker alive at exit.
- [ ] 3. Give the acquisition timeout an exit: a recovery action from TIMED_OUT onto a fresh adapter and generation, a bounded connect so hardware failure lands in a restartable state, and honest UI wording about the driver handle.
- [ ] 4. Fix the replay backpressure permit accounting, bound decode cost per event-loop turn, and reuse one replay presentation timer; assert the pending-batch bound and the timer and thread counts directly.
- [ ] 5. Introduce the shared coalescing window for the filtered-table projection, the profile persistence, and the A-B statistics, keeping immediate lightweight feedback during the gesture and a guaranteed flush on close and profile switch.
- [ ] 6. Make the export hand-off a stable snapshot with the worker owned by the window, and move the recording space guard onto a documented interval; verify capture integrity and throughput.
- [ ] 7. Run the full validation - ruff, pytest, the trace performance audit script, and the Windows hardware acceptance procedure - record the evidence including which findings remain platform-dependent, close out the Logics task, and leave the repository commit-ready.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_040_give_the_application_a_diagnostic_voice_before_changing_its_behaviour`
- `item_041_remove_the_unbounded_and_serialized_ui_thread_waits`
- `item_042_give_the_acquisition_timeout_an_exit`
- `item_043_make_the_replay_and_ingestion_bounds_hold_in_practice`
- `item_044_coalesce_the_work_driven_by_continuous_pointer_and_keyboard_input`
- `item_045_make_export_and_recording_thread_safe_and_bounded`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC4 -> `item_040_give_the_application_a_diagnostic_voice_before_changing_its_behaviour`. Proof deferred to slice closeout.
- request-AC7 -> `item_040_give_the_application_a_diagnostic_voice_before_changing_its_behaviour`. Proof deferred to slice closeout.
- request-AC8 -> `item_040_give_the_application_a_diagnostic_voice_before_changing_its_behaviour`. Proof deferred to slice closeout.
- request-AC15 -> `item_040_give_the_application_a_diagnostic_voice_before_changing_its_behaviour`. Proof deferred to slice closeout.
- request-AC1 -> `item_041_remove_the_unbounded_and_serialized_ui_thread_waits`. Proof deferred to slice closeout.
- request-AC2 -> `item_041_remove_the_unbounded_and_serialized_ui_thread_waits`. Proof deferred to slice closeout.
- request-AC3 -> `item_041_remove_the_unbounded_and_serialized_ui_thread_waits`. Proof deferred to slice closeout.
- request-AC4 -> `item_041_remove_the_unbounded_and_serialized_ui_thread_waits`. Proof deferred to slice closeout.
- request-AC15 -> `item_041_remove_the_unbounded_and_serialized_ui_thread_waits`. Proof deferred to slice closeout.
- request-AC5 -> `item_042_give_the_acquisition_timeout_an_exit`. Proof deferred to slice closeout.
- request-AC6 -> `item_042_give_the_acquisition_timeout_an_exit`. Proof deferred to slice closeout.
- request-AC15 -> `item_042_give_the_acquisition_timeout_an_exit`. Proof deferred to slice closeout.
- request-AC9 -> `item_043_make_the_replay_and_ingestion_bounds_hold_in_practice`. Proof deferred to slice closeout.
- request-AC10 -> `item_043_make_the_replay_and_ingestion_bounds_hold_in_practice`. Proof deferred to slice closeout.
- request-AC14 -> `item_043_make_the_replay_and_ingestion_bounds_hold_in_practice`. Proof deferred to slice closeout.
- request-AC15 -> `item_043_make_the_replay_and_ingestion_bounds_hold_in_practice`. Proof deferred to slice closeout.
- request-AC11 -> `item_044_coalesce_the_work_driven_by_continuous_pointer_and_keyboard_input`. Proof deferred to slice closeout.
- request-AC15 -> `item_044_coalesce_the_work_driven_by_continuous_pointer_and_keyboard_input`. Proof deferred to slice closeout.
- request-AC12 -> `item_045_make_export_and_recording_thread_safe_and_bounded`. Proof deferred to slice closeout.
- request-AC13 -> `item_045_make_export_and_recording_thread_safe_and_bounded`. Proof deferred to slice closeout.
- request-AC15 -> `item_045_make_export_and_recording_thread_safe_and_bounded`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_011_eliminate_the_remaining_peaklive_freezes_dead_ends_and_silent_failures_found_by_the_ui_thread_audit`
- Product brief(s): `prod_011_peaklive_freeze_free_and_self_diagnosing_workstation`
- Architecture decision(s): (none yet)
