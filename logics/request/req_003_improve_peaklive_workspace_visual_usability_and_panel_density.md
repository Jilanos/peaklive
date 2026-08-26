## req_003_improve_peaklive_workspace_visual_usability_and_panel_density - Improve PeakLive workspace visual usability and panel density
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Desktop workspace visual usability
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-08-26 16:07:29

# AI Context
- Summary: Refine the existing native workspace so signal selection, dark-theme controls, collapsible side panels, and graph composition serve focused live analysis.
- Keywords: improve, peaklive, workspace, visual, usability, panel, density
- Use when: An analyst cannot clearly see or efficiently operate selection, navigation, or measurement controls in the existing desktop workspace.
- Skip when: The work changes CAN decoding, acquisition, or analytical semantics rather than the usability of their existing controls.

# Needs
- Make the signal explorer prioritize the signal name and direct actions, rather than devoting a large share of each row to repeated shown and favorite labels.
- Make every interactive control legible in the dark instrument theme, including unchecked checkboxes and expanded combo-box menus.
- Make collapsing Signals and Inspector reclaim workspace area, with a discoverable compact state and restoration behavior.
- Make graph controls and the graph/trace composition read as an intentional measurement workspace instead of a collection of poorly aligned options.

# Context
- PeakLive is a native PySide6 CAN-analysis desktop application with a three-column workspace: Signals, Graphs and Trace, and Inspector.
- The Signals panel combines independently enabled DBCs with the signal explorer. DBC enablement is already available in the DBC library, so its control must remain visible and must not be duplicated in signal rows.
- SignalExplorerPanel currently renders a three-column tree: signal name, shown, and fav. Each signal row repeats the literal labels shown and fav beside a checkbox, reducing the available width for the signal name.
- The shared dark stylesheet styles closed QComboBox controls but has no explicit popup-view rules and no explicit unchecked-checkbox indicator rules, making some controls nearly unreadable on a dark background.
- CollapsiblePanel hides its body but remains a child of a horizontal QSplitter with its previous allocation. A collapsed Signals or Inspector panel therefore leaves an empty reserved column.
- GraphStackPanel exposes zoom, grid, follow-live, cursor, window, and cursor-summary controls in one horizontal row above a vertically stacked graph area. The workspace also uses a vertical splitter for graphs, trace, and report.
- The redesign must preserve existing DBC conflict behavior, shown-signal plots, favorite persistence, keyboard access, profile layout persistence, and headless Qt testability.

# Acceptance criteria
- AC1: The signal explorer presents each signal name as the dominant, readable row content, while shown and favorite actions remain direct, compact, independently operable, and accessible without repeated text labels in every row.
- AC2: DBC activation remains a separate, discoverable control in the DBC library; this request neither duplicates it in signal rows nor changes enabled-DBC decode semantics.
- AC3: In the dark theme, unchecked and checked checkboxes, combo-box field text, popup-menu text, popup selection, disabled items, and hover/focus states meet readable foreground/background contrast and remain usable with keyboard navigation.
- AC4: Collapsing Signals or Inspector releases its meaningful horizontal workspace allocation. The compact state exposes the panel identity and an obvious expand action, and restoring it returns its content and a sensible remembered or default width.
- AC5: Graph navigation and measurement controls are grouped, aligned, and responsive at 1024x768, 1280x720, and 1600x900; labels and state readouts do not overlap, clip, or force the graphs into an unusable area.
- AC6: The graph, trace, and report arrangement gives the active graph workspace priority while retaining predictable splitter-based resizing and persisted layout behavior.
- AC7: Existing behavior for shown signals, favorites, DBC enabling, profile persistence, graph navigation, A/B cursors, trace selection, and keyboard operation remains covered by headless offscreen regression tests.
- AC8: All new or changed user-visible text is routed through the i18n layer, and no transmit, protocol, acquisition, or decoding behavior is introduced or changed.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_004_peaklive_dense_and_legible_diagnostic_workspace`
- Architecture decision(s): (none yet)

# References
- README.md
- docs/product-scope.md
- src/peaklive/ui/main_window.py
- src/peaklive/ui/theme.py
- src/peaklive/ui/widgets.py
- src/peaklive/ui/panels/signal_explorer.py
- src/peaklive/ui/panels/graph_stack.py
- src/peaklive/ui/panels/dbc_library.py
- tests/test_ui.py
- tests/test_ui_analyst.py

# Backlog
- `item_026_make_signal_selection_compact_name_first_and_state_legible`
- `item_027_restore_full_dark_theme_control_and_menu_legibility`
- `item_028_reclaim_collapsed_panel_space_and_reorganize_graph_workspace_controls`
