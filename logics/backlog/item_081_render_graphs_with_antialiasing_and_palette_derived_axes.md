## item_081_render_graphs_with_antialiasing_and_palette_derived_axes - Render graphs with antialiasing and palette-derived axes
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 39%
> Complexity: Low
> Theme: P2 graph visual quality
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: render, graphs, antialiasing, palette, derived, axes
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Curves lack antialiasing and axes/grid ignore theme tokens.

# Scope
- In:
  - Enable pyqtgraph antialiasing.
  - Set plot background, axis pens, and grid from tokens.
- Out:
  - New graph types.

# Acceptance criteria
- Curves, labels, grid, and background use documented tokens.

# AC Traceability
- request-AC6 -> This backlog slice. Proof: Curves, labels, grid, and background use documented tokens.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - plots and axes look disconnected from the UI
- Rationale: Set by scaffold input or defaulted for grooming.
