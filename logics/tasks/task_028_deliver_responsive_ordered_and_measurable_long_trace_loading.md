## task_028_deliver_responsive_ordered_and_measurable_long_trace_loading - Deliver responsive ordered and measurable long trace loading
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 28%
> Complexity: High
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: maintainer@example.invalid
> Indicators reviewed: 2026-09-13 23:46:55

# AI Context
- Summary: Sequence measurement, ordered transport, storage failure containment, writer optimization and long-capture qualification.
- Keywords: deliver, responsive, ordered, measurable, long, trace, loading
- Use when: Implementing the approved preparation contract with the active historical task's revision and cancellation interfaces.
- Skip when: Claiming completion from green scaffolding or silently closing existing platform and rare-event gaps.

# Context
- The audit and synthetic fault probe reproduce missing history attribution, event order/capacity bypass and an unchecked SQLite failure. The user accepts long preparation for equally dense captures up to fifty minutes.
- Synthetic implementation is ready. Windows reference-machine access and temporary-disk policy gate final qualification/default selection, not the start of transport and failure-boundary work. Coordinate existing historical reconstruction before changing shared writer ownership.

# Plan
- [ ] 1. Read the incremental audit and active historical backlog first. Confirm ownership boundaries and record the operator's fifty-minute workload; preserve unrelated external deletions.
- [ ] 2. High-priority evidence checkpoint: implement the complete lifecycle harness and fail-closed verdicts first because every optimization and terminal-state claim depends on them. Capture a reference baseline and the exact matrix actually executed.
- [ ] 3. High-priority integrity checkpoint: unify ordered frame/event transport, then implement explicit failure and acknowledgement ownership. Add focused regressions for the audit's deterministic counterexamples.
- [ ] 4. High-priority performance checkpoint: move/batch historical writes behind bounded single-writer ownership, enforce resource admission and integrate the active historical reconstruction/session revision contract. Preserve live capture and rare-event fidelity.
- [ ] 5. Coordinate navigation/cancellation/coverage prerequisites with the existing active historical task; do not implement duplicate backlog slices or silently waive its outstanding guarantees.
- [ ] 6. Medium-priority qualification checkpoint: run representative typical/fifty-minute synthetic cases and the native Windows reference matrix. Long total loading is acceptable; responsive, cancellable, correctly labelled preparation and exact evidence remain required.
- [ ] 7. Run focused regressions, full platform suites and required lint/i18n/Logics validation in proportion to the changes. Update affected docs and commit each meaningful implementation wave following ADR 009.
- [ ] 8. Before finish, attach distinct behavioral evidence for all request ACs, explicitly resolve or retain platform/resource-policy blockers, and use lifecycle closeout commands. This corpus creation itself does not start implementation.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Commit each meaningful implementation wave with its evidence and affected workflow docs; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_130_measure_and_gate_the_complete_trace_preparation_lifecycle`
- `item_131_deliver_ordered_bounded_replay_batches_for_frames_and_bus_events`
- `item_132_contain_historical_persistence_failures_and_settle_ingestion_ownership`
- `item_133_move_and_batch_historical_trace_ingestion_behind_bounded_writer_ownership`
- `item_134_qualify_typical_and_fifty_minute_trace_loading_with_existing_historical_work`

# Definition of Done (DoD)
- [ ] Runtime implementation satisfies every request criterion with distinct behavioral evidence.
- [ ] Queue, writer, revision and resource invariants pass fault and source-oracle tests without weakening historical fidelity.
- [ ] Typical and fifty-minute workloads have current native Windows evidence; unqualified scenarios prevent full closeout.
- [ ] Focused and full tests, Ruff and applicable i18n checks pass; Logics lint/audit/flow validation and refreshed context pack are complete.
- [ ] Existing historical/workspace acceptance remains assigned to its original owner; meaningful waves were committed with evidence under ADR 009.

# AC Traceability
- request-AC1 -> `item_130_measure_and_gate_the_complete_trace_preparation_lifecycle`. Proof deferred to slice closeout.
- request-AC7 -> `item_130_measure_and_gate_the_complete_trace_preparation_lifecycle`. Proof deferred to slice closeout.
- request-AC2 -> `item_131_deliver_ordered_bounded_replay_batches_for_frames_and_bus_events`. Proof deferred to slice closeout.
- request-AC6 -> `item_131_deliver_ordered_bounded_replay_batches_for_frames_and_bus_events`. Proof deferred to slice closeout.
- request-AC3 -> `item_132_contain_historical_persistence_failures_and_settle_ingestion_ownership`. Proof deferred to slice closeout.
- request-AC5 -> `item_132_contain_historical_persistence_failures_and_settle_ingestion_ownership`. Proof deferred to slice closeout.
- request-AC6 -> `item_132_contain_historical_persistence_failures_and_settle_ingestion_ownership`. Proof deferred to slice closeout.
- request-AC4 -> `item_133_move_and_batch_historical_trace_ingestion_behind_bounded_writer_ownership`. Proof deferred to slice closeout.
- request-AC5 -> `item_133_move_and_batch_historical_trace_ingestion_behind_bounded_writer_ownership`. Proof deferred to slice closeout.
- request-AC6 -> `item_133_move_and_batch_historical_trace_ingestion_behind_bounded_writer_ownership`. Proof deferred to slice closeout.
- request-AC1 -> `item_134_qualify_typical_and_fifty_minute_trace_loading_with_existing_historical_work`. Proof deferred to slice closeout.
- request-AC2 -> `item_134_qualify_typical_and_fifty_minute_trace_loading_with_existing_historical_work`. Proof deferred to slice closeout.
- request-AC3 -> `item_134_qualify_typical_and_fifty_minute_trace_loading_with_existing_historical_work`. Proof deferred to slice closeout.
- request-AC4 -> `item_134_qualify_typical_and_fifty_minute_trace_loading_with_existing_historical_work`. Proof deferred to slice closeout.
- request-AC5 -> `item_134_qualify_typical_and_fifty_minute_trace_loading_with_existing_historical_work`. Proof deferred to slice closeout.
- request-AC6 -> `item_134_qualify_typical_and_fifty_minute_trace_loading_with_existing_historical_work`. Proof deferred to slice closeout.
- request-AC7 -> `item_134_qualify_typical_and_fifty_minute_trace_loading_with_existing_historical_work`. Proof deferred to slice closeout.

# Validation
- Corpus preparation baseline: 626 Linux/offscreen tests passed in 197.18s; initial and shown-window probes reproduce the history bottleneck. Ordered event and SQLite error probes reproduce the reported gaps.
- Wave 1 (item_131, 2026-09-14): see `item_131`'s own Validation entry. `tests/test_replay_ordered_transport.py` added (3 new tests).
- Wave 2 (item_132, 2026-09-14): see `item_132`'s own Validation entry. `tests/test_history_write_failures.py` added (6 new tests). Full suite after wave 2: `uv run pytest -ra` -> 637 passed; Ruff clean across `src/peaklive` and `tests`.

# Report
- Wave 1 landed item_131 (ordered bounded replay transport unifying frames and valid bus events). Wave 2 landed item_132 (historical-persistence failure containment: read-only/locked/disk-full SQLite failures now produce one explicit terminal state instead of an uncaught exception escaping a Qt slot, with no-retry-after-failure and guaranteed-successful-reopen guarantees). Implementation order was adjusted from the plan's literal step numbering: the ordering and failure-containment fixes were implemented before the item_130 measurement harness, since both are self-contained, independently testable correctness fixes, and the harness (still pending) will measure the post-fix pipeline rather than needing to precede every other change. Wave 2 also extracted `ingest_controller.py`'s signal-backfill section into a new `signal_backfill_controller.py` mixin to stay under the repo's 400-line-per-UI-module budget with room for item_133's writer work. Remaining: item_130 (harness), item_133 (bounded writer), item_134 (qualification, native Windows evidence out of reach from this session).

# Links
- Request: `req_029_make_long_trace_loading_responsive_ordered_and_failure_explicit`
- Product brief(s): `prod_027_peaklive_responsive_and_trustworthy_long_trace_preparation`
- Architecture decision(s): (none yet)
