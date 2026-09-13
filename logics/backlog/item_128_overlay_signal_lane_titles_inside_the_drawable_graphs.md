## item_128_overlay_signal_lane_titles_inside_the_drawable_graphs - Overlay signal lane titles inside the drawable graphs
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: In-plot signal identity
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-13 15:32:01

# AI Context
- Summary: Recover each lane's title-row height with a ViewBox-anchored identity overlay that passes through graph gestures.
- Keywords: overlay, signal, lane, titles, inside, drawable, graphs
- Use when: Changing lane composition, overlay geometry, accessible identity, or title contrast.
- Skip when: Changing curve sampling, signal values, palettes, or Y-axis fitting semantics.

# Problem
- Each lane currently allocates a separate QLabel row above the PlotWidget, consuming height for every shown signal.

# Scope
- In:
  - Replace build_lane's title layout row with a screen-anchored overlay attached to the drawable ViewBox geometry; keep it out of data bounds and autorange calculations.
  - Preserve lane_identity, curve-colour matching, optional units, and intentional full-identity access; retain a subtle separator without a full-width title background.
  - Anchor the overlay after resize/axis layout and keep it fixed during pan/zoom. Use bounded elision and restrained text outline or local translucent backing if needed for contrast.
  - Allow gestures and cursor dragging through the overlay while exposing deliberate detail/accessibility; update existing header-structure expectations to test the new product behaviour.
  - Coordinate with item_112's active delivery: retain its identity/provenance requirements and narrow only title placement.
- Out:
  - Changing signal selection, palette assignments, curve reduction, Y-scale semantics, historical rendering, or adding graph scrollbars.

# Acceptance criteria
- AC1: Titles start 2-6 logical pixels inside the top-left of each ViewBox, right of Y ticks, and no title widget contributes vertical layout height or autorange padding.
- AC2: At the same window size and lane count, plot area gains the removed title-row height; 1, 3, and 8 lanes retain aligned X origins, legible Y ticks, one bottom time axis, and no added scrolling.
- AC3: Long/duplicate names, units, and raw preview remain identifiable with complete accessible details; technical hashes stay absent from ambient graph hover.
- AC4: Pan, wheel zoom, fit, follow-live, and A/B drag initiated under the title still work; title anchoring survives these interactions, resize, and lane rebuilds.

# AC Traceability
- request-AC5 -> This backlog slice. Proof: AC1: Titles start 2-6 logical pixels inside the top-left of each ViewBox, right of Y ticks, and no title widget contributes vertical layout height or autorange padding.
- request-AC6 -> This backlog slice. Proof: AC2: At the same window size and lane count, plot area gains the removed title-row height; 1, 3, and 8 lanes retain aligned X origins, legible Y ticks, one bottom time axis, and no added scrolling.
- request-AC9 -> This backlog slice. Proof: AC3: Long/duplicate names, units, and raw preview remain identifiable with complete accessible details; technical hashes stay absent from ambient graph hover.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_026_peaklive_predictable_and_space_efficient_measurement_workspace`
- Architecture decision(s): (none yet)
- Request: `req_027_restore_predictable_panel_geometry_and_reclaim_graph_workspace_space`
- Primary task(s): `task_027_deliver_stable_panel_restoration_and_a_space_efficient_graph_workspace`

# Priority
- Priority: Medium - removing repeated title bands increases plot height while preserving the existing lane identity contract.
- Rationale: Set by scaffold input or defaulted for grooming.
