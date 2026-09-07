## item_098_drain_live_acquisition_completely_through_a_bounded_authoritative_handoff - Drain live acquisition completely through a bounded authoritative handoff
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 75%
> Complexity: High
> Theme: Lossless live ingestion and bounded responsiveness
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-07 12:36:49

# AI Context
- Summary: Correct live Stop and overload handling so every worker-accepted frame reaches authoritative session state exactly once through a bounded handoff before its generation retires.
- Keywords: live-ingestion, stop-drain, final-batch, bounded-handoff, generation-safety, exactly-once
- Use when: Changing acquisition worker delivery, UI ingestion scheduling, Stop sequencing, final-batch handling, or live overload behavior.
- Skip when: Working on replay-only flow control, historical retention capacity, output formats, or DBC identity without changing live delivery.

# Problem
- Stop invalidates and clears the presentation generation before requesting worker shutdown, so queued frames and the final partial worker batch cannot reach authoritative session state.
- The live handoff extends an unbounded list and drains all accumulated frames in one UI turn; downstream bounded stores do not constrain this upstream growth.
- The capture can therefore contain frames omitted from facts, cache, trace, and plots, and overload can progress toward memory exhaustion or a frozen event loop.

# Scope
- In:
  - Separate acceptance of authoritative live facts from bounded presentation work while preserving exactly-once generation semantics.
  - Define a bounded producer-consumer handoff or equivalent flow control whose overload outcome is explicit and does not silently falsify the session.
  - Change normal Stop and worker completion ordering so the active generation drains accepted frames, settles presentation, and only then retires.
  - Preserve bounded timeout recovery and stale-generation rejection without allowing an abandoned worker to contaminate a later session.
  - Prepare focused regression coverage but defer all test execution to the orchestration task's final verification phase.
- Out:
  - Increasing every retention capacity or retaining an unlimited historical session in memory.
  - Changing raw capture formats, DBC decode semantics, or graph appearance.
  - Executing tests before all implementation slices are complete.

# Acceptance criteria
- AC1: Normal Stop retains every accepted frame exactly once across facts, cache, trace, and selected series, including queued and final partial batches.
- AC2: Sustained producer overload cannot grow memory or one UI event-loop turn beyond documented deterministic bounds, and any inability to preserve authoritative facts is surfaced as an integrity failure.
- AC3: Timeout recovery and a subsequent generation cannot accept stale frames from the abandoned worker.
- AC4: Regression tests for stop-time drain, final-batch delivery, overload bounds, and stale generations are executed only in the final verification phase.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Normal Stop retains every accepted frame exactly once across facts, cache, trace, and selected series, including queued and final partial batches.
- request-AC2 -> This backlog slice. Proof: AC2: Sustained producer overload cannot grow memory or one UI event-loop turn beyond documented deterministic bounds, and any inability to preserve authoritative facts is surfaced as an integrity failure.
- request-AC13 -> This backlog slice. Proof: AC4: Regression tests for stop-time drain, final-batch delivery, overload bounds, and stale generations are executed only in the final verification phase.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_018_peaklive_trustworthy_measurement_identity_and_recoverable_local_evidence`
- Architecture decision(s): (none yet)
- Request: `req_019_eliminate_peaklive_second_pass_integrity_identity_and_recovery_gaps`
- Primary task(s): `task_019_implement_every_second_pass_peaklive_integrity_and_recovery_correction`

# Priority
- Priority: High - current Stop behavior deterministically discards accepted frames, while sustained overload can grow the upstream queue and one UI turn without a bound.
- Rationale: Set by scaffold input or defaulted for grooming.
