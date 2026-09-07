## item_099_make_replay_completion_truthful_under_backpressure_and_cancellation - Make replay completion truthful under backpressure and cancellation
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Replay integrity and explicit terminal states
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: Make replay success contingent on acknowledged delivery of every parsed frame and expose cancellation, replacement, parser failure, and backpressure failure as distinct outcomes.
- Keywords: replay, backpressure, acknowledgement, terminal-state, progress, cancellation, truncation
- Use when: Changing replay worker permits, batch dispatch, progress reporting, completion signaling, cancellation, or generation replacement.
- Skip when: Changing live acquisition flow control, supported replay syntax, or eager file loading without touching replay completion truthfulness.

# Problem
- A presentation-permit timeout is currently interpreted as an instruction to stop parsing rather than as bounded waiting, cancellation, or failure.
- The final batch dispatch result is ignored and the worker unconditionally emits total progress and marks success.
- The UI completion path announces success without proving complete acknowledged delivery.

# Scope
- In:
  - Define explicit terminal results for completed, cancelled, replaced, backpressure-failed, and parser-failed replay.
  - Require successful dispatch and acknowledgement of every batch before success and total progress can be emitted.
  - Keep cancellation and stale-generation replacement bounded without leaking permits or retaining obsolete batches.
  - Prepare focused slow-consumer and cancellation regression coverage for final-phase execution only.
- Out:
  - Adding binary replay formats or changing supported text grammar.
  - Replacing bounded replay with eager whole-file loading.
  - Executing replay tests during this implementation slice.

# Acceptance criteria
- AC1: A slow consumer receives every source frame exactly once or an explicit non-success terminal result; it never receives a successful truncated session.
- AC2: Success and 100 percent progress are emitted only after complete accepted delivery, while cancellation, replacement, parse failure, and backpressure failure remain distinguishable.
- AC3: Pending permits and queued batches are settled without leaks across every terminal path.
- AC4: All replay regressions are executed only after the complete repository implementation is finished.

# AC Traceability
- request-AC3 -> This backlog slice. Proof: AC1: A slow consumer receives every source frame exactly once or an explicit non-success terminal result; it never receives a successful truncated session.
- request-AC13 -> This backlog slice. Proof: AC4: All replay regressions are executed only after the complete repository implementation is finished.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_018_peaklive_trustworthy_measurement_identity_and_recoverable_local_evidence`
- Architecture decision(s): (none yet)
- Request: `req_019_eliminate_peaklive_second_pass_integrity_identity_and_recovery_gaps`
- Primary task(s): `task_019_implement_every_second_pass_peaklive_integrity_and_recovery_correction`

# Priority
- Priority: High - the current permit timeout truncates a supported trace and reports a false successful completion.
- Rationale: Set by scaffold input or defaulted for grooming.
