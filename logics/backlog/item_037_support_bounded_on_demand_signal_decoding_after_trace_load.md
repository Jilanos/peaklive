## item_037_support_bounded_on_demand_signal_decoding_after_trace_load - Support bounded on-demand signal decoding after trace load
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: High
> Theme: Lazy signal exploration and session reuse
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-28 20:14:24

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: support, bounded, demand, signal, decoding, after, trace, load
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- SeriesStore currently receives decoded samples only for signals selected during ingestion, leaving later selections without historical data.
- The UI selection path can rebuild graph definitions but has no bounded source/index contract for deriving a newly selected signal from the loaded session.
- Reopening the trace would repeat parsing and decoding, reset user state, and amplify the performance problem.

# Scope
- In:
  - Define a bounded loaded-session source/index or replay cache sufficient to derive newly selected supported signals without reopening the file.
  - Decode newly requested signals off the UI critical path, merge samples exactly once into bounded SeriesStore projections, and preserve filters/report/session facts.
  - Expose loading, unavailable decode, and completion states for on-demand signal population.
  - Cover repeated selection, deselection, replacement, cancellation, and capacity behavior with offscreen tests.
- Out:
  - Unbounded retention of every decoded signal or full duplicate copies of capture data.
  - Changes to DBC interpretation rules or trace editing.

# Acceptance criteria
- AC3: A signal selected after load appears from the existing session without reopening or reparsing the trace, and repeated toggles do not duplicate samples.
- AC4: On-demand decoding is bounded, deterministic, cancellable, and explicit when data is unavailable.
- AC7: Existing graph, filter, report, replay replacement, and bounded-store behavior remains correct.
- AC8: Tests prove lazy selection behavior at high volume and across replacement/cancellation races.

# AC Traceability
- request-AC3 -> This backlog slice. Proof: AC3: A signal selected after load appears from the existing session without reopening or reparsing the trace, and repeated toggles do not duplicate samples.
- request-AC4 -> This backlog slice. Proof: AC4: On-demand decoding is bounded, deterministic, cancellable, and explicit when data is unavailable.
- request-AC7 -> This backlog slice. Proof: AC7: Existing graph, filter, report, replay replacement, and bounded-store behavior remains correct.
- request-AC8 -> This backlog slice. Proof: AC8: Tests prove lazy selection behavior at high volume and across replacement/cancellation races.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_009_peaklive_fast_explorable_and_globally_navigable_traces`
- Architecture decision(s): (none yet)
- Request: `req_009_audit_peaklive_performance_and_make_trace_signal_exploration_and_time_navigation_complete`
- Primary task(s): `task_010_deliver_a_measured_lazy_and_globally_navigable_peaklive_trace_workspace`

# Priority
- Priority: High - analysts must not reload a large trace just to inspect another signal.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_010_deliver_a_measured_lazy_and_globally_navigable_peaklive_trace_workspace`

# Notes
- Task `task_010_deliver_a_measured_lazy_and_globally_navigable_peaklive_trace_workspace` was finished via `logics-manager flow finish task` on 2026-08-28.
