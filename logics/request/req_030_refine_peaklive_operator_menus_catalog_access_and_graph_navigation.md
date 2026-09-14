## req_030_refine_peaklive_operator_menus_catalog_access_and_graph_navigation - Refine PeakLive operator menus, catalog access, and graph navigation
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 95%
> Confidence: 95%
> Complexity: High
> Theme: Operator workspace organization and bounded graph navigation
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-14 16:30:50

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: refine, peaklive, operator, menus, catalog, access, graph, navigation
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Needs
- Move acquisition lifecycle and recording configuration out of View into a dedicated Recording menu without removing the compact header lifecycle controls.
- Move the existing profile save-as behavior, labelled Save measurement setup, from File into Setup, alongside channel, bitrate, and acquisition-mode choices exposed as keyboard-accessible cascading submenus.
- Move DBC activation and management out of Signals into a dedicated DBC menu, while preserving asynchronous catalog mutations and conflict handling.
- Make the Signals panel lead with currently displayed signals and their latest known values.
- Keep graph navigation near acquired data, allowing at most five percent of the acquired time span as intentional blank context beyond either end.
- Give the graph canvas more horizontal area, offer a View choice between full-span and trailing-window Follow live with full-span as the default, regroup fit controls, and make the header Stop control visibly red while acquisition is active.

# Context
- The operator confirmed three new menu-bar menus named Recording, Setup, and DBC. Save measurement setup retains the current profile save-as behavior.
- AcquisitionBar currently owns channel, bitrate, capture-format, and controller-mode combo boxes; capture format is persisted under recording settings, while channel, bitrate, and controller mode are profile settings.
- DBC enablement, removal, and conflict resolution are already asynchronous catalog operations, but DbcLibraryPanel is currently embedded above SignalExplorerPanel in Signals.
- GraphNavigation already distinguishes capture and live global extents, Fit, and Follow live. Its range updates are currently unconstrained after manual pan or zoom.
- The shared graph left-axis allocation is a fixed width and must be reduced only without clipping tick labels or lane identity at supported workspace sizes.
- All operator-visible copy must be localized, all menus must remain keyboard accessible, and existing profile persistence, passive-listen-only safety, replay behavior, DBC conflict semantics, and headless Qt coverage must remain intact.

# Acceptance criteria
- AC1: View contains only view/navigation and panel-visibility commands; Recording contains Start and Stop acquisition plus recording settings, while the compact header lifecycle controls remain available and Stop is visually red only in a stoppable acquisition phase.
- AC2: Recording, Setup, and DBC are new menu-bar menus. Setup contains Save measurement setup with the existing profile save-as behavior and channel, bitrate, and acquisition-mode parent actions whose choices open in right-hand cascading submenus on pointer hover and are equally usable from the keyboard; changing a choice preserves profile persistence and lifecycle safety gates.
- AC3: ASC/TRC format is configured only through Recording settings and no longer consumes top-bar space; the selected format remains profile-scoped and is applied to new recordings only.
- AC4: A DBC top-level menu lists loaded DBCs as independently checkable entries and exposes add, remove, and conflict-management commands; it is the sole workspace control for DBC enablement and management, and Signals no longer renders the DBC library or its per-DBC signal count.
- AC5: Signals begins with a compact displayed-signals summary showing each currently displayed signal's identity, last known value, unit, and an explicit unavailable state before any value has been observed; it stays synchronized with shown-state and DBC changes without changing decode or historical-signal semantics, and refreshes at most once per second.
- AC6: Manual pan and zoom cannot show more than five percent of the acquired time span beyond either edge, with stable behavior for an empty, one-sample, or near-zero-duration session; Fit and Follow live obey the same bound.
- AC7: View offers a Follow live mode choice between Full acquisition span and Trailing window. Full acquisition span is the default and presents t=0 through the newest acquired sample; Trailing window retains the existing short-tail behavior. An explicit manual navigation still disables follow-live and remains bounded by AC6.
- AC8: Graph left-side whitespace is reduced only to the smallest safe shared axis gutter, graph fit controls are regrouped without overlap or clipping, and all graph/lane labels remain legible at 1024x768, 1280x720, and 1600x900.
- AC9: Focused and full headless tests cover menu ownership, submenu selection and persistence, lifecycle gating, DBC mutations/conflicts, displayed-signal values, graph boundary clamping, follow-live extent, responsive geometry, and localized text.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_028_peaklive_focused_operator_controls_and_bounded_measurement_canvas`
- Architecture decision(s): (none yet)

# References
- src/peaklive/ui/actions.py
- src/peaklive/ui/main_window.py
- src/peaklive/ui/panels/acquisition_bar.py
- src/peaklive/ui/panels/dbc_library.py
- src/peaklive/ui/panels/signal_explorer.py
- src/peaklive/ui/panels/graph_navigation.py
- src/peaklive/ui/panels/graph_stack.py
- src/peaklive/ui/dialogs/recording.py
- src/peaklive/ui/catalog_controller.py
- src/peaklive/domain/models.py
- tests/test_ui.py
- tests/test_ui_analyst.py
- tests/test_ui_parity.py
- tests/test_graph_navigation.py

# Backlog
- `item_135_organize_recording_and_setup_commands_around_safe_profile_ownership`
- `item_136_move_dbc_management_to_its_own_menu_and_summarize_displayed_signals`
- `item_137_bound_graph_time_navigation_and_reclaim_safe_graph_canvas_width`
