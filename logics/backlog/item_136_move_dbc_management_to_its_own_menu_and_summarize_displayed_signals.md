## item_136_move_dbc_management_to_its_own_menu_and_summarize_displayed_signals - Move DBC management to its own menu and summarize displayed signals
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 95%
> Confidence: 95%
> Progress: 100%
> Complexity: High
> Theme: DBC catalog and signal observability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-14 16:30:50

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: move, dbc, management, own, menu, summarize, displayed, signals
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Signals currently spends its top region on a DBC library, mixing catalog ownership with per-signal exploration and reducing room for signal state.
- An operator cannot scan the currently displayed signals and their latest values without reading individual graph lanes or searching the tree.

# Scope
- In:
  - Create a DBC top-level menu beside View that lists each loaded definition as a checkable action and contains explicit add, remove, and conflict-management entry points.
  - Reuse DbcCatalogWorker and WorkspaceCatalog asynchronous operations; menu state must remain correct while an add, remove, enable, disable, or conflict-resolution operation is pending or fails.
  - Remove DbcLibraryPanel from Signals and avoid duplicating DBC enable/disable, remove, conflict, or count controls elsewhere in that panel.
  - Add a compact displayed-signals section at the top of Signals, ordered deterministically, showing display name/qualified identity, last value, unit, and unavailable/stale state without requiring a graph redraw per frame; coalesce updates to at most one refresh per second.
  - Synchronize this summary with shown/favorite changes, DBC enable/disable/remove, session reset, replay, live acquisition, and profile restoration while retaining raw preview behavior when no decoded signal is shown.
  - Preserve conflict diagnostics and all existing selected-signal provenance rules.
- Out:
  - Changing DBC conflict precedence, parser behavior, DBC file storage, or asynchronous worker architecture.
  - Adding signal alarms, numeric editing, or a second source of truth for series values.
  - Replacing the full signal explorer tree.

# Acceptance criteria
- AC1: The DBC menu presents every loaded DBC with a checked/unchecked activation state and provides add, remove, and conflict-management paths without embedding DBC controls in Signals.
- AC2: Menu-driven enable, disable, remove, and conflict resolution preserve the current async catalog operation, profile persistence, selected-signal reconciliation, and failure-notification behavior.
- AC3: Signals displays every currently shown decoded signal with its most recent value and unit, marks an unobserved value explicitly, removes or updates entries on catalog and shown-state changes, and refreshes at most once per second.
- AC4: The summary does not invent values, alter retained series/history samples, reorder source data, or prevent use of raw preview when no decoded signal is shown.
- AC5: Tests cover multiple DBCs, conflict state, pending mutations, session reset, replay/live updates, persistence, and accessible menu/summary labels.

# AC Traceability
- request-AC4 -> This backlog slice. Proof: AC1: The DBC menu presents every loaded DBC with a checked/unchecked activation state and provides add, remove, and conflict-management paths without embedding DBC controls in Signals.
- request-AC5 -> This backlog slice. Proof: AC3: Signals displays every currently shown decoded signal with its most recent value and unit, marks an unobserved value explicitly, removes or updates entries on catalog and shown-state changes, and refreshes at most once per second.
- request-AC9 -> This backlog slice. Proof: AC5: Tests cover multiple DBCs, conflict state, pending mutations, session reset, replay/live updates, persistence, and accessible menu/summary labels.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_028_peaklive_focused_operator_controls_and_bounded_measurement_canvas`
- Architecture decision(s): (none yet)
- Request: `req_030_refine_peaklive_operator_menus_catalog_access_and_graph_navigation`
- Primary task(s): `task_029_deliver_peaklive_operator_menu_catalog_and_graph_canvas_refinement`

# Priority
- Priority: High - catalog state and live signal state need separate, immediately discoverable homes.
- Rationale: Set by scaffold input or defaulted for grooming.

# Validation
- Wave 2 implemented: DBC library panel removed from Signals; a new top-level DBC menu (menu_dbc) lists every loaded DBC as a checkable action mirroring WorkspaceCatalog's async enable/disable/remove/conflict-resolution operations, with Add/Remove/Conflicts entry points and the whole menu disabled while an operation is pending. A new SignalSummaryPanel leads Signals with currently shown signals, their latest value and unit, refreshed at most once/second (immediate first refresh, coalesced afterward) via WorkspaceSignalSummary. DBC load/decode failures now route to the shared session_note. Evidence: full pytest suite green (no regressions), new tests/test_signal_summary.py added, ruff clean, logics-manager lint/audit clean (no new blocking issues).

# Tasks
- `task_029_deliver_peaklive_operator_menu_catalog_and_graph_canvas_refinement`

# Notes
- Task `task_029_deliver_peaklive_operator_menu_catalog_and_graph_canvas_refinement` was finished via `logics-manager flow finish task` on 2026-09-14.
