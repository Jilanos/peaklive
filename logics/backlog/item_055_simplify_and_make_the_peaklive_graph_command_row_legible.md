## item_055_simplify_and_make_the_peaklive_graph_command_row_legible - Simplify and make the PeakLive graph command row legible
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Graph header density and cursor readouts
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: simplify, peaklive, graph, command, row, legible
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- The + and - zoom buttons, grid toggle, and window readout consume scarce header width while the B cursor time clips.
- The fit/resize glyphs are too small to be recognized reliably inside their buttons.
- Follow live is not guaranteed to sit with the primary graph commands after responsive layout pressure.

# Scope
- In:
  - Remove visible and focusable zoom-in, zoom-out, grid, and window/no-sample readout controls and their misleading tooltips/shortcuts.
  - Retain and enlarge the fit-all and fit-Y glyphs while preserving their semantics, accessibility, and keyboard operation.
  - Lay out Follow live alongside the remaining graph commands in one non-wrapping graph header row.
  - Allocate header width so complete A and B cursor times display together at all supported viewports; retain cursor placement and measurement behavior.
  - Add rendering and interaction regressions for removal, geometry, complete cursor readouts, and retained navigation behavior.
- Out:
  - Changing sample storage, cursor calculation, export scope, or data acquisition lifecycle.
  - Removing wheel/pan navigation or fit actions.
  - Introducing a second graph toolbar or a wrapping layout.

# Acceptance criteria
- AC2: The graph command row has no + zoom button, - zoom button, or grid control. The remaining fit-all and fit-Y/resize glyphs are visually larger and centered in their buttons, Follow live is on the same horizontal row as these commands, and all remaining actions retain accessible names, tooltips, keyboard reachability, and working behavior.
- AC3: At 1024x768, 1280x720, and 1600x900, both complete A and B cursor timestamps are visible together in the graph header without clipping, overlap, wrapping, or tooltip-only fallback. The graph header shows neither start/end-second window text, delta/zoom window text, nor the No sample yet placeholder.
- AC4: The graph no longer exposes the removed zoom buttons, grid toggle, or window readout through visible UI, keyboard shortcuts, inaccessible focus targets, or misleading tooltips. Existing pan/scroll navigation, fit actions, cursor placement, Follow live, and measurement calculations remain intact.
- AC7: Focused offscreen/rendered UI regression tests prove combo trigger contrast, removed-control absence, enlarged fit glyph geometry, one-row containment, simultaneous complete A/B timestamps, absent window/no-sample text, Follow live placement, eye/star state contrast, and preserved graph/signal workflows.

# AC Traceability
- request-AC2 -> This backlog slice. Proof: AC2: The graph command row has no + zoom button, - zoom button, or grid control. The remaining fit-all and fit-Y/resize glyphs are visually larger and centered in their buttons, Follow live is on the same horizontal row as these commands, and all remaining actions retain accessible names, tooltips, keyboard reachability, and working behavior.
- request-AC3 -> This backlog slice. Proof: AC3: At 1024x768, 1280x720, and 1600x900, both complete A and B cursor timestamps are visible together in the graph header without clipping, overlap, wrapping, or tooltip-only fallback. The graph header shows neither start/end-second window text, delta/zoom window text, nor the No sample yet placeholder.
- request-AC4 -> This backlog slice. Proof: AC4: The graph no longer exposes the removed zoom buttons, grid toggle, or window readout through visible UI, keyboard shortcuts, inaccessible focus targets, or misleading tooltips. Existing pan/scroll navigation, fit actions, cursor placement, Follow live, and measurement calculations remain intact.
- request-AC7 -> This backlog slice. Proof: AC7: Focused offscreen/rendered UI regression tests prove combo trigger contrast, removed-control absence, enlarged fit glyph geometry, one-row containment, simultaneous complete A/B timestamps, absent window/no-sample text, Follow live placement, eye/star state contrast, and preserved graph/signal workflows.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_016_peaklive_compact_graph_controls_and_unmistakable_signal_states`
- Architecture decision(s): (none yet)
- Request: `req_016_compact_peaklive_graph_controls_and_unmistakable_signal_states`
- Primary task(s): `task_017_implement_compact_graph_controls_and_unmistakable_signal_states`

# Priority
- Priority: High - graph navigation and A/B comparison are core diagnostic actions; clipped cursor times and redundant controls directly obstruct their use.
- Rationale: Set by scaffold input or defaulted for grooming.
