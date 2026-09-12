## item_123_bound_viewport_scheduling_and_expose_truthful_loading_and_measurement_states - Bound viewport scheduling and expose truthful loading and measurement states
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 35%
> Complexity: High
> Theme: Historical request lifecycle and cache consistency
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-12 17:10:01

# AI Context
- Summary: Bound workers and caches while preserving current results and analytical truthfulness.
- Keywords: bound, viewport, scheduling, expose, truthful, loading, measurement, states
- Use when: Implementing cancellable latest-viewport requests, revision isolation and nonmodal states.
- Skip when: Changing acquisition transport or recovering unrecorded live frames.

# Problem
- A new QThread can start for every refresh, while cancellation is checked only between signals. Cache-hit callbacks rebuild keys from current UI state and can leave incompatible requests active.
- Bounds and historical measurements still perform SQL on the UI thread; the worker failed signal is not presented to the operator.

# Scope
- In:
  - For a signal selected after file loading, reconstruct its complete history in cancellable background work with visible progress, preserving viewport, cursors and other lanes. Publish exact samples, complete summaries and event anchors under source/DBC/data revision checks, invalidate cached empty results, and never silently substitute the retained tail. Report source-unavailable/changed, cancelled, partial and failed states explicitly.
  - Stream the original file through the existing parser and DBC decoding path in bounded chunks, without replaying frames into acquisition/session counters or retaining the entire capture in RAM. Serialize reconstruction jobs, deduplicate signal requests and reuse completed revision-matched history. Coordinate SQLite writer ownership with ingestion; publish coverage atomically only after successful completion. Deselection, reload, DBC changes and shutdown retire stale jobs. Measure preparation separately from viewport latency; no full reconstruction promise for unrecorded live frames.
  - Implement one active plus one replaceable pending request, actual SQL/chunk cancellation, immutable result identity and a canonical viewport key including source/DBC/data revisions, signal set, width and resolution.
  - Invalidate incompatible in-flight work on cache hits; fix cache-hit/replacement point accounting and enforce a byte limit of 64 MiB across all lanes.
  - Use revision-cached bounds; keep scans and long exact measurement work off the GUI thread. Do not dirty unchanged or hidden measurements on a viewport-only change.
  - Retain last valid curves while pending and present accessible loading, incomplete, empty and error states through existing i18n. Diagnose the busy pointer with request/heartbeat evidence before attributing it.
  - Make A/B overflow/partial coverage explicit instead of silently falling back to a retained tail or dropping selected lanes; preserve current export coverage semantics.
  - Retain the read-only SQLite worker fix and safe QThread teardown from 7cc00d6; cover shutdown, reset, selection changes and cache-hit A/B/A races.
- Out:
  - General application concurrency rewrite, acquisition transport changes and raising retention caps to hide missing history.

# Acceptance criteria
- AC1: Rapid reverse zoom and cache hits cannot install an empty or stale result over valid current data.
- AC5: Queue, cancellation, revision and memory invariants hold over 1000 gestures; measured reference-machine latency/heartbeat targets hold with three and eight lanes.
- AC6: Pending/error state clears on completion/cancel, historical analytical overflow is explicit, and pure navigation does not issue hidden/unchanged measurement queries. Compare preselected and late-selected versions of the same signal against a full-file raw oracle beyond 50000 aggregate frames, including rare events early in the file. Verify identical timecodes/values, rendered full coverage and event discoverability; assert zoom/cursors/other lanes and session counters stay unchanged. Exercise cancellation/retry, duplicate selection, source missing/changed, DBC change, reload, shutdown and stale empty-cache completion. Qualify the reported after-load case in the Windows artifact.
- AC8: Regressions exercise real in-flight workers, source resets and failure delivery rather than only finished-signal flags.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Rapid reverse zoom and cache hits cannot install an empty or stale result over valid current data.
- request-AC5 -> This backlog slice. Proof: AC5: Queue, cancellation, revision and memory invariants hold over 1000 gestures; measured reference-machine latency/heartbeat targets hold with three and eight lanes.
- request-AC6 -> This backlog slice. Proof: AC6: Pending/error state clears on completion/cancel, historical analytical overflow is explicit, and pure navigation does not issue hidden/unchanged measurement queries.
- request-AC8 -> This backlog slice. Proof: AC8: Regressions exercise real in-flight workers, source resets and failure delivery rather than only finished-signal flags.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_025_discoverable_rare_diagnostic_events_in_dense_historical_views`
- Architecture decision(s): (none yet)
- Request: `req_026_restore_dense_historical_curves_and_preserve_rare_diagnostic_signal_events`
- Primary task(s): `task_026_restore_dense_historical_overview_coverage_and_rare_event_discoverability`

# Priority
- Priority: High - correctness must survive rapid navigation without reintroducing the previous UI lag.
- Rationale: Set by scaffold input or defaulted for grooming.
