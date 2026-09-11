## item_117_coalesce_historical_viewport_requests_and_own_cancellable_background_reads - Coalesce historical viewport requests and own cancellable background reads
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 95%
> Complexity: High
> Theme: Qt scheduling and historical worker lifecycle
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-11 16:00:33

# AI Context
- Summary: Replace accumulated GUI callbacks with one latest-viewport scheduler and owned cancellable history reads.
- Keywords: coalesce, historical, viewport, requests, own, cancellable, background, reads
- Use when: Fixing event amplification, SQLite thread ownership, stale results and lifecycle teardown.
- Skip when: Choosing the summary hierarchy; that follows in the bounded summaries slice.

# Problem
- Static singleShot callbacks accumulate; linked lanes repeat the same full-panel refresh.
- Historical queries run synchronously in the GUI and share its SQLite connection.

# Scope
- In:
  - Replace static per-event timers with one parent-owned restartable single-shot timer and canonical anchor viewport deduplication including fit, wheel, pan and resize.
  - Introduce a worker-owned SQLite read connection and immutable bounded result contract; retain all widget updates in the GUI thread. Do not use check_same_thread=False as the ownership design.
  - Keep one active request and one replaceable pending request. Include session generation, DBC/source and data revisions, signal selection, range and resolution in request keys. Cancel active SQL/chunked preparation, not only result installation.
  - Keep the last valid curve while pending, update only changed curves, and retire pending timers/readers before session teardown without GUI joins or lock waits.
  - Cache global/signal bounds by data revision. Instrument request count, queue depth, cancellation latency, GUI apply cost and query thread identity.
- Out:
  - Claiming that threading alone removes the O(raw samples) overview cost.
  - Changing acquisition transport or discarding raw samples.

# Acceptance criteria
- AC1: Navigation enqueue/apply operations respect the event-loop budget; full acceptance follows summary integration.
- AC2: A burst of 30 identical refresh requests yields one latest-viewport execution; linked lane duplicates do not multiply executions. SQL never runs on the GUI thread.
- AC6: Queue depth never exceeds one active plus one pending; old-session results and callbacks are rejected after reset, replacement, deselection and shutdown.
- AC7: Deterministic tests exercise cancellation during actual work, not just completion-generation checks, and preserve live navigation and replay completion behavior.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Navigation enqueue/apply operations respect the event-loop budget; full acceptance follows summary integration.
- request-AC2 -> This backlog slice. Proof: AC2: A burst of 30 identical refresh requests yields one latest-viewport execution; linked lane duplicates do not multiply executions. SQL never runs on the GUI thread.
- request-AC6 -> This backlog slice. Proof: AC6: Queue depth never exceeds one active plus one pending; old-session results and callbacks are rejected after reset, replacement, deselection and shutdown.
- request-AC7 -> This backlog slice. Proof: AC7: Deterministic tests exercise cancellation during actual work, not just completion-generation checks, and preserve live navigation and replay completion behavior.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_024_peaklive_responsive_and_faithful_historical_navigation_correction`
- Architecture decision(s): (none yet)
- Request: `req_025_restore_responsive_and_faithful_historical_graph_navigation`
- Primary task(s): `task_025_deliver_responsive_and_faithful_historical_graph_navigation`

# Priority
- Priority: High - each zoom currently queues synchronous work that can freeze input for seconds.
- Rationale: Set by scaffold input or defaulted for grooming.
