## item_103_prevent_stale_concurrent_profile_writers_from_erasing_setup_changes - Prevent stale concurrent profile writers from erasing setup changes
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Concurrent profile consistency
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: Add explicit local concurrency control to profile persistence so a stale application instance cannot silently replace another instance's completed setup change.
- Keywords: profile-store, concurrent-writer, stale-write, atomic-replace, revision, lock, merge
- Use when: Changing profile load/save coordination, revision checks, local locking, merge behavior, conflict feedback, or abandoned-lock recovery.
- Skip when: Changing unrelated profile fields, cloud synchronization, user accounts, or single-process UI defaults without touching store consistency.

# Problem
- Unique temporary names and fsync make an individual save durable but do not coordinate two instances that loaded different historical snapshots.
- The later whole-file replace silently erases fields or profiles saved by the first instance.
- There is no revision token or operator-visible stale-write conflict.

# Scope
- In:
  - Choose and document a local coordination contract: serialized lock, compare-and-swap revision, deterministic merge, or explicit stale-write rejection.
  - Keep atomic durable replacement and corrupt-store recovery while preventing lost updates and handling abandoned coordination artifacts safely.
  - Surface an actionable operator result if a concurrent change cannot be merged automatically.
  - Prepare two-instance, crash-recovery, and stale-write regression coverage for final execution only.
- Out:
  - Cloud synchronization, multi-user accounts, remote merge, or collaborative editing.
  - Changing unrelated profile fields or measurement defaults.
  - Running profile tests during implementation.

# Acceptance criteria
- AC1: Two instances saving independent changes cannot silently erase either completed change.
- AC2: Conflicting changes resolve deterministically or reject the stale writer with actionable feedback while retaining a readable store.
- AC3: Atomicity, durability, corrupt-store quarantine, and normal single-instance saves remain intact.
- AC4: Concurrency and recovery tests run only in the final verification phase.

# AC Traceability
- request-AC11 -> This backlog slice. Proof: AC1: Two instances saving independent changes cannot silently erase either completed change.
- request-AC13 -> This backlog slice. Proof: AC4: Concurrency and recovery tests run only in the final verification phase.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_018_peaklive_trustworthy_measurement_identity_and_recoverable_local_evidence`
- Architecture decision(s): (none yet)
- Request: `req_019_eliminate_peaklive_second_pass_integrity_identity_and_recovery_gaps`
- Primary task(s): `task_019_implement_every_second_pass_peaklive_integrity_and_recovery_correction`

# Priority
- Priority: Medium - the loss requires multiple running instances, but it silently removes completed operator configuration.
- Rationale: Set by scaffold input or defaulted for grooming.
