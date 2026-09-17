## req_034_restore_application_responsiveness_with_follow_live_and_nonblocking_replay_history - Restore application responsiveness with Follow live and nonblocking replay history
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Whole-application live and replay responsiveness
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-17 12:50:29

# AI Context
- Summary: Consolidate deferred replay admission and the reported six-curve full-extent live-follow slowdown.
- Keywords: restore, application, responsiveness, follow, live, nonblocking, replay, history
- Use when: Delivering or qualifying the consolidated replay and live-follow responsiveness correction.
- Skip when: Changing unrelated workspace cosmetics, adapters or recording formats.

# Priority
- Priority: High - whole-application live responsiveness and the deferred replay block affect the core acquisition workflow.

# Needs
- Deliver the replay historical-write backpressure work documented but not implemented after task_031, retaining all five acceptance criteria of req_033.
- Correct the operator-confirmed loss of responsiveness across the application once Follow live is enabled, including steady acquisition and ordinary controls rather than only Stop.
- Measure and implement the proposed 30-second look-ahead axis policy if it effectively restores responsiveness while keeping incoming samples visible and all accepted data intact.
- Keep the remaining operator questions, provisional defaults and evidence-dependent release gates explicit so implementation can start without inventing a confirmed root cause.

# Context
- Operator report on 2026-09-17: testing confirms the entire application becomes much less responsive once Follow live is enabled. The proposed alternative is to reserve 30 seconds ahead of the curve and repeat every 30 seconds if effective. The report establishes a symptom and correlation, not an isolated root cause or a measured fix.
- Repository baseline: 108c88d records req_033 after completed task_031. Its deferred replay scope is incorporated here; retire req_033 through the workflow CLI with this request as its replacement after verifying coverage. Do not reopen or erase the delivered stop evidence.
- item_139 compared off/full/trailing during a six-second synthetic stop experiment and repaired an unbounded wind-down drain. Its statement that Follow live was not a factor is limited to that fixture and stop path; it does not disprove this new steady-state or long-session operator report.
- Confirmed code path: _drain_replay_batch pops a batch then _ingest_replay_records may call _ingest_frames several times for interleaved frame/event groups. Each group can submit history. A single queue-capacity check before an entire mixed batch is insufficient unless capacity for all submissions is guaranteed. Deferred consumption must resume at an exact ordered position without replaying projections or acknowledging early.
- HistoryWriter currently bounds its queue to eight batches and submit can block the caller; replay has its own four-batch permit bound. Preserve both bounds and exact ownership. The current 5-second no-progress stall budget must become event-loop-friendly, reset on durable progress, and remain an explicit failure for a genuinely stuck writer.
- Confirmed candidate graph path: live _render_frames flushes graphs; GraphStackPanel.refresh_data applies _apply_follow to the in-memory path, which calls setXRange and emits view_changed. The historical path schedules/cancels HistoryViewportWorker and has a 75 ms viewport timer. Profile signal fan-out, shared-axis relayout, curve preparation, measurement refresh and worker scheduling separately before attributing the slowdown.
- req_033 evidence: queue_wait was 0.49 versus 0.48 ms/1k frames on the same Linux fixture after/before task_031; on hosted Windows it reached 322 ms/1k while history_write was 367 ms/1k within its 400 ms/1k budget. The product queue_wait budget is 50 ms/1k; the existing 200 ms/1k Windows tolerance is not a product target and must not be widened.
- Operator-confirmed axis behavior: incoming points continue updating while automatic X-axis movement advances in 30-second steps with blank future space. This is neither future-value prediction nor a 30-second delay in acquisition, persistence or curve refresh. Adoption still depends on measured effectiveness.
- Operator-confirmed reproduction: build v0.1.2+b202609161508, live CAN acquisition, full-extent Follow from the beginning, six displayed curves, slowdown perceptible at the first click on the screen. No Follow-disable comparison has been performed; do not claim immediate recovery. The report does not establish whether the click causes the slowdown or merely reveals it.
- Operator clarification: the same slowdown occurs with the A/B/statistics table visible and hidden, so hiding it is not an accepted remedy. Remaining reproduction questions: recording active or inactive; OS and hardware; approximate CAN frame rate and elapsed acquisition duration before the first click; whether disabling Follow restores responsiveness. File loading and trailing mode are regression coverage, not operator-reported reproductions. These unknowns do not block a synthetic six-lane reproduction; record fixture defaults explicitly.
- Operator-confirmed short-window behavior: preserve the trailing span and reduce the advance instead of widening it. Engineering default to validate: min(30 seconds, one quarter of the selected span), leaving at least three quarters for recent history.
- Provisional acceptance targets reuse the previous 200 ms input-feedback and 250 ms maximum heartbeat-gap contract and add a 500 ms maximum incoming-point display age at supported load. Record fixture capacity explicitly. Missing operator hardware details do not block synthetic diagnosis, but operator-machine/packaged-Windows confirmation remains a qualification gate and cannot be replaced by a Linux pass.
- No implementation or performance measurement is claimed by this corpus. Existing local deletions under logics/external are operator-owned; use generated/anonymized fixtures and never require or commit those removed files. Coordinate any overlap with item_123's existing viewport scheduling scope and record which acceptance work this task actually delivers.

