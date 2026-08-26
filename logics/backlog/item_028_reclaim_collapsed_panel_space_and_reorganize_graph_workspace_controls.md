## item_028_reclaim_collapsed_panel_space_and_reorganize_graph_workspace_controls - Reclaim collapsed panel space and reorganize graph workspace controls
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Responsive workspace layout
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-26 16:07:29

# AI Context
- Summary: Make side-panel collapse genuinely release splitter space and arrange graph controls around readable responsive measurement work.
- Keywords: reclaim, collapsed, panel, space, reorganize, graph, workspace, controls
- Use when: A collapsed side panel still occupies workspace width or graph controls and data compete for the same limited area.
- Skip when: The work requires docking, a multi-window architecture, or new graph-analysis behavior.

# Problem
- Signals and Inspector show a minus button, but collapsing hides only their bodies while the horizontal splitter continues reserving the same empty columns.
- The graph option row is visually crowded and poorly grouped, while the graph/trace/report layout does not sufficiently prioritize the active graph workspace.

# Scope
- In:
  - Define and implement a compact collapsed-side-panel state that releases splitter width, preserves panel identity, and provides an obvious plus-style expand action.
  - Choose one documented collapse interaction: a fully collapsed edge rail restored from its expand control, or a narrow vertical-title rail that can be expanded. The chosen interaction must be applied consistently to Signals and Inspector.
  - Remember usable expanded widths and restore them on expansion, while keeping the profile layout persistence contract valid.
  - Reorganize graph controls into visually coherent groups for view navigation, display options, cursor placement, and readouts.
  - Make the graph-control layout wrap, compact, or adapt intentionally rather than overlap or clip at supported bench resolutions.
  - Adjust graph, trace, and report splitter defaults and minimum sizes so the active workspace retains a useful graph area and all sections remain resizable.
  - Preserve existing collapse shortcuts, A/B cursor behavior, follow-live behavior, trace selection, report availability, and splitter persistence.
- Out:
  - Detachable floating panels, multiple windows, or a docking-framework migration.
  - New graph analysis features or changes to cursor/statistics semantics.
  - Removing trace or report functionality from the workspace.

# Acceptance criteria
- AC1: Collapsing Signals or Inspector visibly reduces its horizontal allocation and gives the center workspace the released area.
- AC2: The collapsed state remains discoverable, exposes the panel identity plus a clear expand affordance, and restores the panel content without losing state.
- AC3: Expanded width and collapsed state persist per profile; an invalid or unavailable stored size falls back to a safe usable default.
- AC4: Graph controls are grouped and aligned by purpose, and their labels/readouts remain visible without overlap or clipping at 1024x768, 1280x720, and 1600x900.
- AC5: The default graph/trace/report arrangement provides a usable graph area, supports splitter resizing, and preserves user adjustments across profile reload.
- AC6: Keyboard panel-collapse and graph-navigation behavior remains functional after the layout change.
- AC7: Headless UI tests cover space reclamation, expand/restore behavior, persistence, supported-resolution geometry constraints, and graph-control visibility.

# AC Traceability
- request-AC4 -> This backlog slice. Proof: AC1: Collapsing Signals or Inspector visibly reduces its horizontal allocation and gives the center workspace the released area.
- request-AC5 -> This backlog slice. Proof: AC2: The collapsed state remains discoverable, exposes the panel identity plus a clear expand affordance, and restores the panel content without losing state.
- request-AC6 -> This backlog slice. Proof: AC3: Expanded width and collapsed state persist per profile; an invalid or unavailable stored size falls back to a safe usable default.
- request-AC7 -> This backlog slice. Proof: AC4: Graph controls are grouped and aligned by purpose, and their labels/readouts remain visible without overlap or clipping at 1024x768, 1280x720, and 1600x900.
- request-AC8 -> This backlog slice. Proof: AC5: The default graph/trace/report arrangement provides a usable graph area, supports splitter resizing, and preserves user adjustments across profile reload.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_004_peaklive_dense_and_legible_diagnostic_workspace`
- Architecture decision(s): (none yet)
- Request: `req_003_improve_peaklive_workspace_visual_usability_and_panel_density`
- Primary task(s): `task_004_deliver_the_peaklive_visual_usability_and_responsive_workspace_refinement`

# Priority
- Priority: High - the current collapse controls do not create usable workspace area, and graph controls compete with the data they should support.
- Rationale: Set by scaffold input or defaulted for grooming.
