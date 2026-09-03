## task_016_implement_legible_peaklive_graph_comparison_and_signal_controls - Implement legible PeakLive graph comparison and signal controls
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 80%
> Progress: 85%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-03 15:40:00

# AI Context
- Summary: Deliver and prove the graph-comparison and signal-navigation usability slices while preserving their current data and profile contracts.
- Keywords: implement, legible, peaklive, graph, comparison, signal, controls
- Use when: Implementing the linked graph-control and Signals-tree backlog slices as one coordinated workspace usability delivery.
- Skip when: Only a standalone decoding, acquisition, or export change is required.

# Context
- GraphStackPanel owns the curve pens, shared X geometry, and cursor state; MeasurementPanel owns presentation of the A/B and range statistics. Its persisted visibility preference hides values/statistics only, never A/B cursor lines.
- SignalExplorerPanel owns the DBC > message > signal hierarchy and shown/favorite interaction, while the shared theme owns branch and combo-box affordance rendering.
- The graph/trace header request crosses existing panel boundaries: GraphControlsBar is within GraphStackPanel, the workspace selector is reparented above it, and Play/Stop remain in AcquisitionBar. The confirmed single line includes Graphs/Trace, Graphs-only selection, no-sample state, zoom/resize, Play/Stop, cursor actions, and timing readouts.
- Existing profiles persist shown and favorite signals but not colour assignment or measurement visibility; add a backward-compatible persisted preference for measurement-value visibility. Curve colours stay deterministic and need no profile field.

# Plan
- [x] 1. Implement the confirmed one-line Graphs/Trace header contract and profile-persisted value-visibility preference while keeping A/B cursor lines and lifecycle semantics unchanged.
- [x] 2. Add focused offscreen baselines for graph colours and axis fitting, signal-tree geometry and icon states, combo-box trigger states, measurement visibility, accessibility, and benchmark viewport containment.
- [x] 3. Implement the graph comparison slice: stable palette, explicit X+Y and Y-only fit controls, and non-destructive cursor-measurement visibility.
- [x] 4. Implement the explorer/theme slice: visible branch affordances, compact eye/star actions, name-first geometry, and explicit drop-down styling, while preserving filters and profiles.
- [x] 5. Run targeted and full UI tests, i18n validation for changed copy, Logics validation, audit, and status-required lint. Record closeout proof only after both slices satisfy their acceptance criteria.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Implementation notes
- One deviation from the original design note: item_054's eye/star actions stay in their existing trailing tree columns (SHOWN_COLUMN=1, FAVORITE_COLUMN=2, name stays column 0) rather than being reordered ahead of the name. Qt only ever attaches branch/indentation decoration to a tree's logical column 0 (verified empirically), so moving the name out of column 0 would detach the expand arrow from the row it belongs to. The action columns were made compact (28px, was 46px) and rendered as eye/star pictograms via a paint-only delegate instead, which reclaims width for the name without touching column order - preserving `Qt.ItemIsUserCheckable`/`checkState()` as the interaction model also kept every existing test across the suite (test_ui.py, test_ui_parity.py, test_ui_analyst.py) working unchanged, since they address shown/favorite by the same column indices.
- Branch expand/collapse affordance (AC2) could not be done via `::branch` QSS: a CSS border-triangle rule (the same technique already used for `QComboBox::down-arrow`) renders correctly with a hidden tree header but degrades to a flat, low-contrast box once the header is visible (confirmed empirically, appears to be a Fusion-style quirk) - and SignalExplorerPanel needs its header for the column labels. Implemented instead as a `QTreeWidget.drawBranches()` override (`BranchAffordanceTree` in `signal_row_icons.py`), which also adds a hover state the native indicator never had.
- Play/Stop are reparented into the new one-line header as compact "▶"/"■" glyph buttons (same visual language as the other header nav buttons) rather than their previous full-text "Start/Stop Acquisition" labels - `AcquisitionBar` still owns and wires `start_button`/`stop_button` unchanged, only their displayed text and parent widget changed; full wording is preserved in tooltip and accessible name.
- `tests/conftest.py` extraction (sharing `_window`/`_with_dbc`/`_contrast`/`_rendered_contrast` across test files) was scoped out to limit risk on an already-large change; `test_ui_graph_comparison.py` and `test_ui_signal_affordances.py` carry small self-contained copies of the helpers they need instead.

