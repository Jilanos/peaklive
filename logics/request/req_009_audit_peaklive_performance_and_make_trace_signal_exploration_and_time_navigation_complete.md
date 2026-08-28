## req_009_audit_peaklive_performance_and_make_trace_signal_exploration_and_time_navigation_complete - Audit PeakLive performance and make trace signal exploration and time navigation complete
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Application performance, lazy signal exploration, and complete time-axis navigation
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-08-28 20:14:23

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: audit, peaklive, performance, trace, signal, exploration, time, navigation, complete
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Needs
- An analyst must be able to open large ASC/TRC captures without an unexpectedly long or UI-blocking load phase.
- After a trace is loaded, selecting a signal that was not initially selected must populate its graph from the loaded trace without reopening or reparsing the file.
- Trace graphs must offer a complete-capture view instead of defaulting to only the last few seconds, while live acquisition must keep a global X-axis beginning at zero and expand it as data arrives.
- The project needs an evidence-based performance audit covering parser, worker dispatch, projection, graph refresh, bounded storage, and lifecycle cancellation before optimization changes are accepted.

# Context
- Replay currently parses incrementally but each rendered batch is decoded and projected only for currently selected signals, so later signal selection has no historical samples to display.
- The replay and graph paths combine file parsing, DBC decoding, trace-table updates, series updates, report refreshes, and plot redraws; large captures can therefore spend most of their time in presentation work rather than file IO.
- GraphStackPanel follows the live tail by default and its range behavior is shared between replay and acquisition, which makes a completed trace appear limited to its newest few seconds and makes live analysis lose a stable overview.
- TraceBuffer and SeriesStore are intentionally bounded, so any fix must preserve bounded memory and explicit retention semantics rather than retaining every decoded sample indefinitely.
- The existing ASC/TRC replay reliability work provides generation-safe replacement and bounded anomaly dispatch; this corpus audits and extends that behavior without widening into binary formats or hardware acquisition.

# Acceptance criteria
- AC1: A reproducible performance audit measures representative small, medium, and high-volume ASC/TRC loads across parsing, worker dispatch, decoding, trace projection, series projection, graph refresh, and report refresh, with documented budgets and an identified dominant-cost breakdown.
- AC2: Opening a large supported trace remains responsive under the documented budget: progress is visible, user actions and cancellation are serviced within the responsiveness bound, and no stage performs an accidental eager full-file or unbounded UI projection.
- AC3: A loaded trace retains sufficient bounded source/session information to add a previously unselected signal without reopening the file; selecting or deselecting signals updates graphs and measurements without resetting the session or duplicating samples.
- AC4: Signal-on-demand decoding is bounded and deterministic: it reuses parsed/retained data or an explicit indexed cache, reports unavailable/unsupported decode facts clearly, and does not silently require a second trace load.
- AC5: A completed trace defaults to a view spanning the full available capture extent (from the trace origin to its final timestamp), with an explicit follow-tail control for analysts who want tail behavior.
- AC6: During acquisition, the X-axis starts at zero and expands monotonically with elapsed session time so the operator can see the global signal history; optional follow-tail navigation remains available without changing the global extent semantics.
- AC7: Existing bounded trace/series capacities, filters, reports, replay replacement/cancellation, and normal acquisition behavior remain correct on Linux and Windows CI.
- AC8: Sanitized parser fixtures, synthetic high-volume performance tests, offscreen UI responsiveness tests, lazy-signal selection tests, full-extent replay tests, and live-axis tests provide machine-checkable evidence for the delivered budgets and semantics.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_009_peaklive_fast_explorable_and_globally_navigable_traces`
- Architecture decision(s): (none yet)

# References
- src/peaklive/analysis/replay.py
- src/peaklive/services/replay_worker.py
- src/peaklive/ui/session_controller.py
- src/peaklive/ui/catalog_controller.py
- src/peaklive/ui/panels/graph_stack.py
- src/peaklive/analysis/series.py
- src/peaklive/analysis/trace.py
- tests/test_replay_worker.py
- tests/test_ui_analyst.py
- tests/test_ui_lifecycle.py

# Backlog
- `item_036_audit_and_optimize_the_peaklive_trace_loading_critical_path`
- `item_037_support_bounded_on_demand_signal_decoding_after_trace_load`
- `item_038_deliver_full_capture_replay_and_zero_based_live_time_navigation`
