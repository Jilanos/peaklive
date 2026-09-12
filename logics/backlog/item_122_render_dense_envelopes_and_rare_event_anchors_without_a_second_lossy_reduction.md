## item_122_render_dense_envelopes_and_rare_event_anchors_without_a_second_lossy_reduction - Render dense envelopes and rare event anchors without a second lossy reduction
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Pixel-aware historical rendering and diagnostic fidelity
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-12 16:30:45

# AI Context
- Summary: Render source extrema once and retain short-event anchors independently of envelopes.
- Keywords: render, dense, envelopes, rare, event, anchors, second, lossy, reduction
- Use when: Fixing blank sparse historical curves and preserving diagnostic event discoverability.
- Skip when: Using uniform stride or claiming finite pixels show every raw event individually.

# Problem
- Automatic pyqtgraph peak downsampling is applied again to already-reduced sparse history and can output zero points.
- Min/max alone can omit a diagnostically important short transition that is not a bucket extremum.

# Scope
- In:
  - Give each prepared result explicit mode, coverage, source count, range, width and budget metadata. Disable automatic secondary reduction for historical envelopes and restore the existing live policy on mode changes.
  - Use min(4000, max(256, 4 * viewport_width_px)) as the proposed historical envelope budget and retain the 20000-source-sample exact cap; select modes by density/coverage with hysteresis.
  - Preserve first/min/max/last real samples and gaps; represent isolated samples explicitly. Test data actually passed through PlotDataItem.getData() and visual paths.
  - Define discrete/error transition anchors independently of the analog envelope, preserving original timecodes. Cluster only presentation when multiple anchors collide, with visible count/range and exact zoom/drill-down.
  - Operator-confirmed analog case: preserve a 250 A to 180 A dip lasting 100 ms, including entry/extremum/recovery anchors even beside a larger bucket extremum. The binary case is four asserted frames after 50000 quiet frames. No configured threshold is required; dense noisy changes may use truthful activity clusters.
  - Keep markers distinct from samples and preserve exact A/B/export source semantics. Document enum and nonfinite behavior; do not fabricate numeric zeros.
  - Study reference-project pixel budgets, time-bucket source extrema, metadata and error states; reimplement these contracts in the existing stack without copying its renderer or async mutation race.
- Out:
  - Uniform Nth-sample decimation, averaging diagnostic peaks, semantic threshold guessing and an oscillation-density overlay as an independent product feature.

# Acceptance criteria
- AC1: Three lanes stay visible across forward/reverse zoom sweeps and width changes when source evidence exists.
- AC3: Nonempty sparse prepared results cannot become empty through secondary reduction; exact/overview/empty/incomplete statuses and one-point behavior are tested.
- AC4: Inject one/two-frame pulses, the four-frame assertion after 50000 quiet frames, and the 250 A to 180 A dip lasting 100 ms at bucket edges and late in the trace, including non-extreme error-code changes; verify a source-timecode anchor or explicit cluster survives every level and zoom exposes the original samples.
- AC6: Marker/envelope data never supplies supposedly exact measurements or exports.
- AC8: Attach renderer-level and packaged visual evidence, not just option assertions.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Three lanes stay visible across forward/reverse zoom sweeps and width changes when source evidence exists.
- request-AC3 -> This backlog slice. Proof: AC3: Nonempty sparse prepared results cannot become empty through secondary reduction; exact/overview/empty/incomplete statuses and one-point behavior are tested.
- request-AC4 -> This backlog slice. Proof: AC4: Inject one/two-frame pulses, the four-frame assertion after 50000 quiet frames, and the 250 A to 180 A dip lasting 100 ms at bucket edges and late in the trace, including non-extreme error-code changes; verify a source-timecode anchor or explicit cluster survives every level and zoom exposes the original samples.
- request-AC6 -> This backlog slice. Proof: AC6: Marker/envelope data never supplies supposedly exact measurements or exports.
- request-AC8 -> This backlog slice. Proof: AC8: Attach renderer-level and packaged visual evidence, not just option assertions.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_025_discoverable_rare_diagnostic_events_in_dense_historical_views`
- Architecture decision(s): (none yet)
- Request: `req_026_restore_dense_historical_curves_and_preserve_rare_diagnostic_signal_events`
- Primary task(s): `task_026_restore_dense_historical_overview_coverage_and_rare_event_discoverability`

# Priority
- Priority: High - two-frame errors must stay discoverable and populated curves must never disappear on zoom-out.
- Rationale: Set by scaffold input or defaulted for grooming.