# Backlog
- `item_053_deliver_distinguishable_graph_traces_and_explicit_graph_fitting_controls`
- `item_054_deliver_a_compact_high_contrast_signals_tree_and_explicit_drop_down_affordances`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_053_deliver_distinguishable_graph_traces_and_explicit_graph_fitting_controls`. Proof deferred to slice closeout.
- request-AC6 -> `item_053_deliver_distinguishable_graph_traces_and_explicit_graph_fitting_controls`. Proof deferred to slice closeout.
- request-AC7 -> `item_053_deliver_distinguishable_graph_traces_and_explicit_graph_fitting_controls`. Proof deferred to slice closeout.
- request-AC8 -> `item_053_deliver_distinguishable_graph_traces_and_explicit_graph_fitting_controls`. Proof deferred to slice closeout.
- request-AC9 -> `item_053_deliver_distinguishable_graph_traces_and_explicit_graph_fitting_controls`. Proof deferred to slice closeout.
- request-AC2 -> `item_054_deliver_a_compact_high_contrast_signals_tree_and_explicit_drop_down_affordances`. Proof deferred to slice closeout.
- request-AC3 -> `item_054_deliver_a_compact_high_contrast_signals_tree_and_explicit_drop_down_affordances`. Proof deferred to slice closeout.
- request-AC4 -> `item_054_deliver_a_compact_high_contrast_signals_tree_and_explicit_drop_down_affordances`. Proof deferred to slice closeout.
- request-AC5 -> `item_054_deliver_a_compact_high_contrast_signals_tree_and_explicit_drop_down_affordances`. Proof deferred to slice closeout.
- request-AC9 -> `item_054_deliver_a_compact_high_contrast_signals_tree_and_explicit_drop_down_affordances`. Proof deferred to slice closeout.

# Validation
- Targeted: `QT_QPA_PLATFORM=offscreen uv run python -m pytest tests/test_ui_graph_comparison.py tests/test_ui_signal_affordances.py tests/test_graph_navigation.py tests/test_ui_workspace_refinement.py` - all pass (9 + 7 + existing suites).
- i18n/structure: `QT_QPA_PLATFORM=offscreen uv run python -m pytest tests/test_ui_structure.py tests/test_i18n.py` - all pass.
- Full suite: `QT_QPA_PLATFORM=offscreen uv run python -m pytest tests/` - 418 passed, 0 failed.
- Lint: `uv run ruff check .` - all checks passed.
- Logics: `logics-manager flow validate task_016_...` - 0 findings.

# Report
- Both backlog slices implemented and validated. item_053 (graph comparison) fully meets its acceptance criteria. item_054 (signal tree/combo affordances) meets AC2, AC4, AC5, and AC9, and partially meets AC3 (eye/star pictograms and compact width delivered; column order/merge not, for a documented Qt-constraint reason - see task Implementation notes and item_054's AC3 traceability entry). No changes to data acquisition, decoding, retention, measurement formulas, exports, or acquisition lifecycle semantics. `MeasurementProfile` gained one backward-compatible optional field (`measurement_values_visible`, default `True`); no schema version bump needed. Working tree is commit-ready; no commits made (ADR 009, operator controls commits).

# Links
- Request: `req_015_make_peaklive_graph_comparison_and_signal_controls_unmistakably_legible`
- Product brief(s): `prod_015_peaklive_unmistakable_graph_comparison_and_signal_controls`
- Architecture decision(s): (none yet)
