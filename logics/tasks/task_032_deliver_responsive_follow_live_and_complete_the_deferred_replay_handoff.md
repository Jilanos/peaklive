## task_032_deliver_responsive_follow_live_and_complete_the_deferred_replay_handoff - Deliver responsive Follow live and complete the deferred replay handoff
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 95%
> Confidence: 90%
> Progress: 85%
> Complexity: High
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-17 13:27:21

# AI Context
- Summary: Orchestrate replay admission, measured live-follow correction and sustained Windows qualification.
- Keywords: deliver, responsive, follow, live, complete, deferred, replay, handoff
- Use when: Delivering or qualifying the consolidated replay and live-follow responsiveness correction.
- Skip when: Changing unrelated workspace cosmetics, adapters or recording formats.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.
- Confirmed reproduction: Windows 11, build v0.1.2+b202609161508, six curves, full-extent Follow live and recording active. Exercise the first interaction before 15 seconds of acquisition, with the measurement table shown and hidden, then retain the sustained five-minute qualification.

# Priority
- Priority: High
- Rationale: Deliver the reported live responsiveness correction and deferred replay fix before lower-priority workspace work.

# Plan
- [x] 1. Wave 1 (High): record operator answers or retain the explicit provisional defaults; capture baseline reproduction and off/full/trailing timings before modifying either path. Read the prior stop evidence and freeze runbook; inventory overlapping item_123 obligations.
- [x] 2. Wave 2 (High): implement and verify nonblocking replay history admission with exact mixed-record resume/permit accounting, bounded retries, durable completion and failure/cancellation containment; preserve all req_033 criteria.
- [x] 3. Wave 3 (High): profile live Follow fan-out, compare continuous movement with the 30-second look-ahead prototype, implement the effective bounded policy, and verify fresh points, short trailing windows and navigation/session semantics.
- [ ] 4. Wave 4 (High, depends on Waves 2-3, partly open): run real five-minute responsiveness and exact integrity qualification, hosted-Windows queue_wait audit and packaged/operator checks. Keep unavailable evidence visibly pending instead of closing on a Linux-only pass.
- [ ] 5. At each meaningful implementation wave, update affected evidence and commit code/tests/docs together under ADR 009. Start the task through flow start only when implementation actually begins; this corpus creates no implementation proof.
- [ ] 6. Before any new UI copy, run i18n status and honor the existing contract. Run repository checks and Logics lint/audit/validate, refresh the context pack, and close via flow closeout only with complete acceptance proof and a settled product brief.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Commit each meaningful completed wave under ADR 009, including its code, tests and workflow evidence.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_143_complete_nonblocking_ordered_replay_admission_to_historical_persistence`
- `item_144_bound_live_follow_rendering_and_qualify_a_thirty_second_axis_look_ahead`
- `item_145_qualify_whole_application_follow_and_replay_responsiveness_on_windows`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful implementation waves follow ADR 009 with affected docs updated and each completed wave committed.

# AC Traceability
- request-AC2 -> `item_143_complete_nonblocking_ordered_replay_admission_to_historical_persistence`. Proof deferred to slice closeout.
- request-AC3 -> `item_143_complete_nonblocking_ordered_replay_admission_to_historical_persistence`. Proof deferred to slice closeout.
- request-AC7 -> `item_143_complete_nonblocking_ordered_replay_admission_to_historical_persistence`. Proof deferred to slice closeout.
- request-AC8 -> `item_143_complete_nonblocking_ordered_replay_admission_to_historical_persistence`. Proof deferred to slice closeout.
- request-AC1 -> `item_144_bound_live_follow_rendering_and_qualify_a_thirty_second_axis_look_ahead`. Proof deferred to slice closeout.
- request-AC4 -> `item_144_bound_live_follow_rendering_and_qualify_a_thirty_second_axis_look_ahead`. Proof deferred to slice closeout.
- request-AC5 -> `item_144_bound_live_follow_rendering_and_qualify_a_thirty_second_axis_look_ahead`. Proof deferred to slice closeout.
- request-AC6 -> `item_144_bound_live_follow_rendering_and_qualify_a_thirty_second_axis_look_ahead`. Proof deferred to slice closeout.
- request-AC7 -> `item_144_bound_live_follow_rendering_and_qualify_a_thirty_second_axis_look_ahead`. Proof deferred to slice closeout.
- request-AC1 -> `item_145_qualify_whole_application_follow_and_replay_responsiveness_on_windows`. Proof deferred to slice closeout.
- request-AC2 -> `item_145_qualify_whole_application_follow_and_replay_responsiveness_on_windows`. Proof deferred to slice closeout.
- request-AC3 -> `item_145_qualify_whole_application_follow_and_replay_responsiveness_on_windows`. Proof deferred to slice closeout.
- request-AC4 -> `item_145_qualify_whole_application_follow_and_replay_responsiveness_on_windows`. Proof deferred to slice closeout.
- request-AC5 -> `item_145_qualify_whole_application_follow_and_replay_responsiveness_on_windows`. Proof deferred to slice closeout.
- request-AC6 -> `item_145_qualify_whole_application_follow_and_replay_responsiveness_on_windows`. Proof deferred to slice closeout.
- request-AC7 -> `item_145_qualify_whole_application_follow_and_replay_responsiveness_on_windows`. Proof deferred to slice closeout.
- request-AC8 -> `item_145_qualify_whole_application_follow_and_replay_responsiveness_on_windows`. Proof deferred to slice closeout.

# Validation
- Wave 1 baseline (Linux, this repository at 5305b5b, offscreen Qt): focused suites
  `test_replay_integrity`, `test_history_writer`, `test_replay_ordered_transport`,
  `test_stop_responsiveness`, `test_graph_navigation` - 48 passed.
- Wave 2 regression `tests/test_replay_backpressure.py` (3072-frame, three-lane synthetic
  capture; each persisted batch slowed to 120 ms). With the repair: 5 passed. With
  admission neutralised so `submit()` blocks as before, two of them fail: the GUI thread
  accumulates 0.298 s inside `HistoryWriter.submit` against a 0.05 s bound, and the
  stalled-writer containment test fails outright.
- The primary regression measures the `queue_wait` stage - the time the GUI thread spends
  inside `submit` - rather than a wall-clock heartbeat gap. An earlier heartbeat-only
  version passed in isolation at 0.069 s but reached 0.294 s when the whole suite ran in
  one interpreter, which measures host contention rather than the defect. The heartbeat
  assertion is retained alongside it; the stage measurement is what fails the baseline.
- Wave 2 `queue_wait` before/after on the same audit fixture
  (`scripts/audit_trace_performance.py`, 200 000 frames, 16 signals): 0.49 ms/1k frames
  recorded for req_033 after task_031, 0.03 ms/1k frames now - inside the unchanged
  50 ms/1k product budget. `history_write` stays dominant at 372.67 ms/1k, inside its
  400 ms/1k budget.
- Wave 3 off/full/trailing comparison on one fixture (six lanes, 3 s live acquisition,
  `tests/test_follow_live_responsiveness.py`), as (axis moves, view notifications,
  max 50 ms-heartbeat gap):
  - Follow off: (0, 0, 0.068 s)
  - Follow full, continuous policy: (88, 88, 0.071 s)
  - Follow trailing, continuous policy: (86, 86, 0.107 s)
  - Follow full, 30 s look-ahead policy: (1, 2, 0.069 s)
  - Follow trailing, look-ahead policy: (1, 2, 0.077 s)
  The stepped policy removes about 99% of follow-driven range and notification work,
  well beyond the 50% req_034 AC5 asks for as supporting evidence.
- Wave 4 boundary semantics, `tests/test_follow_axis_boundaries.py` (15 cases, deterministic:
  the extent is driven directly, so no wall clock decides a boundary). Covers the initial
  reserve, the axis held still until data reaches the edge, a 10 000 s timestamp jump
  absorbed in one update, an idle session fabricating nothing, trailing span W preserved
  with look-ahead capped at W/4, reset on mode/session change, and immediate catch-up on
  re-enable.
- Wave 4 lane matrix, `tests/test_follow_live_qualification.py` (7 cases): no lanes, one,
  six and nine; recording on and off; measurement table shown and hidden; final extent
  after Stop; three repeated start/stop cycles. All within the 200 ms control-feedback,
  250 ms heartbeat-gap and 500 ms point-age budgets, with no dropped frames and no
  historical-persistence failure.
- Wave 4 sustained run (Linux, offscreen Qt, `PEAKLIVE_QUALIFY=1`, six lanes, recording
  active, 300 s of real event loop): 1 133 312 frames accepted; 12 axis moves, so at least
  ten look-ahead boundaries were crossed; heartbeat gap max 0.181 s and p95 0.074 s against
  the 250 ms budget; slowest control `mode_trailing` at 0.0145 s against the 200 ms budget.
  Recorded limitation: the point-age metric compares the newest accepted sample with the
  newest drawn point and read 0.000 s throughout, so it confirms the curve is never left
  behind but is too coarse to resolve sub-refresh staleness; it is not evidence of
  zero display latency.
- The sustained case is opt-in behind `PEAKLIVE_QUALIFY=1`: CI applies a 120 s per-test
  faulthandler timeout on Linux and a 300 s per-module bound on Windows, so a five-minute
  test cannot run in the ordinary suite.
- Full repository suite and Ruff: see the Report below.

# Report
- Wave 1 established the baseline and found the overlap with `item_123` to be the
  historical viewport scheduler, which this task reuses rather than rewrites.
- Wave 2 delivered nonblocking, resumable replay admission. `_drain_replay_batch` now
  checks historical writer capacity before each frame group instead of once per batch,
  defers at an exact record index, keeps the worker permit held until the batch is fully
  projected, and bounds a non-draining writer on absence of durable progress rather than
  on a blocking wait. The Windows-only 200 ms/1k `queue_wait` tolerance in
  `tests/test_trace_performance.py` is removed; the stage is now asserted to be measured
  and held to the product budget on every operating system.
- Wave 3 found and repaired a defect the measurement exposed: every lane's view box was
  connected to `_x_range_changed`, so a linked lane merely mirroring the anchor - including
  from its own `resizeEvent` - was read as a manual navigation and silently cleared Follow
  live on any relayout of a multi-lane stack. Only the anchor now reports. With following
  actually staying on, the continuous policy was measured at one axis move per refresh,
  and the 30-second look-ahead policy replaced it.
- Not established: no measured reproduction of the operator's whole-application slowdown
  was obtained on this Linux fixture; all three configurations stayed inside the 250 ms
  heartbeat budget at six lanes over three seconds. The work above is an isolation of
  follow-specific cost and a repair of two defects found on that path, not a confirmed
  root cause of the reported symptom.
- The 400-line UI module budget guarded by `tests/test_ui_structure.py` was respected by
  extracting the replay drain, admission check and backpressure bound into a new
  `src/peaklive/ui/replay_admission.py` mixin rather than by raising the budget.
- Pre-existing on this Linux/offscreen environment, unchanged by this work and verified
  against 5305b5b in a clean worktree: `test_ui.py::test_main_window_has_accessible_workspace_and_explicit_lifecycle`
  and `test_ui_analyst.py::test_layout_geometry_and_collapse_state_persist_across_a_restart`.
- Wave 4 delivered its Linux half: boundary semantics, the lane matrix and the sustained
  five-minute run above. A defect the boundary cases exposed is repaired - Fit's own edge
  margin was trimmed flush to the last sample by the next follow refresh, so a window that
  already shows the whole extent is now left alone.
- Wave 4 open gates, which a synthetic Linux pass cannot close and which are not claimed:
  the revised hosted-Windows `queue_wait` audit (the 200 ms/1k tolerance was removed on
  Linux evidence and hosted Windows must confirm it), qualification of the packaged
  `PeakLive.exe`, and confirmation on the operator's own machine against the reported
  build v0.1.2+b202609161508.

# Links
- Request: `req_034_restore_application_responsiveness_with_follow_live_and_nonblocking_replay_history`
- Product brief(s): `prod_031_responsive_live_graph_following_and_lossless_replay_presentation`
- Architecture decision(s): (none yet)
