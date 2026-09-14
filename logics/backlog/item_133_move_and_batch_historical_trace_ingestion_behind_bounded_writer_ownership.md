## item_133_move_and_batch_historical_trace_ingestion_behind_bounded_writer_ownership - Move and batch historical trace ingestion behind bounded writer ownership
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 60%
> Complexity: High
> Theme: Historical loading performance
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-14 09:40:14

# AI Context
- Summary: Remove seven-level summary and SQLite commit work from Qt ingestion without reducing historical fidelity.
- Keywords: move, batch, historical, trace, ingestion, behind, bounded, writer, ownership
- Use when: Implementing measured transaction batching and shared writer/resource ownership.
- Skip when: Rewriting the viewport scheduler or changing database technology without evidence.

# Problem
- The GUI constructs and commits historical samples, seven summary levels and run events every 256 frames.
- The measured sixteen-signal history reaches about 39 times the synthetic source bytes; no explicit disk admission policy exists.

# Scope
- In:
  - Priority rationale: history construction is the measured dominant selected-signal loading cost and blocks the interaction path.
  - Declare a single SQLite writer owner with bounded record/sample/byte queues, explicit backpressure and transactional revision publication; move SQL and CPU-heavy history preparation off the GUI path.
  - Measure grouped summary construction, numeric extrema handling and transaction sizing before choosing optimizations; retain complete original sample/summary/anchor semantics.
  - Use separate first-data and ready milestones so staged preparation remains truthful; cancellation must be checked within bounded work chunks.
  - Integrate the existing late-selection writer and session/reset lifecycle through one agreed ownership contract; stale generations cannot write to or clean a new session.
  - Add configurable temporary-disk limit and free-space margin with explicit resource exhaustion; select documented defaults after workload estimation rather than allocating proportional memory.
  - Protect live acquisition/recording from new SQLite waits because ingestion helpers are shared; test it against a saturated synthetic adapter.
- Out:
  - Replacing SQLite, weakening durability to claim speed, reducing raw history or suppressing rare events.
  - Implementing the existing navigation scheduler, cache byte-budget or clustered-event UI in this slice.

# Acceptance criteria
- AC1: Instrumented GUI ingestion performs no historical SQL or full-history summary construction; writer concurrency, queue count/bytes and chunk sizes have deterministic asserted limits.
- AC2: Selected-signal sample counts, exact values/timestamps and summary/event fidelity match a source oracle across batch sizes, including one-frame final batches.
- AC3: Resource-limit, reset, cancellation, late selection and shutdown tests prove writer cleanup and revision isolation without stale mutation.
- AC4: Reference-machine loading stays within the retained 250ms interaction objective and reports first-data/ready time, with a measured reduction of the identified GUI history work.
- AC5: Live recording and bounded replay continue to preserve authoritative counts without new GUI-thread disk waits.

# AC Traceability
- request-AC4 -> This backlog slice. Proof (partial - byte-budget bound not yet implemented, see Report): `tests/test_history_writer.py::test_the_queue_bounds_pending_batches_and_submit_blocks_until_drained`.
- request-AC5 -> This backlog slice. Proof: `tests/test_history_writer.py::test_submitted_samples_are_persisted_with_exact_values_and_settled_is_reported`, `tests/test_graph_navigation.py::test_the_full_extent_waits_for_the_background_writer_to_settle`.
- request-AC6 -> This backlog slice. Proof (partial - late-selection coordination not yet done, see Report): `tests/test_history_writer.py::test_a_write_below_the_free_disk_margin_is_refused_before_it_starts`, `tests/test_history_write_failures.py` (reset/reopen case), `src/peaklive/ui/window_shutdown.py` (bounded settle on close).

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
- Rationale: Historical preparation is the measured dominant selected-signal loading cost.

