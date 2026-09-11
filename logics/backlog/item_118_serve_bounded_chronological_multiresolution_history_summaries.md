## item_118_serve_bounded_chronological_multiresolution_history_summaries - Serve bounded chronological multiresolution history summaries
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 40%
> Complexity: High
> Theme: SQLite resolution hierarchy and exact-query policy
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-11 16:00:33

# AI Context
- Summary: Eliminate raw-range rescans while preserving chronological extrema and late capture coverage within an explicit point budget.
- Keywords: serve, bounded, chronological, multiresolution, history, summaries
- Use when: Building indexed resolution levels, density-aware exact selection and bounded result caching.
- Skip when: Claiming that raw SQL aggregation or moving the Python scan to a thread meets the final complexity target.

# Problem
- The overview scans every raw sample for every query; its output cap does not bound CPU or database reads.
- Four-point buckets followed by a global slice lose later intervals and produce nonchronological x values.

# Scope
- In:
  - Define and implement disk-backed hierarchical first/min/max/last summaries, counts and stable sample identities with indexed signal/level/bucket keys and incrementally maintained global/per-signal bounds.
  - Build summaries in bounded background batches with progress/cancellation; preserve exact historical rows. Specify transaction ownership and committed-read semantics; introduce WAL only if concurrent write/read needs it, with size/checkpoint policy.
  - Select a level using viewport pixels and density estimates. Query a bounded set of summary buckets plus bounded edges; raw full-range rescans and raw SQL GROUP BY are not the final interactive path.
  - Budget up to four slots per bucket before emitting; deduplicate by sample identity and sort chronologically. Preserve full interval endpoints, late extrema, duplicate timestamp ordering and gaps.
  - Distinguish exact overflow, empty, missing, error and cancellation. Retain 20000 exact cap; use density/pixel policy and hysteresis rather than a fixed duration fraction.
  - Cache immutable viewport results within 64 MiB total with explicit invalidation. Record index footprint, temporary-disk quota/failure behavior and scaling.
- Out:
  - Database migration or GPU rendering as prerequisite.
  - Replacing original samples with summaries or silently reducing analytical precision.

# Acceptance criteria
- AC1: Integrated warm/cold navigation meets the documented budgets with 1/4/8 lanes.
- AC3: Instrumentation proves broad queries read bounded summary rows as fixture duration grows 10x; overview and exact point caps hold independently of raw volume.
- AC4: Oscillating 400-sample and late-spike fixtures preserve end timestamp and all required bucket extrema within the cap, ordered by timestamp/sample identity; exact values match the oracle.
- AC6: Cache bytes, construction batches and temporary index resources obey explicit limits; cancellation and disk-full failures leave the source and last valid display intact.
- AC7: Include at least 1 million aggregate samples, sparse/nonnumeric/irregular/duplicate cases and repeat-navigation memory checks.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Integrated warm/cold navigation meets the documented budgets with 1/4/8 lanes.
- request-AC3 -> This backlog slice. Proof: AC3: Instrumentation proves broad queries read bounded summary rows as fixture duration grows 10x; overview and exact point caps hold independently of raw volume.
- request-AC4 -> This backlog slice. Proof: AC4: Oscillating 400-sample and late-spike fixtures preserve end timestamp and all required bucket extrema within the cap, ordered by timestamp/sample identity; exact values match the oracle.
- request-AC6 -> This backlog slice. Proof: AC6: Cache bytes, construction batches and temporary index resources obey explicit limits; cancellation and disk-full failures leave the source and last valid display intact.
- request-AC7 -> This backlog slice. Proof: AC7: Include at least 1 million aggregate samples, sparse/nonnumeric/irregular/duplicate cases and repeat-navigation memory checks.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_024_peaklive_responsive_and_faithful_historical_navigation_correction`
- Architecture decision(s): (none yet)
- Request: `req_025_restore_responsive_and_faithful_historical_graph_navigation`
- Primary task(s): `task_025_deliver_responsive_and_faithful_historical_graph_navigation`

# Priority
- Priority: High - broad-view scans dominate latency and the existing envelope can lose late data.
- Rationale: Set by scaffold input or defaulted for grooming.
