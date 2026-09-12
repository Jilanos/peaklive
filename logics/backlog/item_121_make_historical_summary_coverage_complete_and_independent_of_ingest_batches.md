## item_121_make_historical_summary_coverage_complete_and_independent_of_ingest_batches - Make historical summary coverage complete and independent of ingest batches
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 15%
> Complexity: High
> Theme: Authoritative historical data and revision ownership
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-12 17:10:01

# AI Context
- Summary: Reject incomplete summaries and invalidate all historical derivatives on reset.
- Keywords: historical, summary, coverage, complete, independent, ingest, batches
- Use when: Repairing batch-dependent loss of full-history coverage and building committed complete levels.
- Skip when: Working on UI labels or unrelated recording formats.

# Problem
- Summary maintenance is skipped for decoded batches above 32 rows but any surviving summary is trusted as complete.
- clear() deletes raw samples only; summary and overview cache entries can leak into a later session.

# Scope
- In:
  - Reproduce bulk-plus-one/bulk-plus-sixteen and mixed multi-signal batch failures with the diagnostic and deterministic source oracles.
  - Add completeness and committed revision ownership for each signal/level; invalidate incomplete levels and use a cancellable authoritative fallback until rebuilding completes.
  - Build complete first/min/max/last/count hierarchy levels in bounded background batches; preserve raw rows and read-only worker connections. Avoid seven per-row SELECT/UPDATE loops on the GUI ingest path.
  - Handle partial edge buckets, stable duplicate-time sample identity, full endpoints and late extrema; reserve point budget before emitting rather than truncating the last buckets.
  - Reset samples, summaries, persistent caches and extent/revision metadata in one owner transaction; invalidate panel caches and in-flight requests.
  - Measure row visits, index preparation/cancellation, temporary-disk footprint and disk-full behavior; publish ready levels only after complete commits.
- Out:
  - Renderer replacement, source-sample deletion, silent partial summaries and full-file late-selection decoding.

# Acceptance criteria
- AC1: Broad historical source results remain nonempty with complete expected coverage for the reported dense scenarios.
- AC2: All declared batch partitions yield the same interval coverage and extrema; reset with reused signal/range keys never returns old values.
- AC3: Summary results preserve source identity, chronology, endpoints and budget without slicing away late data.
- AC5: Indexed reads scale with output budget in a 10x-duration experiment; construction and fallback are separately measured and cancellable.
- AC8: Store/worker regression tests and per-signal completeness evidence are attached before integration qualification.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Broad historical source results remain nonempty with complete expected coverage for the reported dense scenarios.
- request-AC2 -> This backlog slice. Proof: AC2: All declared batch partitions yield the same interval coverage and extrema; reset with reused signal/range keys never returns old values.
- request-AC3 -> This backlog slice. Proof: AC3: Summary results preserve source identity, chronology, endpoints and budget without slicing away late data.
- request-AC5 -> This backlog slice. Proof: AC5: Indexed reads scale with output budget in a 10x-duration experiment; construction and fallback are separately measured and cancellable.
- request-AC8 -> This backlog slice. Proof: AC8: Store/worker regression tests and per-signal completeness evidence are attached before integration qualification.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_025_discoverable_rare_diagnostic_events_in_dense_historical_views`
- Architecture decision(s): (none yet)
- Request: `req_026_restore_dense_historical_curves_and_preserve_rare_diagnostic_signal_events`
- Primary task(s): `task_026_restore_dense_historical_overview_coverage_and_rare_event_discoverability`

# Priority
- Priority: High - partial summaries can silently replace the full capture with one sample.
- Rationale: Set by scaffold input or defaulted for grooming.
