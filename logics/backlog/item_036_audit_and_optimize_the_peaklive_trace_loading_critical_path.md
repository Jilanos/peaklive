## item_036_audit_and_optimize_the_peaklive_trace_loading_critical_path - Audit and optimize the PeakLive trace loading critical path
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: High
> Theme: Performance diagnosis and bounded replay presentation
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-28 20:14:24

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: audit, optimize, peaklive, trace, loading, critical, path
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- The application has no stage-level evidence showing whether parse, decode, projection, or graph/report refresh dominates large-trace latency.
- Replay batches can cause repeated UI projection work even though retained trace and series stores are bounded.
- A performance change without budgets and responsiveness assertions risks moving the bottleneck or regressing cancellation and replacement.

# Scope
- In:
  - Add sanitized and synthetic benchmark fixtures and stage-level timing instrumentation that is cheap or disabled outside tests.
  - Measure parser, worker, decoding, trace/series projection, graph refresh, and report refresh separately at representative volumes.
  - Optimize the dominant costs with bounded batching/coalescing and explicit progress/cancellation budgets.
  - Add offscreen event-loop responsiveness and memory/retention regression coverage.
- Out:
  - Binary formats, hardware acquisition, CAN FD, or semantic DBC changes.
  - Removing malformed-record evidence or increasing retention limits without a documented budget.

# Acceptance criteria
- AC1: The audit report identifies stage-level timings and a dominant-cost conclusion for representative trace sizes.
- AC2: Large-trace opening meets documented latency, responsiveness, progress, cancellation, and bounded-work budgets.
- AC7: Existing replay, filters, reports, cancellation, replacement, and bounded stores remain regression-free.
- AC8: Benchmark and UI tests are deterministic and run in CI without external captures.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: The audit report identifies stage-level timings and a dominant-cost conclusion for representative trace sizes.
- request-AC2 -> This backlog slice. Proof: AC2: Large-trace opening meets documented latency, responsiveness, progress, cancellation, and bounded-work budgets.
- request-AC7 -> This backlog slice. Proof: AC7: Existing replay, filters, reports, cancellation, replacement, and bounded stores remain regression-free.
- request-AC8 -> This backlog slice. Proof: AC8: Benchmark and UI tests are deterministic and run in CI without external captures.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_009_peaklive_fast_explorable_and_globally_navigable_traces`
- Architecture decision(s): (none yet)
- Request: `req_009_audit_peaklive_performance_and_make_trace_signal_exploration_and_time_navigation_complete`
- Primary task(s): `task_010_deliver_a_measured_lazy_and_globally_navigable_peaklive_trace_workspace`

# Priority
- Priority: High - trace opening is a core workflow and current load latency prevents reliable use of large captures.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_010_deliver_a_measured_lazy_and_globally_navigable_peaklive_trace_workspace`

# Notes
- Task `task_010_deliver_a_measured_lazy_and_globally_navigable_peaklive_trace_workspace` was finished via `logics-manager flow finish task` on 2026-08-28.
