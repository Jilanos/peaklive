## item_133_move_and_batch_historical_trace_ingestion_behind_bounded_writer_ownership - Move and batch historical trace ingestion behind bounded writer ownership
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Historical loading performance
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-13 23:32:48

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
- request-AC4 -> This backlog slice. Proof: AC1: Instrumented GUI ingestion performs no historical SQL or full-history summary construction; writer concurrency, queue count/bytes and chunk sizes have deterministic asserted limits.
- request-AC5 -> This backlog slice. Proof: AC2: Selected-signal sample counts, exact values/timestamps and summary/event fidelity match a source oracle across batch sizes, including one-frame final batches.
- request-AC6 -> This backlog slice. Proof: AC3: Resource-limit, reset, cancellation, late selection and shutdown tests prove writer cleanup and revision isolation without stale mutation.

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
