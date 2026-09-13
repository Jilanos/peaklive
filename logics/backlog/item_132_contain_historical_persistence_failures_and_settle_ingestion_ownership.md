## item_132_contain_historical_persistence_failures_and_settle_ingestion_ownership - Contain historical persistence failures and settle ingestion ownership
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Recoverable trace preparation
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-13 23:32:48

# AI Context
- Summary: Turn mid-batch SQLite exceptions into explicit incomplete outcomes with exact permit retirement.
- Keywords: contain, historical, persistence, failures, settle, ingestion, ownership
- Use when: Defining accepted versus persisted batches and recoverable terminal cleanup.
- Skip when: Silently retrying partial mutations or treating discarded historical coverage as complete.

# Problem
- A SQLite exception currently occurs after trace/facts/frame mutations and before batch acknowledgement, escaping the GUI slot.

# Scope
- In:
  - Priority rationale: explicit failure and permit ownership must exist before moving historical writes between threads.
  - Define batch accepted/projected/persisted states and terminal failure ownership shared by ordered replay and historical persistence.
  - Handle database write/commit and worker failures once, stop further source consumption, retain actionable nonmodal failure and mark analytical coverage incomplete.
  - Test read-only, busy/locked, bounded disk-full injection, append/commit exception and retry; use owned temporary paths only.
  - Preserve source captures and already-valid independent exports; ensure clearing or reopening releases resources without double-counting partial batches.
  - Coordinate failure and cleanup semantics with the active historical reconstruction backlog instead of duplicating its worker lifecycle implementation.
- Out:
  - Automatic destructive source repair or silently substituting retained-tail history.
  - A comprehensive live transport redesign.

# Acceptance criteria
- AC1: The query_only reproduction no longer escapes a Qt slot, leaks a permit, blocks the drain indefinitely or reports complete analysis.
- AC2: Locked/full/write/commit/worker failure cases emit one terminal cause, retire ownership exactly once, preserve source bytes and permit a subsequent successful open.
- AC3: A failure after partial preparation cannot be retried into duplicate session facts or reused as complete historical coverage.
- AC4: Cancellation and failure clean only artifacts owned by their session/revision and do not remove a new session's samples.

# AC Traceability
- request-AC3 -> This backlog slice. Proof: AC1: The query_only reproduction no longer escapes a Qt slot, leaks a permit, blocks the drain indefinitely or reports complete analysis.
- request-AC5 -> This backlog slice. Proof: AC2: Locked/full/write/commit/worker failure cases emit one terminal cause, retire ownership exactly once, preserve source bytes and permit a subsequent successful open.
- request-AC6 -> This backlog slice. Proof: AC3: A failure after partial preparation cannot be retried into duplicate session facts or reused as complete historical coverage.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_027_peaklive_responsive_and_trustworthy_long_trace_preparation`
- Architecture decision(s): (none yet)
- Request: `req_029_make_long_trace_loading_responsive_ordered_and_failure_explicit`
- Primary task(s): `task_028_deliver_responsive_ordered_and_measurable_long_trace_loading`

# Priority
- Priority: High
- Rationale: Failure and permit ownership must be explicit before moving writes between threads.
