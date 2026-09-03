## req_016_compact_peaklive_graph_controls_and_unmistakable_signal_states - Compact PeakLive graph controls and unmistakable signal states
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 95%
> Confidence: 90%
> Complexity: Medium
> Theme: Compact graph controls and signal-state clarity
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 00:32:08

# AI Context
- Summary: Compact the graph command row and make combo drop-downs and signal eye/favorite states unmistakable in the dark theme, without touching acquisition, decoding, or persistence semantics.
- Keywords: compact, peaklive, graph, controls, unmistakable, signal, states
- Use when: Scoping or reviewing the compact-controls and signal-state-clarity delivery.
- Skip when: The change is unrelated to graph header controls, combo styling, or eye/favorite state rendering.

# Needs
- Replace the unexplained white rectangle at the right of every application drop-down, including channel, measurement profile, Graphs only, and Trace only, with a clear dark-theme drop-down affordance.
- Simplify the graph command row: remove the + and - zoom buttons and the grid control, make the two fit/resize icons visibly larger in their buttons, and keep Follow live on that same row beside the remaining graph commands.
- Show complete A and B cursor times simultaneously; reclaim the needed width by removing the graph window readout, including its start/end seconds, delta/zoom information, and No sample yet state.
- Keep the unselected favorite star icon unchanged, but render the selected favorite in a notably brighter yellow. Make selected versus unselected states of both the visibility eye and favorite star immediately distinguishable.
- Preserve all CAN acquisition, decoding, cursor placement, graph data, follow-live behavior, signal filtering, favorite persistence, accessibility, and keyboard interaction semantics not explicitly removed.

# Context
- GraphControlsBar currently renders zoom-in (+), zoom-out (-), fit-all (⤢), fit-Y (↕), a window/no-sample readout, grid, Follow live, A/B actions, and a cursor summary in compact groups. The window readout is populated by GraphNavigation._refresh_window_label().
- The graph controls must remain a single non-wrapping row at supported desktop viewports. The existing user request explicitly trades the window readout and grid toggle for room to display both cursor timestamps and retain Follow live inline.
- All application QComboBox instances share the dark-theme QSS. Its current down-arrow implementation can render as a confusing white rectangular target on the supported desktop style, so the replacement must be verified from rendered widgets rather than stylesheet text alone.
- SignalExplorerPanel paints shown and favorite state through RowActionDelegate. The current active colour is shared cyan and inactive icons use a muted grey-blue; favorite selection requires a brighter yellow while the inactive star's current appearance remains unchanged.
- 'Eye of fav' is interpreted as the eye and favorite controls: both must have a stronger checked/unchecked distinction. This is recorded as an implementation assumption because no alternate control is present in the Signals tree.

# Acceptance criteria
- AC1: At each application combo box, including channel, measurement profile, Graphs only, and Trace only, the right-side trigger is a recognizable high-contrast drop-down symbol with coherent normal, hover, focus, disabled, and popup states; no unexplained white rectangle is visible on the supported desktop platform.
- AC2: The graph command row has no + zoom button, - zoom button, or grid control. The remaining fit-all and fit-Y/resize glyphs are visually larger and centered in their buttons, Follow live is on the same horizontal row as these commands, and all remaining actions retain accessible names, tooltips, keyboard reachability, and working behavior.
- AC3: At 1024x768, 1280x720, and 1600x900, both complete A and B cursor timestamps are visible together in the graph header without clipping, overlap, wrapping, or tooltip-only fallback. The graph header shows neither start/end-second window text, delta/zoom window text, nor the No sample yet placeholder.
- AC4: The graph no longer exposes the removed zoom buttons, grid toggle, or window readout through visible UI, keyboard shortcuts, inaccessible focus targets, or misleading tooltips. Existing pan/scroll navigation, fit actions, cursor placement, Follow live, and measurement calculations remain intact.
- AC5: An unselected favorite star keeps its current muted visual treatment. A selected favorite star is filled or otherwise selected in a bright, saturated yellow with materially higher contrast. The shown/hidden eye likewise has a clearly stronger checked/unchecked distinction through shape fill, colour, and/or contrast, without relying on colour alone.
- AC6: Eye and favorite actions keep their current click, keyboard, tooltip, accessible-name/state, filtering, and profile-persistence behavior; their state remains unambiguous in normal, hover, focus, and disabled rendering.
- AC7: Focused offscreen/rendered UI regression tests prove combo trigger contrast, removed-control absence, enlarged fit glyph geometry, one-row containment, simultaneous complete A/B timestamps, absent window/no-sample text, Follow live placement, eye/star state contrast, and preserved graph/signal workflows.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_016_peaklive_compact_graph_controls_and_unmistakable_signal_states`
- Architecture decision(s): (none yet)

# References
- src/peaklive/ui/panels/graph_controls.py
- src/peaklive/ui/panels/graph_navigation.py
- src/peaklive/ui/panels/signal_explorer.py
- src/peaklive/ui/panels/signal_row_icons.py
- src/peaklive/ui/theme.py
- src/peaklive/i18n/en.json
- tests/test_ui_workspace_refinement.py
- tests/test_ui_signal_affordances.py
- tests/test_graph_navigation.py

# Backlog
- `item_055_simplify_and_make_the_peaklive_graph_command_row_legible`
- `item_056_make_peaklive_selector_triggers_and_signal_eye_star_states_unmistakable`
