## item_124_qualify_long_view_rare_event_fidelity_on_the_packaged_windows_application - Qualify long-view rare-event fidelity on the packaged Windows application
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Behavioral qualification and reproducible evidence
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-12 16:42:24

# AI Context
- Summary: Prove source coverage, rendered visibility and rare-event drill-down on an identified artifact.
- Keywords: qualify, long, view, rare, event, fidelity, packaged, windows, application
- Use when: Qualifying the three-lane private reproduction and deterministic synthetic cases.
- Skip when: Treating passing flag tests or a private-data upload as acceptable evidence.

# Problem
- Unit-level bounds and curve settings passed while the operator lost all three diagnostic curves after one wheel step.

# Scope
- In:
  - Turn the source/render diagnostic into deterministic synthetic tests with one million aggregate samples, three/eight lanes, mixed batch sizes, 1/10/100 ms periods, irregular timing and non-extreme two-frame events.
  - Sweep 500/640/650/660/800 s and whole capture plus pixel-width-dependent threshold probes. Record raw rows, summary coverage, display counts, event anchors, detail mode, active/pending work and final generation.
  - Qualify exact zoom/drill-down around original event timestamps and distinguish event clusters from measured source values.
  - Use the operator's preselected signals with local DBC configuration and private trace on an identified Windows executable; copy its build identity and record artifact hash, screen geometry and exact gestures privately.
  - Run required repository tests on Linux and Windows, packaging, Logics validation and the packaged visual reproduction; keep private data and source labels out of versioned evidence.
  - Write AC-by-AC evidence and remaining limitations. Preserve prior task 025 history; do not close this correction while artifact-specific qualification or the mandatory pulse/dip fidelity evidence remains missing.
- Out:
  - A private capture committed to CI, passive green-CI-only acceptance, and rewriting prior completion proof.

# Acceptance criteria
- AC1: The operator's forward/reverse wheel-zoom sequence and full fit remain populated in the packaged application.
- AC2: Batch partition/reset cases prove summary completeness and cache invalidation.
- AC3: Actual display output preserves coverage, point policy and explicit empty/incomplete distinctions.
- AC4: Rare short-event discoverability and exact-timecode drill-down are demonstrated at all tested scales.
- AC5: Attach independent row-work, cache, queue and GUI-heartbeat evidence including cold/warm/index preparation phases.
- AC6: Analytical truthfulness, pending/error recovery and stable live behavior are verified. Compare preselected and late-selected versions of the same signal against a full-file raw oracle beyond 50000 aggregate frames, including rare events early in the file. Verify identical timecodes/values, rendered full coverage and event discoverability; assert zoom/cursors/other lanes and session counters stay unchanged. Exercise cancellation/retry, duplicate selection, source missing/changed, DBC change, reload, shutdown and stale empty-cache completion. Qualify the reported after-load case in the Windows artifact.
- AC7: Copy/paste of the build identity agrees with artifact evidence.
- AC8: Linux/Windows CI, Windows packaging, private reproduction and all evidence gates pass before task closeout.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: The operator's forward/reverse wheel-zoom sequence and full fit remain populated in the packaged application.
- request-AC2 -> This backlog slice. Proof: AC2: Batch partition/reset cases prove summary completeness and cache invalidation.
- request-AC3 -> This backlog slice. Proof: AC3: Actual display output preserves coverage, point policy and explicit empty/incomplete distinctions.
- request-AC4 -> This backlog slice. Proof: AC4: Rare short-event discoverability and exact-timecode drill-down are demonstrated at all tested scales.
- request-AC5 -> This backlog slice. Proof: AC5: Attach independent row-work, cache, queue and GUI-heartbeat evidence including cold/warm/index preparation phases.
- request-AC6 -> This backlog slice. Proof: AC6: Analytical truthfulness, pending/error recovery and stable live behavior are verified.
- request-AC7 -> This backlog slice. Proof: AC7: Copy/paste of the build identity agrees with artifact evidence.
- request-AC8 -> This backlog slice. Proof: AC8: Linux/Windows CI, Windows packaging, private reproduction and all evidence gates pass before task closeout.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_025_discoverable_rare_diagnostic_events_in_dense_historical_views`
- Architecture decision(s): (none yet)
- Request: `req_026_restore_dense_historical_curves_and_preserve_rare_diagnostic_signal_events`
- Primary task(s): `task_026_restore_dense_historical_overview_coverage_and_rare_event_discoverability`

# Priority
- Priority: High - existing green tests did not detect the operator-visible disappearance.
- Rationale: Set by scaffold input or defaulted for grooming.
