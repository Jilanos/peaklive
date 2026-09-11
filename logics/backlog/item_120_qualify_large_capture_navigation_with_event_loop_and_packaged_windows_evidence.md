## item_120_qualify_large_capture_navigation_with_event_loop_and_packaged_windows_evidence - Qualify large capture navigation with event loop and packaged Windows evidence
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 70%
> Complexity: Medium
> Theme: Reproducible navigation regression qualification
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-11 16:00:33

# AI Context
- Summary: Prove interactive responsiveness and waveform fidelity using real event-loop measurements and an identifiable Windows executable.
- Keywords: qualify, large, capture, navigation, event, loop, packaged, windows, evidence
- Use when: Qualifying 1/4/8 lanes, scaling, cache endurance and the private-capture regression.
- Skip when: Using pyqtgraph option flags or total test runtime as a responsiveness verdict.

# Problem
- Existing graph tests mostly inspect pyqtgraph flags or bounded small series; they do not measure historical GUI blocking.
- The private capture reproduces the regression but cannot be the sole CI fixture or expose payloads.

# Scope
- In:
  - Turn the diagnostic cases into deterministic synthetic correctness and structural regression tests; retain the standalone probe for optional private capture evidence.
  - Build a GUI heartbeat harness driven by real Qt navigation with 1/4/8 linked lanes, 100 mixed gestures, widths 1024/1280/1600 and 1000-gesture cache endurance.
  - Report timing distributions, warm/cold and index-construction phases separately, row visits, point counts, active/pending requests, cancellation/stale counts, cache bytes and disk footprint.
  - Use at least 1 million historical samples with 100 Hz/1 kHz and irregular series, a 10x-duration complexity comparison, late extrema and independent exact-value oracles.
  - Qualify the identifiable packaged Windows executable after replay settles, with representative selected DBC signals. Record machine/build identity; re-run the private capture locally when available, without committing it.
  - Run focused historical/navigation/measurement/lifecycle tests plus required repository checks. Associate behavioral evidence with each request AC and explicitly identify unavailable platform/capture checks.
- Out:
  - Closing on total pytest runtime or option flags alone.
  - Hardware CAN transmission tests or public redistribution of the private capture.

# Acceptance criteria
- AC1: With completed historical data and 1, 4 and 8 linked lanes, 100 mixed wheel/pan/fit gestures meet a 20 ms heartbeat p95 lateness <= 50 ms and maximum <= 150 ms on the recorded Windows reference machine. Warm final viewport latency <= 250 ms and cold indexed-query latency <= 1 s after settling; index construction is separately reported.
- AC2: Navigation has one owned restartable 75 ms timer, at most one active and one replaceable pending history request; duplicate linked-axis notifications coalesce. No historical SQL, full-history scan or JSON reduction executes on the GUI thread. Obsolete work cancels and stale results cannot install.
- AC3: Broad views use indexed precomputed resolution levels and cached bounds. Returned overview points per lane <= min(4000, max(256, 4 * viewport_width_px)); raw exact points <= 20000. Instrumented rows visited scale with viewport budget and hierarchy depth rather than raw-range sample count.
- AC4: Every overview preserves full interval coverage, first/last samples and per-bucket extrema including late spikes, emits stable chronological timestamps/sample identities, and never truncates later buckets to meet its budget. Exact results match original decoded samples and distinguish overflow, empty, missing, error and cancelled states.
- AC5: Fit, follow and range selection use one authoritative historical extent; density-aware exact selection replaces the fixed 8-percent duration heuristic. Overview/exact/loading/unavailable states are visible and accessible; previous valid data remains usable while waiting. Historical A/B results are exact for their requested range or explicitly unavailable/partial.
- AC6: Session, source/DBC revision, data revision, signal selection and viewport generation isolate caches and workers. Historical viewport caches are capped at 64 MiB total; queues and index resources have explicit bounds and cleanup. Replacement, cancellation, deselection, disk errors and shutdown cannot apply stale data or block the GUI.
- AC7: Deterministic long dense/irregular/oscillating fixtures, 10x source-length scaling, real event-loop measurements and an identifiable packaged Windows replay prove the correction. Existing live capture, replay backpressure, trace retention, exports and decode semantics retain their documented behavior; no raw history is discarded to achieve speed.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: With completed historical data and 1, 4 and 8 linked lanes, 100 mixed wheel/pan/fit gestures meet a 20 ms heartbeat p95 lateness <= 50 ms and maximum <= 150 ms on the recorded Windows reference machine. Warm final viewport latency <= 250 ms and cold indexed-query latency <= 1 s after settling; index construction is separately reported.
- request-AC2 -> This backlog slice. Proof: AC2: Navigation has one owned restartable 75 ms timer, at most one active and one replaceable pending history request; duplicate linked-axis notifications coalesce. No historical SQL, full-history scan or JSON reduction executes on the GUI thread. Obsolete work cancels and stale results cannot install.
- request-AC3 -> This backlog slice. Proof: AC3: Broad views use indexed precomputed resolution levels and cached bounds. Returned overview points per lane <= min(4000, max(256, 4 * viewport_width_px)); raw exact points <= 20000. Instrumented rows visited scale with viewport budget and hierarchy depth rather than raw-range sample count.
- request-AC4 -> This backlog slice. Proof: AC4: Every overview preserves full interval coverage, first/last samples and per-bucket extrema including late spikes, emits stable chronological timestamps/sample identities, and never truncates later buckets to meet its budget. Exact results match original decoded samples and distinguish overflow, empty, missing, error and cancelled states.
- request-AC5 -> This backlog slice. Proof: AC5: Fit, follow and range selection use one authoritative historical extent; density-aware exact selection replaces the fixed 8-percent duration heuristic. Overview/exact/loading/unavailable states are visible and accessible; previous valid data remains usable while waiting. Historical A/B results are exact for their requested range or explicitly unavailable/partial.
- request-AC6 -> This backlog slice. Proof: AC6: Session, source/DBC revision, data revision, signal selection and viewport generation isolate caches and workers. Historical viewport caches are capped at 64 MiB total; queues and index resources have explicit bounds and cleanup. Replacement, cancellation, deselection, disk errors and shutdown cannot apply stale data or block the GUI.
- request-AC7 -> This backlog slice. Proof: AC7: Deterministic long dense/irregular/oscillating fixtures, 10x source-length scaling, real event-loop measurements and an identifiable packaged Windows replay prove the correction. Existing live capture, replay backpressure, trace retention, exports and decode semantics retain their documented behavior; no raw history is discarded to achieve speed.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_024_peaklive_responsive_and_faithful_historical_navigation_correction`
- Architecture decision(s): (none yet)
- Request: `req_025_restore_responsive_and_faithful_historical_graph_navigation`
- Primary task(s): `task_025_deliver_responsive_and_faithful_historical_graph_navigation`

# Priority
- Priority: High - current option-level tests passed while the delivered interaction freezes.
- Rationale: Set by scaffold input or defaulted for grooming.
