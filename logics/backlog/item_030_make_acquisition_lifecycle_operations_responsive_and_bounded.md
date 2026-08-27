## item_030_make_acquisition_lifecycle_operations_responsive_and_bounded - Make acquisition lifecycle operations responsive and bounded
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 10%
> Complexity: High
> Theme: Acquisition lifecycle reliability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-27 13:45:19

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: acquisition, lifecycle, operations, responsive, bounded
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Adapter connect, receive, disconnect, and recorder finalization can be slow or block. The UI needs a lifecycle contract that remains responsive without concealing incomplete shutdown or data-loss risk.
- Current start/stop behavior has no explicit timeout escalation, generation guard, or deterministic recovery policy for a worker that does not finish.

# Scope
- In:
  - Explicit acquisition lifecycle state machine, user-visible transitional/degraded states, action gating, and idempotent repeated-action handling.
  - A cancellable/bounded worker shutdown protocol that keeps Qt UI work on the UI thread and isolates potentially blocking driver or recording operations.
  - Timeout, failure, and window-close behavior with recoverable recording markers and a documented operator outcome.
  - Fake blocking/failing adapter and recorder tests, including event-loop responsiveness assertions and Windows hardware acceptance instructions.
- Out:
  - Changing capture format semantics beyond accurately marking incomplete or unclean finalization.
  - Solving defects inside third-party CAN drivers or forcefully killing external driver resources.
  - New CAN protocol features or transmission controls.

# Acceptance criteria
- AC1: Start and Stop have explicit, observable lifecycle states and keep the window interactive under controllably delayed connect, receive, disconnect, and finalization operations.
- AC2: Each acquisition generation reaches one terminal result exactly once; stale signals, duplicate clicks, and close-window races cannot restart controls for a newer or abandoned generation.
- AC3: A bounded shutdown timeout produces an actionable state without blocking the UI indefinitely, retains diagnostic detail, and leaves artifacts correctly finalized or marked incomplete.
- AC4: Normal, connect-error, receive-error, disconnect-error, recorder-error, and timeout paths restore a deterministic usable UI state or present the documented safe exit path.
- AC5: Offscreen tests use controllably blocking fakes to prove event processing, state transitions, duplicate-action safety, and artifact outcome; a hardware runbook covers the supported Windows adapter.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Start and Stop have explicit, observable lifecycle states and keep the window interactive under controllably delayed connect, receive, disconnect, and finalization operations.
- request-AC2 -> This backlog slice. Proof: AC2: Each acquisition generation reaches one terminal result exactly once; stale signals, duplicate clicks, and close-window races cannot restart controls for a newer or abandoned generation.
- request-AC3 -> This backlog slice. Proof: AC3: A bounded shutdown timeout produces an actionable state without blocking the UI indefinitely, retains diagnostic detail, and leaves artifacts correctly finalized or marked incomplete.
- request-AC4 -> This backlog slice. Proof: AC4: Normal, connect-error, receive-error, disconnect-error, recorder-error, and timeout paths restore a deterministic usable UI state or present the documented safe exit path.
- request-AC7 -> This backlog slice. Proof: AC5: Offscreen tests use controllably blocking fakes to prove event processing, state transitions, duplicate-action safety, and artifact outcome; a hardware runbook covers the supported Windows adapter.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_006_peaklive_responsive_runtime_and_identifiable_builds`
- Architecture decision(s): (none yet)
- Request: `req_006_keep_peaklive_responsive_during_acquisition_dbc_changes_and_test_build_verification`
- Primary task(s): `task_006_deliver_responsive_peaklive_lifecycle_dbc_operations_and_build_identity`

# Priority
- Priority: High - a frozen acquisition start or stop prevents bench work and can make capture evidence difficult to recover.
- Rationale: Set by scaffold input or defaulted for grooming.
