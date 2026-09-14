## item_137_bound_graph_time_navigation_and_reclaim_safe_graph_canvas_width - Bound graph time navigation and reclaim safe graph canvas width
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 95%
> Confidence: 95%
> Progress: 0%
> Complexity: High
> Theme: Graph navigation and density
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: bound, graph, time, navigation, reclaim, safe, canvas, width
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Manual graph pan and zoom may travel beyond the time that was acquired, leaving an unhelpful blank canvas.
- The operator wants View to offer both full-acquisition-span and existing trailing-window Follow live modes, with full acquisition span from zero through the newest frame as the default; graph controls and a fixed left gutter compete with drawable width.

# Scope
- In:
  - Define one shared X-range clamp used by wheel zoom, pan, Fit, Follow live, programmatic range synchronization, replay, and live acquisition.
  - Allow at most five percent of the acquired span beyond each data edge; define an explicit finite minimum-padding rule for empty, one-sample, and near-zero spans without NaN, jitter, or recursive range signals.
  - Add a View submenu for Follow live mode: Full acquisition span is the default and uses the live global extent from t=0 to newest sample, while Trailing window retains the existing short-tail behavior. Persist the selected profile preference; manual navigation disables follow-live but never escapes the clamp.
  - Reorder/group Fit, Fit Y, zoom, and Follow live controls according to navigation intent while preserving keyboard shortcuts and A/B cursor controls.
  - Replace the fixed excess left gutter with a measured shared axis width derived from required labels plus minimal padding; preserve lane-title and axis-label legibility at supported viewports.
  - Cover headless geometry and navigation contracts across capture/replay/live sessions and multi-lane graphs.
- Out:
  - Changing Y-axis autoscaling semantics, raw/history sampling, graph downsampling, or historical viewport scheduling.
  - Changing capture timestamps, changing the existing trailing-window duration, or hiding valid data to gain space.
  - Relaxing the existing responsive-layout acceptance owned by active workspace work.

# Acceptance criteria
- AC1: Every graph X-range path is clamped to the data extent plus no more than five percent of that extent at either side, including user pan/zoom, Fit, Follow live, capture completion, and plot synchronization.
- AC2: Empty, one-sample, and sub-millisecond extents remain finite and stable, and no manual operation causes repeated range-change recursion or an invalid view range.
- AC3: View offers Full acquisition span and Trailing window Follow live modes. Full acquisition span is the default and presents [0, newest timestamp] subject only to documented small edge padding; Trailing window retains the existing duration; manually zooming or panning disables follow-live without breaking bounds.
- AC4: Fit-related controls have a documented compact order and retain their current shortcuts, accessible names, and cursor/measurement behavior.
- AC5: The graph canvas gains width from a smaller safe left gutter, while vertical tick labels, lane labels, controls, and graphs remain visible and non-overlapping at supported viewport sizes.
- AC6: Tests assert the numerical clamp, follow-live extent, edge cases, control order, and minimum geometry rather than relying solely on screenshots.

# AC Traceability
- request-AC6 -> This backlog slice. Proof: AC1: Every graph X-range path is clamped to the data extent plus no more than five percent of that extent at either side, including user pan/zoom, Fit, Follow live, capture completion, and plot synchronization.
- request-AC7 -> This backlog slice. Proof: AC3: View offers Full acquisition span and Trailing window Follow live modes. Full acquisition span is the default and presents [0, newest timestamp] subject only to documented small edge padding; Trailing window retains the existing duration; manually zooming or panning disables follow-live without breaking bounds.
- request-AC8 -> This backlog slice. Proof: AC5: The graph canvas gains width from a smaller safe left gutter, while vertical tick labels, lane labels, controls, and graphs remain visible and non-overlapping at supported viewport sizes.
- request-AC9 -> This backlog slice. Proof: AC6: Tests assert the numerical clamp, follow-live extent, edge cases, control order, and minimum geometry rather than relying solely on screenshots.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_028_peaklive_focused_operator_controls_and_bounded_measurement_canvas`
- Architecture decision(s): (none yet)
- Request: `req_030_refine_peaklive_operator_menus_catalog_access_and_graph_navigation`
- Primary task(s): `task_029_deliver_peaklive_operator_menu_catalog_and_graph_canvas_refinement`

# Priority
- Priority: High - unconstrained graph navigation wastes analyst attention and the current gutter/control layout reduces the drawable measurement area.
- Rationale: Set by scaffold input or defaulted for grooming.
