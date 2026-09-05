## item_069_decimate_plots_and_bound_measurement_recomputation - Decimate plots and bound measurement recomputation
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: P1 graph performance
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-05 10:41:26

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: decimate, plots, bound, measurement, recomputation
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Plots redraw all points and statistics recalculate at 20 Hz.

# Scope
- In:
  - Enable clipping and downsampling.
  - Coalesce A-B statistics.
  - Measure with eight signals and separated cursors.
- Out:
  - Changing statistical definitions.

# Acceptance criteria
- Displayed points are bounded by viewport policy.
- Measurement calculations run no more than their documented cadence and preserve final values.

# AC Traceability
- request-AC7 -> This backlog slice. Proof: Displayed points are bounded by viewport policy.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - graph refresh work scales beyond screen resolution
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Notes
- Task `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone` was finished via `logics-manager flow finish task` on 2026-09-05.
