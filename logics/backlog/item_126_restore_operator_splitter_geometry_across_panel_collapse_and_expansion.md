## item_126_restore_operator_splitter_geometry_across_panel_collapse_and_expansion - Restore operator splitter geometry across panel collapse and expansion
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 50%
> Complexity: High
> Theme: Panel geometry state
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-13 15:34:34

# AI Context
- Summary: Separate operator geometry from automatic Qt allocations so center and side-panel round trips do not drift.
- Keywords: restore, operator, splitter, geometry, across, panel, collapse, expansion
- Use when: Changing splitter persistence, collapse reflow, resize allocation, or profile restoration.
- Skip when: Adding panel menu actions or changing graph title and cursor presentation.

# Problem
- The existing width memory can capture automatic redistributed geometry, especially when Graphs is collapsed, instead of retaining the operator's chosen divider positions.

# Scope
- In:
  - Reproduce the defect with actual minus/plus clicks and settled Qt events in tests/test_ui_workspace_refinement.py, including center collapse and non-LIFO reopen sequences.
  - Separate preferred user geometry from allocated splitter geometry in layout_reflow/profile_controller; record explicit drags and retain compatible snapshots or equivalent stable per-state preferences for round trips.
  - Define a deterministic constrained-width allocation: hidden panels consume zero, collapsed visible panels consume their rail, open panels respect feasible minimums, and the expanded center absorbs released space. Do not overwrite preferences during automatic redistribution or profile restoration.
  - Preserve existing vertical divider positions and profile serialization through an additive backwards-compatible state representation; validate malformed or incomplete persisted values using existing model conventions.
- Out:
  - Menu visibility actions, overlay titles, cursor-row presentation, and unrelated active historical-rendering work.

# Acceptance criteria
- AC1: Actual toggle-button round trips satisfy request AC1 within 2 logical pixels after event settling for all three panels and repeated/mixed sequences; explicit drags establish the subsequent preferred layout.
- AC2: Resize-small/expand/resize-back tests prove deterministic allocation and restoration of retained preferences without negative widths or offscreen controls where minimums are feasible.
- AC3: Tests of restart, profile switching, collapsed startup, and save debouncing preserve each profile's widths and vertical dividers without transient-geometry corruption.
- AC4: Record failing-before/passing-after geometry evidence and run focused layout/profile regressions; document the state model for the following visibility slice.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Actual toggle-button round trips satisfy request AC1 within 2 logical pixels after event settling for all three panels and repeated/mixed sequences; explicit drags establish the subsequent preferred layout.
- request-AC2 -> This backlog slice. Proof: AC2: Resize-small/expand/resize-back tests prove deterministic allocation and restoration of retained preferences without negative widths or offscreen controls where minimums are feasible.
- request-AC9 -> This backlog slice. Proof: AC3: Tests of restart, profile switching, collapsed startup, and save debouncing preserve each profile's widths and vertical dividers without transient-geometry corruption.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_026_peaklive_predictable_and_space_efficient_measurement_workspace`
- Architecture decision(s): (none yet)
- Request: `req_027_restore_predictable_panel_geometry_and_reclaim_graph_workspace_space`
- Primary task(s): `task_027_deliver_stable_panel_restoration_and_a_space_efficient_graph_workspace`

# Priority
- Priority: High - unstable restoration disrupts every panel toggle and is the prerequisite for reliable hide/show behaviour.
- Rationale: Set by scaffold input or defaulted for grooming.
