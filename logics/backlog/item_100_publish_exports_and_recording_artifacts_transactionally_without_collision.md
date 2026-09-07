## item_100_publish_exports_and_recording_artifacts_transactionally_without_collision - Publish exports and recording artifacts transactionally without collision
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 75%
> Complexity: High
> Theme: Transactional local output and ordered capture evidence
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-07 12:36:49

# AI Context
- Summary: Protect existing evidence with owned export temporaries, atomic publication, a complete capture/sidecar collision domain, stable acquisition iterations, and source-ordered recording.
- Keywords: atomic-export, owned-temporary, capture-collision, event-sidecar, rotation, iteration, source-order
- Use when: Changing export cancellation or publication, capture filename allocation, rotation, event sidecars, acquisition iteration, or recorder ordering.
- Skip when: Adding output formats, retention policy, decoded-value semantics, or remote destinations without changing local transactional behavior.

# Problem
- Decoded export writes directly to its final destination and cancellation cleanup unlinks that destination, including a file that existed before the export began.
- Recording reservation ignores event-sidecar artifacts, while finalization replaces them and rotated segments are allocated without the first segment's complete atomic collision contract.
- The recorder observes the next-acquisition iteration after session start, and the worker can write a later bus event before earlier batched frames.

# Scope
- In:
  - Write each decoded export to a unique owned temporary and atomically publish it only after successful completion.
  - Preserve any prior destination on cancellation or failure and clean only artifacts owned by the current operation.
  - Treat every capture and event-sidecar final, partial, and reservation marker as one atomic bounded allocation domain for first and rotated segments.
  - Snapshot the acquisition's reserved iteration for every segment while persisting the next iteration solely for the next acquisition.
  - Flush earlier frames before recording later adapter events or reconnect transitions so durable line order matches source order.
  - Prepare collision, cancellation, rotation, concurrency, and mixed frame/event regression coverage without executing it before the final gate.
- Out:
  - Adding new output formats, network destinations, retention policies, or recovery of already overwritten historical files.
  - Changing decoded export values or user-selected ranges.
  - Running output tests after individual storage changes.

# Acceptance criteria
- AC1: Successful export atomically replaces the selected destination; cancelled or failed export leaves a prior destination byte-for-byte unchanged and removes only its own temporary.
- AC2: Capture allocation skips every conflicting capture or sidecar artifact and remains bounded and atomic for concurrent first and rotated segment creation.
- AC3: All segments from one acquisition carry the same reserved iteration and monotonically increasing segment value; the next acquisition begins from the persisted next iteration.
- AC4: Mixed frame/event and reconnect fixtures retain adapter delivery order in capture evidence.
- AC5: The complete output regression matrix is executed only in the final verification phase.

# AC Traceability
- request-AC4 -> This backlog slice. Proof: AC1: Successful export atomically replaces the selected destination; cancelled or failed export leaves a prior destination byte-for-byte unchanged and removes only its own temporary.
- request-AC5 -> This backlog slice. Proof: AC2: Capture allocation skips every conflicting capture or sidecar artifact and remains bounded and atomic for concurrent first and rotated segment creation.
- request-AC6 -> This backlog slice. Proof: AC3: All segments from one acquisition carry the same reserved iteration and monotonically increasing segment value; the next acquisition begins from the persisted next iteration.
- request-AC13 -> This backlog slice. Proof: AC5: The complete output regression matrix is executed only in the final verification phase.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_018_peaklive_trustworthy_measurement_identity_and_recoverable_local_evidence`
- Architecture decision(s): (none yet)
- Request: `req_019_eliminate_peaklive_second_pass_integrity_identity_and_recovery_gaps`
- Primary task(s): `task_019_implement_every_second_pass_peaklive_integrity_and_recovery_correction`

# Priority
- Priority: High - cancellation and sidecar collision can currently delete or replace pre-existing operator evidence.
- Rationale: Set by scaffold input or defaulted for grooming.
