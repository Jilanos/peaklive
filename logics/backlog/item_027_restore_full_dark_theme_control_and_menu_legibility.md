## item_027_restore_full_dark_theme_control_and_menu_legibility - Restore full dark-theme control and menu legibility
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 10%
> Complexity: Medium
> Theme: Dark theme accessibility
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-26 16:24:36

# AI Context
- Summary: Establish explicit dark-theme foreground, background, indicator, and focus states for all interactive Qt controls.
- Keywords: restore, full, dark, theme, control, menu, legibility
- Use when: A selector, popup, menu, checkbox, or keyboard focus state lacks sufficient contrast in the dark workspace.
- Skip when: The requested work is a new theme, a visual rebrand, or a behavioral change to the controlled feature.

# Problem
- With the dark workspace background, text in several expanded drop-down menus is rendered dark on dark and is nearly invisible.
- The current stylesheet declares colors for closed selector controls but does not comprehensively style popup views, menu item states, or checkbox indicators.

# Scope
- In:
  - Audit all Qt controls used by the workspace and dialogs for dark-surface foreground/background contrast.
  - Add explicit stylesheet rules for QComboBox popup views and items, QMenu items, QAbstractItemView selection and disabled states, checkbox indicators, focus states, and hover states.
  - Use shared theme tokens rather than panel-local color literals.
  - Verify keyboard focus and selected-item states visually and through widget properties in headless tests.
  - Keep the existing instrument palette and semantic error, warning, running, and disabled states coherent.
- Out:
  - A new light theme or OS-specific theme switcher.
  - Changing business behavior of selectors, menus, dialogs, or acquisition settings.
  - Pixel-perfect matching to an external product.

# Acceptance criteria
- AC1: Every expanded combo-box and menu used by the main workspace and its dialogs renders readable normal, selected, hover, focus, and disabled text on a contrasting background.
- AC2: Unchecked and checked checkboxes are visibly distinct on every dark workspace surface.
- AC3: Keyboard navigation makes the focused and selected item unambiguous without relying on color alone.
- AC4: Theme colors are defined through shared tokens and do not introduce arbitrary panel-local palette values.
- AC5: Offscreen UI tests instantiate representative menus, combo boxes, and checkboxes and assert the stylesheet/state hooks that guard the regression.

# AC Traceability
- request-AC3 -> This backlog slice. Proof: AC1: Every expanded combo-box and menu used by the main workspace and its dialogs renders readable normal, selected, hover, focus, and disabled text on a contrasting background.
- request-AC7 -> This backlog slice. Proof: AC2: Unchecked and checked checkboxes are visibly distinct on every dark workspace surface.
- request-AC8 -> This backlog slice. Proof: AC3: Keyboard navigation makes the focused and selected item unambiguous without relying on color alone.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_004_peaklive_dense_and_legible_diagnostic_workspace`
- Architecture decision(s): (none yet)
- Request: `req_003_improve_peaklive_workspace_visual_usability_and_panel_density`
- Primary task(s): `task_004_deliver_the_peaklive_visual_usability_and_responsive_workspace_refinement`

# Priority
- Priority: High - unreadable selector and menu text blocks basic configuration and navigation throughout the application.
- Rationale: Set by scaffold input or defaulted for grooming.
