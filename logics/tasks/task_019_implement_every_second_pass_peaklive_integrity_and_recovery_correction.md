## task_019_implement_every_second_pass_peaklive_integrity_and_recovery_correction - Implement every second-pass PeakLive integrity and recovery correction
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.

# AI Context
- Summary: Orchestrate all thirteen second-pass corrections in six code-only implementation waves, then author and execute every regression and repository gate once in the final verification phase.
- Keywords: second-pass, implementation-waves, integrity, recovery, identity, deferred-testing, final-verification
- Use when: Implementing req_019 or coordinating its seven backlog slices across acquisition, replay, storage, CAN identity, signal identity, profiles, and trace UI.
- Skip when: Running isolated incremental tests before all six waves are complete, addressing unrelated audit work, or implementing only the earlier broad audit.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Implementation wave 1: redesign the live acquisition handoff and Stop/finalization ordering so authoritative ingestion is complete, exactly once, generation-safe, and bounded. Do not run any tests in this wave.
- [ ] 2. Implementation wave 2: correct replay dispatch, acknowledgement, progress, and terminal-state semantics under slow consumption, cancellation, replacement, and failure. Do not run any tests in this wave.
- [ ] 3. Implementation wave 3: make decoded exports transactional and make capture/sidecar/rotation allocation collision-safe, iteration-stable, and source-ordered. Do not run any tests in this wave.
- [ ] 4. Implementation wave 4: extend the canonical frame model and every dependent layer with direction, declared DLC, safe remote/invalid-payload decoding, and distinct standard/extended identifier keys. Do not run any tests in this wave.
- [ ] 5. Implementation wave 5: introduce provenance-qualified signal identity with legacy-profile handling across explorer, decode, series, graphs, measurements, and export. Do not run any tests in this wave.
- [ ] 6. Implementation wave 6: add concurrent profile-write coordination and record-aware trace context actions, then perform a code-only integration review of all changed interfaces. Do not run tests, lint, benchmarks, or test collection yet.
- [ ] 7. Final verification phase only, after all implementation waves are complete: create or update focused regression tests for every acceptance criterion and reproduced failure. Test files may be prepared now; no test command was allowed earlier.
- [ ] 8. Still within the final verification phase: run the focused integrity suites, then the full Linux/offscreen test suite, lint, internationalization validation, and Logics validation. Fix any failures within this final phase and rerun affected checks plus the final full gate; record exact results and platform limitations before closeout.
- [ ] 9. Complete AC traceability and closeout only after the deferred final verification gate passes. Keep commits under operator control and leave unrelated external artifacts untouched.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_098_drain_live_acquisition_completely_through_a_bounded_authoritative_handoff`
- `item_099_make_replay_completion_truthful_under_backpressure_and_cancellation`
- `item_100_publish_exports_and_recording_artifacts_transactionally_without_collision`
- `item_101_preserve_complete_can_frame_identity_and_make_decoding_total`
- `item_102_qualify_decoded_signal_identity_across_databases_and_identifiers`
- `item_103_prevent_stale_concurrent_profile_writers_from_erasing_setup_changes`
- `item_104_make_trace_context_actions_safe_for_frame_and_event_records`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_098_drain_live_acquisition_completely_through_a_bounded_authoritative_handoff`. Proof deferred to slice closeout.
- request-AC2 -> `item_098_drain_live_acquisition_completely_through_a_bounded_authoritative_handoff`. Proof deferred to slice closeout.
- request-AC13 -> `item_098_drain_live_acquisition_completely_through_a_bounded_authoritative_handoff`. Proof deferred to slice closeout.
- request-AC3 -> `item_099_make_replay_completion_truthful_under_backpressure_and_cancellation`. Proof deferred to slice closeout.
- request-AC13 -> `item_099_make_replay_completion_truthful_under_backpressure_and_cancellation`. Proof deferred to slice closeout.
- request-AC4 -> `item_100_publish_exports_and_recording_artifacts_transactionally_without_collision`. Proof deferred to slice closeout.
- request-AC5 -> `item_100_publish_exports_and_recording_artifacts_transactionally_without_collision`. Proof deferred to slice closeout.
- request-AC6 -> `item_100_publish_exports_and_recording_artifacts_transactionally_without_collision`. Proof deferred to slice closeout.
- request-AC13 -> `item_100_publish_exports_and_recording_artifacts_transactionally_without_collision`. Proof deferred to slice closeout.
- request-AC7 -> `item_101_preserve_complete_can_frame_identity_and_make_decoding_total`. Proof deferred to slice closeout.
- request-AC8 -> `item_101_preserve_complete_can_frame_identity_and_make_decoding_total`. Proof deferred to slice closeout.
- request-AC9 -> `item_101_preserve_complete_can_frame_identity_and_make_decoding_total`. Proof deferred to slice closeout.
- request-AC13 -> `item_101_preserve_complete_can_frame_identity_and_make_decoding_total`. Proof deferred to slice closeout.
- request-AC10 -> `item_102_qualify_decoded_signal_identity_across_databases_and_identifiers`. Proof deferred to slice closeout.
- request-AC13 -> `item_102_qualify_decoded_signal_identity_across_databases_and_identifiers`. Proof deferred to slice closeout.
- request-AC11 -> `item_103_prevent_stale_concurrent_profile_writers_from_erasing_setup_changes`. Proof deferred to slice closeout.
- request-AC13 -> `item_103_prevent_stale_concurrent_profile_writers_from_erasing_setup_changes`. Proof deferred to slice closeout.
- request-AC12 -> `item_104_make_trace_context_actions_safe_for_frame_and_event_records`. Proof deferred to slice closeout.
- request-AC13 -> `item_104_make_trace_context_actions_safe_for_frame_and_event_records`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_019_eliminate_peaklive_second_pass_integrity_identity_and_recovery_gaps`
- Product brief(s): `prod_018_peaklive_trustworthy_measurement_identity_and_recoverable_local_evidence`
- Architecture decision(s): (none yet)
