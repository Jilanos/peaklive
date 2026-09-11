## item_119_align_historical_navigation_extents_and_measurement_truthfulness - Align historical navigation extents and measurement truthfulness
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 70%
> Complexity: Medium
> Theme: Historical graph and analytical consumer contracts
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-11 16:00:33

# AI Context
- Summary: Make fit and historical A/B semantics agree with full source coverage and current detail readiness.
- Keywords: align, historical, navigation, extents, measurement, truthfulness
- Use when: Integrating authoritative extents, accessible detail states and partial or unavailable historical measurements.
- Skip when: Adding full-file backfill for arbitrary newly selected signals or redesigning exports.

# Problem
- Fit/global_extent reads bounded live series while curve loading uses historical bounds.
- Measurements still use the retained tail, and historical empty/overflow states are ambiguous.

# Scope
- In:
  - Use a single cached historical extent for fit, follow, initial capture display and viewport selection; preserve live zero-based semantics.
  - Expose accessible overview/exact/loading/unavailable states through existing UI and translation conventions, with no modal navigation blocker.
  - For historical A/B ranges outside complete retained coverage, obtain exact source-backed results asynchronously where supported or explicitly mark partial/unavailable values; never calculate exact statistics from overview points.
  - Avoid measurement recomputation for unchanged cursors/data and while the values panel is hidden; refresh once on reveal when dirty.
  - Distinguish missing history after late signal selection from a genuinely empty visible interval. Document this limitation instead of claiming full-file backfill.
  - Define nonnumeric/gap plotting behavior without inventing numeric zero samples; invalidate view and measurement results on relevant session/DBC changes.
- Out:
  - A general export or measurement architecture rewrite.
  - Building a new full-file decoder for arbitrary signals selected after replay.

# Acceptance criteria
- AC4: Displayed range coverage is complete and enum/gap handling cannot fabricate exact numeric evidence.
- AC5: Fit returns to actual full history after tail truncation; accessible state tracks pending/exact/overview/failure, and partial historical A/B values are never presented as exact full-range results.
- AC6: Late results cannot overwrite a new DBC/session or update hidden/deselected curves.
- AC7: Cursor persistence, follow disable on manual zoom, export retained-buffer semantics and live acquisition remain covered by existing regressions.

# AC Traceability
- request-AC4 -> This backlog slice. Proof: AC4: Displayed range coverage is complete and enum/gap handling cannot fabricate exact numeric evidence.
- request-AC5 -> This backlog slice. Proof: AC5: Fit returns to actual full history after tail truncation; accessible state tracks pending/exact/overview/failure, and partial historical A/B values are never presented as exact full-range results.
- request-AC6 -> This backlog slice. Proof: AC6: Late results cannot overwrite a new DBC/session or update hidden/deselected curves.
- request-AC7 -> This backlog slice. Proof: AC7: Cursor persistence, follow disable on manual zoom, export retained-buffer semantics and live acquisition remain covered by existing regressions.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_024_peaklive_responsive_and_faithful_historical_navigation_correction`
- Architecture decision(s): (none yet)
- Request: `req_025_restore_responsive_and_faithful_historical_graph_navigation`
- Primary task(s): `task_025_deliver_responsive_and_faithful_historical_graph_navigation`

# Priority
- Priority: High - a responsive plot must not misrepresent capture coverage or exact measurements.
- Rationale: Set by scaffold input or defaulted for grooming.
