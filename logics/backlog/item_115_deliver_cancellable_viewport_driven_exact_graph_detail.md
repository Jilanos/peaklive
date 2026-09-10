## item_115_deliver_cancellable_viewport_driven_exact_graph_detail - Deliver cancellable viewport-driven exact graph detail
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 55%
> Complexity: High
> Theme: Zoom detail scheduling and analytical truthfulness
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-10 12:36:27

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: deliver, cancellable, viewport, driven, exact, graph, detail
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Graph navigation changes the visible range but has no source-backed request path for exact samples outside bounded retained series.
- Rapid pan and zoom gestures can create obsolete background work; accepting its result would display data for the wrong viewport or wrong session.
- Operators need an explicit distinction between an overview curve, an exact curve, a loading state, and unavailable exact detail.

# Scope
- In:
  - Define an automatic viewport policy: use an overview above the documented samples-per-pixel threshold and request exact detail below it, with a configurable or documented guard band to avoid request thrash.
  - Implement debounced, generation-safe, cancellable background range decoding and atomic graph replacement for each selected signal.
  - Add translated, accessible overview/exact/loading/unavailable states without hiding existing graph navigation or cursor controls.
  - Make cursor and measurement consumers request or require exact range data where their result is presented as exact; preserve existing export and trace-table semantics unless an explicit exact-data contract is added.
  - Test rapid viewport changes, signal toggles, replay replacement, worker shutdown, DBC/source failures, sparse and dense signals, and supported screen widths.
- Out:
  - A manual-only mode switch as the sole way to obtain precision.
  - Blocking full-file reparse on the UI thread, fabricated interpolated detail, or silent fallback from requested exact data to approximation.

# Acceptance criteria
- AC3: Zooming to a range below the policy threshold installs exact source-decoded samples for that range without freezing the UI and rejects stale requests safely.
- AC4: Exact graph points match the source capture and active DBC decode values and timestamps exactly.
- AC5: The operator can distinguish overview, exact, loading, and unavailable states through visible and accessible UI feedback.
- AC6: Debouncing, workers, caches, and graph point counts remain bounded under repeated navigation.
- AC7: Measurements and cursors either operate on exact requested data or clearly state their limitation; existing replay and acquisition contracts remain valid.
- AC8: Automated tests prove accurate range detail, cancellation, lifecycle replacement, responsiveness, and no regression in graph navigation.

# AC Traceability
- request-AC3 -> This backlog slice. Proof: AC3: Zooming to a range below the policy threshold installs exact source-decoded samples for that range without freezing the UI and rejects stale requests safely.
- request-AC4 -> This backlog slice. Proof: AC4: Exact graph points match the source capture and active DBC decode values and timestamps exactly.
- request-AC5 -> This backlog slice. Proof: AC5: The operator can distinguish overview, exact, loading, and unavailable states through visible and accessible UI feedback.
- request-AC6 -> This backlog slice. Proof: AC6: Debouncing, workers, caches, and graph point counts remain bounded under repeated navigation.
- request-AC7 -> This backlog slice. Proof: AC7: Measurements and cursors either operate on exact requested data or clearly state their limitation; existing replay and acquisition contracts remain valid.
- request-AC8 -> This backlog slice. Proof: AC8: Automated tests prove accurate range detail, cancellation, lifecycle replacement, responsiveness, and no regression in graph navigation.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_022_peaklive_multiresolution_lossless_historical_trace_detail`
- Architecture decision(s): (none yet)
- Request: `req_023_deliver_multiresolution_trace_graphs_with_precise_on_demand_zoom_detail`
- Primary task(s): `task_023_deliver_bounded_multiresolution_overview_and_exact_zoom_detail_for_historical_traces`

# Priority
- Priority: High - analysts need real values, not an overview approximation, when investigating a short time interval.
- Rationale: Set by scaffold input or defaulted for grooming.
