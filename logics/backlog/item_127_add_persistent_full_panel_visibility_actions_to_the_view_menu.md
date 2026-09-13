## item_127_add_persistent_full_panel_visibility_actions_to_the_view_menu - Add persistent full-panel visibility actions to the View menu
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 50%
> Complexity: Medium
> Theme: Workspace panel visibility
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-13 15:34:34

# AI Context
- Summary: Add profile-backed visibility independent of collapse, including complete rail removal and menu recovery from all-hidden state.
- Keywords: add, persistent, full, panel, visibility, actions, view, menu
- Use when: Implementing View actions, hide/show transitions, keyboard reveal, or legacy profile defaults.
- Skip when: Changing per-signal selection or the workspace mode system.

# Problem
- Collapse leaves a labelled rail; there is no menu command to reclaim that last strip while retaining reliable recovery and panel state.

# Scope
- In:
  - Depends on the geometry slice. Add three checkable View actions in actions.py backed by explicit per-profile visibility, independent of collapsed_panels.
  - Treat Graphs/Trace as the central container including its Report mode; do not turn the new visibility action into a mode selector or per-signal toggle.
  - Make hide/show work for both expanded and collapsed panels, synchronize checkmarks after profile changes, and restore hidden panels from the always-reachable top menu even when all are hidden.
  - Preserve hidden panel contents and active acquisition. Existing F5/F6 and top-menu Start/Stop remain usable with the center hidden. Ctrl+B remains collapse/expand when Signals is visible and reveals then expands Signals when hidden; explicit reveal shortcuts update the menu checkmark.
  - Use translated action labels and accessible names, and add backwards-compatible model round-trip/default tests.
- Out:
  - Changing default visible panels in existing profiles, floating docks, and suspending capture when a panel is hidden.

# Acceptance criteria
- AC1: Each checkable action removes/restores the complete corresponding panel and rail, with no residual unused handle gutter, and reflects explicit state rather than parent/window isVisible timing.
- AC2: Visible-expanded, visible-collapsed, hidden-from-expanded, and hidden-from-collapsed transitions restore the appropriate geometry and collapse state; all-hidden recovery and keyboard reveal work.
- AC3: Old profiles load with all panels visible, new visibility survives save/restart/profile switching, and unrelated profile fields remain unchanged.
- AC4: Hiding and showing does not reset selected signals, X range, A/B, measurement visibility, workspace mode, or Inspector state; acquisition Start/Stop remains available and correct.

# AC Traceability
- request-AC2 -> This backlog slice. Proof: AC1: Each checkable action removes/restores the complete corresponding panel and rail, with no residual unused handle gutter, and reflects explicit state rather than parent/window isVisible timing.
- request-AC3 -> This backlog slice. Proof: AC2: Visible-expanded, visible-collapsed, hidden-from-expanded, and hidden-from-collapsed transitions restore the appropriate geometry and collapse state; all-hidden recovery and keyboard reveal work.
- request-AC4 -> This backlog slice. Proof: AC3: Old profiles load with all panels visible, new visibility survives save/restart/profile switching, and unrelated profile fields remain unchanged.
- request-AC9 -> This backlog slice. Proof: AC4: Hiding and showing does not reset selected signals, X range, A/B, measurement visibility, workspace mode, or Inspector state; acquisition Start/Stop remains available and correct.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_026_peaklive_predictable_and_space_efficient_measurement_workspace`
- Architecture decision(s): (none yet)
- Request: `req_027_restore_predictable_panel_geometry_and_reclaim_graph_workspace_space`
- Primary task(s): `task_027_deliver_stable_panel_restoration_and_a_space_efficient_graph_workspace`

# Priority
- Priority: High - hiding the unused Inspector rail directly recovers graph width and builds on the geometry correction.
- Rationale: Set by scaffold input or defaulted for grooming.
