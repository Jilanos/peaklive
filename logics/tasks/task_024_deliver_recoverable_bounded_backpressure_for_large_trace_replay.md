## task_024_deliver_recoverable_bounded_backpressure_for_large_trace_replay - Deliver recoverable bounded backpressure for large trace replay
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 90%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-10 17:06:41
> Owner: Codex

# AI Context
- Summary: Implement and validate recoverable bounded replay handoff for large traces.
- Keywords: deliver, recoverable, bounded, backpressure, large, trace, replay
- Use when: Developing the replay backpressure correction described by request 024 and backlog item 116.
- Skip when: Investigating live adapter transport, parser format support, or unrelated UI performance work.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Reproduce the 36.7-second failure with a deterministic large capture and a controlled slow presentation path; record queue depth, acknowledgement latency, parsed frame count, and the lifecycle message.
- [ ] 2. Map the replay state machine and choose a bounded handoff policy that tolerates legitimate progress while retaining an explicit cancellation and shutdown escape hatch.
- [ ] 3. Implement exact permit ownership and generation-safe acknowledgement handling, then keep parsing, decoding, historical persistence, and presentation projections lossless.
- [ ] 4. Make progress and completion ordering truthful and preserve distinct diagnostics for parser failure, cancellation, and exhausted backpressure.
- [ ] 5. Add focused regression coverage for slow presentation, selected-signal historical writes, cancellation, stale generations, frame-count integrity, and the no-ack safety case.
- [ ] 6. Run Ruff, the full headless test suite, the trace performance checks, and the Windows packaging validation; record evidence and close the task only after all acceptance criteria pass.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_116_make_bounded_replay_backpressure_recoverable_and_truthful`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_116_make_bounded_replay_backpressure_recoverable_and_truthful`. Proof deferred to slice closeout.
- request-AC2 -> `item_116_make_bounded_replay_backpressure_recoverable_and_truthful`. Proof deferred to slice closeout.
- request-AC3 -> `item_116_make_bounded_replay_backpressure_recoverable_and_truthful`. Proof deferred to slice closeout.
- request-AC4 -> `item_116_make_bounded_replay_backpressure_recoverable_and_truthful`. Proof deferred to slice closeout.
- request-AC5 -> `item_116_make_bounded_replay_backpressure_recoverable_and_truthful`. Proof deferred to slice closeout.
- request-AC6 -> `item_116_make_bounded_replay_backpressure_recoverable_and_truthful`. Proof deferred to slice closeout.
- request-AC7 -> `item_116_make_bounded_replay_backpressure_recoverable_and_truthful`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_024_prevent_long_trace_replay_from_aborting_on_false_backpressure_timeouts`
- Product brief(s): `prod_023_reliable_large_trace_replay_and_presentation_backpressure`
- Architecture decision(s): (none yet)
