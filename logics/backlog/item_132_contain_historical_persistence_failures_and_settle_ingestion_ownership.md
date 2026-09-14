## item_132_contain_historical_persistence_failures_and_settle_ingestion_ownership - Contain historical persistence failures and settle ingestion ownership
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 60%
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
- request-AC3 -> This backlog slice. Proof: `tests/test_history_write_failures.py::test_a_readonly_failure_does_not_escape_the_drain_slot_and_retires_the_permit_once`.
- request-AC5 -> This backlog slice. Proof: `tests/test_history_write_failures.py::test_a_readonly_failure_is_reported_as_one_explicit_terminal_state_not_success`, `::test_a_genuinely_locked_database_is_contained_the_same_way`, `::test_a_simulated_disk_full_commit_failure_is_contained_the_same_way`, `::test_reopening_after_the_fault_clears_succeeds_from_a_fresh_store`.
- request-AC6 -> This backlog slice. Proof: `tests/test_history_write_failures.py::test_after_a_failure_further_batches_do_not_retry_persistence_or_duplicate_facts`.

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

# Validation
- Wave 2 (2026-09-14): `WorkspaceIngest._ingest_frames` now wraps `HistoricalSignalStore.append_many` in `try/except sqlite3.Error`. On failure it calls `_fail_history()` exactly once per session (sets `_history_failed`/`_history_failure_message`, marks `_historical_view_ready = False`, shows one non-modal error note via `trace.history_failed`), and further batches in the same session skip persistence entirely rather than retrying. `_ingest_replay_records` propagates the failure bit to `session_controller._drain_replay_batch`, which retires the current batch's permit (`worker.batch_rendered()`) unconditionally, then requests the worker stop, abandons it (`abandon_worker`), and routes through the existing `_replay_failed_for_generation` terminal-failure path (now idempotent: a second, cascading "Replay cancelled" from the stop request cannot overwrite the real cause). The symmetric live-acquisition path (`_render_frames` / new `_acquisition_history_failed`) gets the same shared containment, since `_ingest_frames` is explicitly the shared ingest method. `_reset_session` now calls `_reset_history_store()`, which discards a poisoned store (one that already failed, or whose `clear()` itself raises) for a brand-new `HistoricalSignalStore`, guaranteeing the next open always succeeds rather than depending on the fault having cleared. Also extracted the on-demand signal-backfill section of `ingest_controller.py` into a new `signal_backfill_controller.WorkspaceSignalBackfill` mixin (behavior-preserving) to stay under the 400-line module budget (`tests/test_ui_structure.py`) with room for this and the item_133 writer work. Local proof: `tests/test_history_write_failures.py` (new, 6 cases: read-only, genuinely locked via a second `BEGIN EXCLUSIVE` connection, simulated disk-full via monkeypatch, no-retry-after-failure, and successful reopen from a fresh store); full suite `uv run pytest -ra` -> 637 passed; Ruff clean.

# Report
- AC2's "preserve source bytes" is satisfied structurally (the fix never touches the replay source path) rather than by a dedicated byte-comparison regression; the existing ASC/TRC replay tests already cover source-path handling separately. The live-acquisition symmetric containment (`_acquisition_history_failed`) has no dedicated regression test in this wave — it reuses the same `_ingest_frames` boundary already covered for replay, and adding a live-specific fault-injection test is deferred as lower-value than the replay-path coverage the request's ACs actually cite.