# Validation
- Wave 3 (2026-09-14): new `services/history_writer.py::HistoryWriter` (`QThread`) is the single owner of all SQL for the primary GUI-ingest path (replay and live acquisition, which share `_ingest_frames`). `_ingest_frames` no longer calls `HistoricalSignalStore.append_many` directly; it calls `HistoryWriter.submit(historical)`, which blocks the caller only long enough to apply the same bounded backpressure contract `ReplayWorker._dispatch` already uses (`MAX_QUEUE_BATCHES=8`, polled with a 5s continuous-stall bound before failing closed - reusing item_132's `_fail_history` containment for both a stalled queue and an on-thread SQLite exception). A disk-admission check (`MIN_FREE_DISK_BYTES=64MiB`) runs before each write and raises the same way a SQLite error would. The writer's own connection uses a 1s lock-retry timeout (`WRITE_LOCK_TIMEOUT_S`, vs. sqlite3's silent 5s default) so a lock conflict surfaces as an explicit, prompt failure instead of an unexplained multi-second stall - this closes a latent gap that predates this item (every existing `HistoricalSignalStore` connection, including the GUI thread's own, inherited sqlite3's 5s default; the writer's connection now overrides it explicitly).
- `_complete_replay` now separates "parsing/decoding is done" (the existing "Trace replay complete" status, unchanged) from "history is actually persisted": `_finish_historical_readiness` polls (20ms, 30s bound) until every submitted batch has settled before marking the historical view ready and showing the full extent, so a slow writer can no longer let the graph display a partial extent as the whole capture (regression: `tests/test_graph_navigation.py::test_the_full_extent_waits_for_the_background_writer_to_settle`, using a monkeypatched slow `append_many`).
- `_reset_history_store` always allocates a brand-new `HistoricalSignalStore` (a fresh temp file) rather than reusing the previous one via `clear()`: the outgoing writer's already-queued batches (if any) keep draining to their own now-orphaned file independently, eliminating any race between a `clear()` on the GUI thread's connection and a concurrent write on the writer's separate connection to the same file. `window_shutdown.py`'s `closeEvent` now also stops/settles the writer (bounded, same pattern as every other worker) before closing `self._history`.
- Local proof: `tests/test_history_writer.py` (new, 5 direct unit tests: exact-fidelity persistence, bounded-queue backpressure across `5x MAX_QUEUE_BATCHES` submissions, fail-closed once stopped, disk-admission refusal via a monkeypatched `shutil.disk_usage`); `tests/test_history_write_failures.py` (rewritten for the async writer: `on_ready` hook lets a test set `PRAGMA query_only=ON` on the writer's own connection from its own thread - sqlite3 forbids cross-thread connection use - covering read-only, a genuinely `BEGIN EXCLUSIVE`-locked database, and a simulated disk-full commit, all 6 cases green); full suite `uv run pytest -ra` -> 643 passed; Ruff clean; all UI modules stay within the 400-line budget.

Two follow-up fixes were needed after the first pass, both against real regressions the drain-deferral exposed rather than test artifacts: (1) `_pump_signal_backfill` (task_026's late-selection reconstruction) was still gating full-source reconstruction eligibility on `_historical_view_ready`, which now lags "replay finished" - selecting a signal in that narrow window silently downgraded to the bounded in-memory reconstruction instead of waiting or using the full source. Fixed by keying eligibility on `_replay_worker is None` (the source is fully read) instead, since `SourceSignalDecodeWorker` reads the source file directly and never needed full history-settlement to begin with; regression: `tests/test_lazy_signals.py::test_a_late_selection_after_replay_is_reconstructed_from_the_full_source`. (2) `_refresh_report()` was moved into the deferred `_finish_historical_readiness` alongside the two things that actually need the writer to drain (`_set_historical_view_ready`, `show_full_extent`), even though the report reads only in-memory `SessionFacts`, not SQL - this made `report_panel.text` briefly stale/empty right after a replay "completed". Moved back to run synchronously in `_complete_replay`, matching pre-item_133 timing exactly; regression: `tests/test_lazy_signals.py::test_deselecting_a_signal_drops_it_without_disturbing_the_session`.

# Report
- Not yet done in this wave, explicitly deferred rather than silently claimed: (1) AC1's "queue count/bytes" - only a batch-count bound (`MAX_QUEUE_BATCHES`) exists; there is no byte-budget bound on queued-but-unsettled samples. (2) AC3's "late selection" - `SourceSignalDecodeWorker` (task_026's late-selection reconstruction worker) still writes directly to `HistoricalSignalStore` on its own thread, uncoordinated with `HistoryWriter`; the two writers are not yet arbitrated through one shared ownership contract, per task_028's own plan step 5 ("do not implement duplicate backlog slices or silently waive its outstanding guarantees" of the active historical task). This is a known, flagged coordination gap, not an oversight. (3) AC4's reference-machine 250ms/first-data-and-ready-time measurement depends on the item_130 harness, not yet built in this task; no performance claim is made here beyond "SQL no longer runs on the GUI thread," which is structurally true by construction (grep confirms `append_many` is called only from `HistoryWriter.run`) but not yet independently measured. (4) No source-oracle byte-for-byte comparison test exists yet for a full end-to-end replay through the new writer at meaningful density; `test_the_full_extent_waits_for_the_background_writer_to_settle` and the pre-existing `test_a_completed_replay_opens_on_the_whole_capture`/`test_a_slow_but_progressing_ui_completes_replay_with_historical_signals` cover count/bounds fidelity at small scale only.
