## req_029_make_long_trace_loading_responsive_ordered_and_failure_explicit - Make long trace loading responsive ordered and failure explicit
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Measured long trace loading and historical ingestion
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.

# AI Context
- Summary: Load the operator's 1.756M-frame typical and 5.575M-frame long workloads with ordered evidence and bounded historical preparation.
- Keywords: long, trace, loading, responsive, ordered, failure, explicit
- Use when: Scoping the four reproduced loading gaps and their integrated Windows qualification.
- Skip when: Reopening the earlier review or duplicating historical navigation and workspace layout tasks.

# Needs
- Load typical and fifty-minute captures without freezing the workspace, losing record order, disguising failed preparation or sacrificing complete historical evidence.
- Expose reliable progress and cancellation throughout parsing, historical preparation and display finalization, accepting longer total loading for longer captures.
- Attribute the complete loading cost and remove synchronous historical persistence from GUI ingestion.
- Coordinate existing historical reconstruction and viewport work through explicit writer ownership and revision contracts.

# Context
- Corrective scope authorized after the incremental review; audit evidence is captured separately in the referenced review request and report. This corpus prepares implementation and does not implement runtime changes.
- Reviewed application baseline cc75668 follows independent review a4a4bbf by 93 commits. Synthetic 200k-frame loading with sixteen signals spends 12.565s in synchronous history writes, omitted by the current stage profiler; initial diagnostic load time is 21.981s and slowest event pass 487ms.
- Reproductions prove source event/frame reordering, 10000 unacknowledged valid events escaping the queue bound, and SQLite write exceptions escaping a partially mutated GUI ingestion batch.
- Operator-provided local capture census: 195753923 bytes, 1755746 frames over 944.788905 seconds, 40 distinct frame identities and mean 1858.347 frames/s. Events: 991 bus statuses, 23 error frames and one parser anomaly. Only aggregate statistics are versioned; no private path, identifier values, DBC or payload data.
- Operator accepts longer preparation for captures up to fifty minutes at comparable density. This implies approximately 5575042 frames and 621579875 source bytes, not a promise of linear runtime or storage. Existing synthetic 1kHz fixtures remain useful microbenchmarks but do not represent this full workload.
- Default selected-signal matrix is 1/8/16 until the operator refines it. Keep the existing 250ms interaction target; do not invent a hard total-load SLA. Report elapsed time, throughput and clearly distinguished first-data versus fully-ready milestones.
- Existing historical scheduling and late reconstruction scope is owned by the referenced active historical backlog/task. It includes cancellation inside SQL, coverage publication, source/DBC/session identity and bounded caches. Coordinate these interfaces instead of creating a duplicate navigation implementation.
- Native Windows hardware/storage, total-load expectations and temporary-disk policy remain open qualification choices. They do not block synthetic implementation. Use explicit incomplete/error states and preserve the original source as the conservative recovery contract.
- Baseline Linux/offscreen full suite passes 626 tests; existing green tests do not cover the demonstrated failures. Windows layout quarantine remains owned by the existing workspace task.

# Acceptance criteria
- AC1: A reproducible harness covers ASC/TRC and 0/1/8/16 selected signals, measures history append/summary/commit, queue wait, GUI projection, first useful data and fully-ready milestones, verifies exact accepted source counts and terminal success, and exits nonzero on timeout, partial load, failure or selected budget overrun.
- AC2: Frames and valid bus events retain source order and exact authoritative counts through one bounded acknowledged replay transport. Event-only captures, bursts of at least 10000 events, mixed record boundaries, EOF, cancellation and replacement cannot bypass bounds or complete before all accepted records settle.
- AC3: Read-only, locked, full and failed history persistence plus worker exceptions cause one explicit failed/incomplete terminal state. No GUI slot exception escapes, source files remain intact, owned queue permits are retired exactly once, retries cannot double-count records and reopening a valid capture succeeds.
- AC4: Raw historical samples, seven-level or equivalently faithful summaries and rare-event anchors are prepared off the GUI thread under a documented single-writer bounded-queue contract. On the declared reference workload the existing 250ms responsiveness objective holds during ingest/finalization/cancel; no higher timeouts, missing history, unbounded queues or disabled integrity checks substitute for that objective.
- AC5: Historical preparation has explicit temporary-disk accounting, admission/low-space policy, bounded batches and cleanup ownership. Reset, deselection, source or DBC changes, late reconstruction, cancellation and shutdown cannot mix revisions or delete another session's data. Configured resource-limit failures are explicit and tested.
- AC6: Current full-history values, timestamps, source order, rare-event anchors and CAN/signal identity remain correct against source-derived oracles; live recording, replay, exports, historical navigation and retained buffers pass relevant regression checks. Existing historical and workspace tasks retain their own unfinished acceptance responsibilities.
- AC7: Qualification includes measured typical-density synthetic captures around 1.756M frames and fifty-minute captures around 5.575M frames at 1858 frames/s, with 1/8/16 selected signals and event-heavy companions. Record machine, build, throughput, first-data/ready latency, memory/disk peaks and cancellation response. Long loading itself is acceptable; unresponsive or misleading loading is not. Native Windows evidence is required before claiming target-platform completion.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_027_peaklive_responsive_and_trustworthy_long_trace_preparation`
- Architecture decision(s): (none yet)

# References
- docs/audit-2026-09-13-trace-loading.md
- logics/request/req_028_incremental_review_findings_trace_loading_and_historical_storage.md
- logics/analysis/trace_load_followup_probe.py
- src/peaklive/analysis/history.py
- src/peaklive/analysis/profiling.py
- src/peaklive/analysis/replay.py
- src/peaklive/services/replay_worker.py
- src/peaklive/services/signal_decode_worker.py
- src/peaklive/ui/ingest_controller.py
- src/peaklive/ui/session_controller.py
- src/peaklive/ui/panels/graph_stack.py
- scripts/audit_trace_performance.py
- tests/test_trace_performance.py
- tests/test_replay_integrity.py
- tests/test_lazy_signals.py
- logics/tasks/task_026_restore_dense_historical_overview_coverage_and_rare_event_discoverability.md
- logics/tasks/task_027_deliver_stable_panel_restoration_and_a_space_efficient_graph_workspace.md

# Backlog
- `item_130_measure_and_gate_the_complete_trace_preparation_lifecycle`
- `item_131_deliver_ordered_bounded_replay_batches_for_frames_and_bus_events`
- `item_132_contain_historical_persistence_failures_and_settle_ingestion_ownership`
- `item_133_move_and_batch_historical_trace_ingestion_behind_bounded_writer_ownership`
- `item_134_qualify_typical_and_fifty_minute_trace_loading_with_existing_historical_work`