# Acceptance criteria
- AC1: Record an identical-workload before/after matrix for Follow off/full/trailing during steady acquisition, enable/disable transitions, replay and Stop; prioritize the reported six-lane full-extent live session and first-click latency, then include no lanes, one lane and nine dense lanes, visible/hidden measurements and recording on/off. Record build, platform, lane count, rate, session age, input latency, heartbeat, data freshness, CPU, queue depth, X-range updates and relevant stage timings. Separate observed causes from hypotheses.
- AC2: Replay never waits for historical writer capacity on the GUI thread: a 50 ms heartbeat has no gap above 250 ms under deliberately slow-but-progressing persistence. Mixed frame/event batches retain order, each frame/sample/event is projected exactly once, permits remain exact and bounded, and completion awaits durable final settlement.
- AC3: Replay cancellation, close, restart and stale generations remain bounded and safe; a writer with no durable progress fails through existing _fail_history containment within the documented stall budget plus one responsive timer turn. A slowly progressing writer is not failed merely because total load time exceeds that budget.
- AC4: At the documented supported stress load, Follow live keeps menu opening, view switching, Follow toggle and Stop feedback within 200 ms, maximum 50 ms-heartbeat gap within 250 ms and incoming-point display age within 500 ms. Measure across at least ten real 30-second boundaries (five minutes), including boundary spikes; do not qualify from only average timings or a six-second stop test.
- AC5: Compare the existing continuous-axis policy with a 30-second look-ahead prototype on the same fixture. Ship the stepwise policy if it meets AC4 and materially reduces measured follow-related work; target at least 50 percent fewer range/layout operations as supporting evidence, not a replacement for latency. If ineffective or damaging to graph semantics, implement an evidence-backed bounded alternative and record why; do not merely disable Follow or leave the reported slowdown unresolved.
- AC6: With the stepwise policy, full mode starts at zero and keeps all acquired history visible with a future right edge; new points remain visible between moves. Trailing mode preserves the selected span with bounded look-ahead. Manual pan/zoom disables Follow, re-enable catches up immediately, Fit/Fit Y and A/B remain correct, and gaps, timestamp jumps, empty sessions, mode changes and restarts cannot create catch-up loops or move another session's viewport. Blank future space never changes actual sample/history bounds or produces fabricated values.
- AC7: No accepted frames, samples, bus events or recording records are dropped, duplicated or reordered to improve responsiveness. Historical envelopes and rare events keep existing fidelity, queues/caches/workers stay explicitly bounded, and stopped/replayed sessions expose their real final extent with truthful durable-completion status. Preserve the prior less-than-3-seconds-or-visible-finalization-feedback stop contract.
- AC8: Meaningful regressions fail against the baseline and pass with the repair; before/after replay evidence includes queue_wait and history_write. Product budgets remain unchanged, the 200 ms/1k Windows queue_wait tolerance is removed or reduced toward the 50 ms/1k product budget, and hosted Windows passes the revised audit. Run focused suites, Ruff and repository CI checks, and record packaged-Windows/operator qualification or leave the corresponding gate open with the specific missing evidence.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_031_responsive_live_graph_following_and_lossless_replay_presentation`
- Architecture decision(s): (none yet)

# References
- logics/request/req_033_take_historical_write_backpressure_off_the_gui_thread_during_trace_replay.md
- logics/tasks/task_031_deliver_responsive_stop_and_polished_measurement_workspace_controls.md
- logics/backlog/item_139_diagnose_and_repair_acquisition_stop_stalls_with_follow_live.md
- logics/backlog/item_123_bound_viewport_scheduling_and_expose_truthful_loading_and_measurement_states.md
- logics/runbook/run_001_capture_a_peaklive_freeze_with_local_diagnostics.md
- src/peaklive/ui/session_controller.py
- src/peaklive/ui/ingest_controller.py
- src/peaklive/ui/stop_finalization.py
- src/peaklive/ui/live_handoff.py
- src/peaklive/ui/panels/graph_navigation.py
- src/peaklive/ui/panels/graph_stack.py
- src/peaklive/ui/panels/graph_history.py
- src/peaklive/ui/panels/measurement.py
- src/peaklive/services/history_writer.py
- src/peaklive/services/history_worker.py
- src/peaklive/services/replay_worker.py
- src/peaklive/analysis/profiling.py
- tests/test_trace_performance.py
- tests/test_stop_responsiveness.py
- tests/test_graph_navigation.py
- tests/test_replay_integrity.py

# Backlog
- `item_143_complete_nonblocking_ordered_replay_admission_to_historical_persistence`
- `item_144_bound_live_follow_rendering_and_qualify_a_thirty_second_axis_look_ahead`
- `item_145_qualify_whole_application_follow_and_replay_responsiveness_on_windows`
