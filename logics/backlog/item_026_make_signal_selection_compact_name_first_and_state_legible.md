## item_026_make_signal_selection_compact_name_first_and_state_legible - Make signal selection compact, name-first, and state-legible
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 45%
> Complexity: Medium
> Theme: Signal explorer
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-26 16:24:36

# AI Context
- Summary: Rebalance the grouped signal tree around a readable signal name and compact independent shown/favorite actions.
- Keywords: signal, selection, compact, name, first, state, legible
- Use when: Tree-row density or state affordances prevent an operator from finding and selecting a decoded signal quickly.
- Skip when: The required change concerns which DBC definitions are enabled or how they decode frames.

# Problem
- Signal rows give separate columns to shown and fav, then repeat those words next to each checkbox. This consumes disproportionate width while the signal name, the most important information, is truncated.
- The unchecked checkbox affordance is hard to see against the dark surface, making state and action ambiguous.
- DBC enablement is a distinct concern already available in the DBC library and must not be conflated with per-signal shown or favorite state.

# Scope
- In:
  - Redesign the signal tree row and headers so the signal name receives the dominant flexible width.
  - Represent shown and favorite as compact, recognizable controls or icons with concise header-level labels, tooltips, accessible names, and keyboard-operable state.
  - Set practical minimum widths and resize behavior that protect signal-name readability before action columns consume width.
  - Provide clear checked, unchecked, hover, focus, and disabled visual states for shown and favorite controls in the shared dark theme.
  - Keep shown-only, favorites-only, search, grouped DBC/message navigation, single-click activation, and profile persistence working.
  - Retain DBC enabled/disabled control in the DBC library without duplicating it in the explorer.
- Out:
  - Changing the DBC catalog, conflict precedence, or decode pipeline.
  - Adding per-signal recording filters or bulk edit workflows.
  - Replacing the tree navigation model with a separate database browser.

# Acceptance criteria
- AC1: At the default Signals-panel width, a signal row allocates most horizontal width to the signal name and no longer repeats shown or fav text beside every checkbox.
- AC2: Shown and favorite can each be toggled directly and independently using mouse and keyboard, with an accessible name and tooltip that state the action and state.
- AC3: The unchecked, checked, hover, focus, and disabled states are visually distinguishable on the dark theme.
- AC4: DBC enablement remains controlled from the DBC library and has no duplicated per-signal control.
- AC5: Search, shown-only, favorites-only, grouping, and persisted shown/favorite selections retain their current behavior.
- AC6: Headless tests assert column sizing or layout policy, state toggling, accessible names, and persistence.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: At the default Signals-panel width, a signal row allocates most horizontal width to the signal name and no longer repeats shown or fav text beside every checkbox.
- request-AC2 -> This backlog slice. Proof: AC2: Shown and favorite can each be toggled directly and independently using mouse and keyboard, with an accessible name and tooltip that state the action and state.
- request-AC3 -> This backlog slice. Proof: AC3: The unchecked, checked, hover, focus, and disabled states are visually distinguishable on the dark theme.
- request-AC7 -> This backlog slice. Proof: AC4: DBC enablement remains controlled from the DBC library and has no duplicated per-signal control.
- request-AC8 -> This backlog slice. Proof: AC5: Search, shown-only, favorites-only, grouping, and persisted shown/favorite selections retain their current behavior.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_004_peaklive_dense_and_legible_diagnostic_workspace`
- Architecture decision(s): (none yet)
- Request: `req_003_improve_peaklive_workspace_visual_usability_and_panel_density`
- Primary task(s): `task_004_deliver_the_peaklive_visual_usability_and_responsive_workspace_refinement`

# Priority
- Priority: High - signal identification and selection are primary analyst actions, and the current row layout hides the most important information.
- Rationale: Set by scaffold input or defaulted for grooming.
