## item_024_deliver_keyboard_accessibility_menus_and_layout_persistence - Deliver keyboard accessibility, menus, and layout persistence
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Workspace ergonomics
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-25 12:29:44

# AI Context
- Summary: Makes the workspace operable without a mouse and stable on bench screens: shortcuts for acquisition, views, cursors, fit and fullscreen; tooltips and accessible names on every control; complete tab order; a File/View/Help menu bar; a resizable graph/trace divider; persisted geometry; and verified layout at 1024x768, 1280x720 and 1600x900.
- Keywords: shortcuts, tooltips, accessible names, tab order, menu bar, fullscreen, splitter persistence, viewports
- Use when: Adding shortcuts, tooltips, accessible names or tab order, building the menu bar or fullscreen mode, or persisting and restoring splitter and collapse geometry.
- Skip when: User-remappable keybindings, formal screen-reader certification, and touch or mobile layouts.

# Problem
- The main window contains no shortcut and no tooltip, so every action requires a mouse and no control explains itself.
- Splitter sizes are hard-coded and never persisted, there is no menu bar, no fullscreen mode, no resizable divider between graphs and trace, and no verified behavior at bench screen sizes.

# Scope
- In:
  - Add shortcuts for start and stop acquisition, view switching, panel collapse, cursor A and B placement, fit view, filter focus, and fullscreen.
  - Add a tooltip and an accessible name to every actionable control.
  - Ensure tab order reaches the DBC library, signal explorer, filter fields, trace rows, measurement table, and every dialog, and that dialogs are fully keyboard-operable.
  - Add a menu bar with File, View, and Help covering the top-bar actions plus an About entry.
  - Add a fullscreen mode and a resizable divider between the graph stack and the trace view.
  - Persist splitter geometry, divider position, and collapse state per profile.
  - Declare a minimum window size and verify the layout at 1024x768, 1280x720, and 1600x900.
  - Publish the shortcut list in the repository documentation.
- Out:
  - Fully user-remappable keybindings.
  - Screen-reader certification against a formal accessibility standard.
  - Touch or mobile layouts.

# Acceptance criteria
- AC1: Every listed shortcut is bound and performs its action.
- AC2: Every actionable control exposes a tooltip and an accessible name.
- AC3: Tab order reaches each listed region and every dialog can be completed and dismissed from the keyboard.
- AC4: The menu bar exposes the top-bar actions plus About, and fullscreen can be entered and left.
- AC5: Splitter geometry, divider position, and collapse state persist across an application restart on the same profile.
- AC6: The layout stays usable at 1024x768, 1280x720, and 1600x900, with no control clipped below the declared minimum size.
- AC7: The shortcut list is documented in the repository.
- AC8: Headless offscreen tests cover shortcuts, tab order, menu actions, persistence, and the three viewport sizes.

# AC Traceability
- request-AC9 -> This backlog slice. Proof: AC1: Every listed shortcut is bound and performs its action.
- request-AC10 -> This backlog slice. Proof: AC2: Every actionable control exposes a tooltip and an accessible name.
- request-AC12 -> This backlog slice. Proof: AC3: Tab order reaches each listed region and every dialog can be completed and dismissed from the keyboard.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_003_peaklive_analyst_measurement_and_reporting_workspace`
- Architecture decision(s): (none yet)
- Request: `req_002_complete_the_peaklive_analyst_workspace_to_cantracediag_parity`
- Primary task(s): `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Priority
- Priority: Medium - bench use is keyboard-driven and the current layout is neither persisted nor size-verified.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Notes
- Task `task_003_deliver_the_peaklive_analyst_workspace_parity_wave` was finished via `logics-manager flow finish task` on 2026-08-25.
