## item_054_deliver_a_compact_high_contrast_signals_tree_and_explicit_drop_down_affordances - Deliver a compact, high-contrast Signals tree and explicit drop-down affordances
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 85%
> Confidence: 70%
> Progress: 85%
> Complexity: High
> Theme: Signal navigation and dark-theme affordances
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-03 15:40:00

# AI Context
- Summary: Make nested signal-tree expansion, shown/favorite actions, signal names, and combo-box triggers readable and actionable on the dark instrument theme.
- Keywords: deliver, compact, high, contrast, signals, tree, explicit, drop, down, affordances
- Use when: Branch markers, per-signal states, signal names, or drop-down actions are visually ambiguous or consume excessive workspace width.
- Skip when: The work changes DBC catalog ownership, decode precedence, hierarchy meaning, or recording policy.

# Problem
- Dark-on-dark or otherwise indistinct branch markers leave an operator unable to tell whether a DBC or message can be expanded or collapsed.
- Nested DBC and message indentation plus two action columns consume width before the signal name, causing routine signal names to be cut off.
- Checkboxes and a white drop-down click target do not clearly communicate their actions within the dark visual system.

# Scope
- In:
  - Render explicit high-contrast tree branch icons for expanded and collapsed DBC/message nodes, with mouse, keyboard, focus, hover, and disabled states.
  - Redesign signal rows to reserve two leading compact action positions after the tree indentation: eye for shown and star for favorite. Use filled/highlighted selected states and muted-but-visible unselected states, without repeating shown/favorite words or a checkbox column/header.
  - Allocate remaining row width to the signal name with bounded elision, full-name tooltips, and accessible descriptions; retain DBC then message hierarchy rather than adding another indentation level.
  - Audit and improve QComboBox trigger/popup styling across the application so the arrow/action is explicit, readable, and consistent on the supported platform.
  - Retain all existing explorer filtering, grouping, shown/favorite behavior, keyboard activation, DBC-library ownership, and profile persistence.
  - Add offscreen tests for geometry, branch visibility/state, icon action states/accessibility, combo rendering contract, filtering, and persistence.
- Out:
  - Changing DBC catalog management, conflict precedence, frame decoding, or per-signal recording behavior.
  - Removing DBC/message grouping or moving DBC enabled/disabled state into the Signals tree.
  - Replacing standard combo boxes with a custom menu system outside the stated affordance problem.

# Acceptance criteria
- AC2: In the Signals tree, DBC and message rows have a visible expanded/collapsed affordance in all enabled, hover, focus, and disabled states; it can be operated with mouse and keyboard.
- AC3: A signal row reserves no separate shown/favorite checkbox columns. Its name remains the primary flexible field, while two compact eye and star controls occupy the leading reserved space; selected state is filled or highlighted and unselected state remains visibly muted, with tooltips, accessible names, and keyboard operation.
- AC4: Signal search, shown-only, favorites-only, grouping, single-click show/hide, DBC enablement separation, and persisted shown/favorite selections retain their semantics after the compact tree redesign.
- AC5: Every QComboBox used by the application has a clearly recognizable, high-contrast drop-down affordance and a coherent hover, focus, disabled, and popup state on supported desktop platforms; it is not rendered as an unexplained white square.
- AC9: Offscreen and focused UI regression tests cover colour assignment/stability, tree affordance contrast and compact geometry, shown/favorite interaction and persistence, combo-box trigger states, one-row control containment, fit semantics, measurement visibility, and preserved existing graph/signal workflows.

# AC Traceability
- request-AC2 -> This backlog slice. Proof: `BranchAffordanceTree.drawBranches()` (`src/peaklive/ui/panels/signal_row_icons.py`) paints an explicit filled chevron for every has-children row (enabled/hover/disabled colour variants; native Left/Right/Enter keyboard expand-collapse retained). Covered by `tests/test_ui_signal_affordances.py::test_dbc_and_message_rows_expose_a_high_contrast_branch_affordance`, `::test_branch_expand_collapse_is_keyboard_operable`, `::test_disabled_rows_still_carry_a_legible_branch`.
- request-AC3 -> This backlog slice. **Partially proven.** Delivered: checkbox squares replaced by filled/muted eye and star pictograms (`RowActionDelegate`), action columns shrunk 46px -> 28px so the name keeps more width, tooltip/accessible-name pairing unchanged. **Not delivered as literally specified:** the eye/star columns stay in their existing trailing position (`SHOWN_COLUMN=1`, `FAVORITE_COLUMN=2`, name stays column 0) rather than a "leading" position ahead of the name, and they remain two distinct tree columns rather than being merged away entirely - Qt only attaches branch/indentation decoration to a tree's logical column 0, so relocating the name out of it would detach the expand arrow from its row (verified empirically; see task doc Implementation notes). Covered by `tests/test_ui_signal_affordances.py::test_shown_and_favorite_actions_paint_distinctly_when_active`, `::test_the_action_columns_are_compact_and_the_name_keeps_the_flexible_width`, `::test_action_cells_keep_their_tooltip_and_accessible_state`.
- request-AC4 -> This backlog slice. Proof: filtering/grouping/persistence logic in `SignalExplorerPanel` untouched; existing `tests/test_ui_workspace_refinement.py` item_026 tests (search, shown-only, favorites-only, DBC enablement, restart persistence) still pass unmodified against the new rendering.
- request-AC5 -> This backlog slice. Proof: `theme.py` `CONTROL_STYLE` gained `QComboBox::down-arrow:hover`; existing combo contrast rules audited across the app. Covered by `tests/test_ui_signal_affordances.py::test_every_workspace_combo_box_paints_a_visible_drop_down_affordance` (walks every visible `QComboBox` in the built window).
- request-AC9 -> This backlog slice. Proof: see item_053's AC9 entry - the same two new test files and full-suite run cover both slices' regression surface together (418 tests, 0 failures; `ruff check .` clean).

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_015_peaklive_unmistakable_graph_comparison_and_signal_controls`
- Architecture decision(s): (none yet)
- Request: `req_015_make_peaklive_graph_comparison_and_signal_controls_unmistakably_legible`
- Primary task(s): `task_016_implement_legible_peaklive_graph_comparison_and_signal_controls`

# Priority
- Priority: High - signal selection is a primary analyst workflow, and hidden tree controls plus name truncation make the core selection state unreliable.
- Rationale: Set by scaffold input or defaulted for grooming.
