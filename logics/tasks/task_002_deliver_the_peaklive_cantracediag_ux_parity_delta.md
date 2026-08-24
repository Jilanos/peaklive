## task_002_deliver_the_peaklive_cantracediag_ux_parity_delta - Deliver the PeakLive CanTraceDiag UX parity delta
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 95%
> Confidence: 90%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: codex
> Indicators reviewed: 2026-08-24 14:43:18

# AI Context
- Summary: Orchestrates the PeakLive CanTraceDiag UX parity request from delta analysis through DBC, acquisition, signal, graph, layout, visual, and validation slices.
- Keywords: deliver, peaklive, cantracediag, parity, delta
- Use when: Coordinating or implementing the UX parity delivery and deciding which ready backlog slice should run next.
- Skip when: Working on unrelated PeakLive maintenance, low-level driver fixes, or long hardware qualification outside the bounded UX validation scope.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Capture the CanTraceDiag-to-PeakLive UX delta and convert it into a Qt-specific implementation and validation map.
- [x] 2. Implement multi-DBC library, parsing diagnostics, DBC enable/remove state, and conflict resolution first because the signal explorer depends on it.
- [x] 3. Add the acquisition setup panel with bitrate and controller-mode semantics while preserving the application receive-only MVP boundary.
- [x] 4. Implement the DBC/message-grouped signal explorer with search, favorites, shown filtering, and clickable plot selection.
- [x] 5. Add multi-graph rendering, A/B cursors, readouts, graph/trace combo configurations, and collapsible panels.
- [x] 6. Apply the CanTraceDiag-aligned instrument visual system across the refined workspace.
- [x] 7. Validate with fake/replay/fixture automation and, if useful, an optional PCAN smoke test capped at 2 minutes; then close out with Logics lint and audit.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_009_analyze_the_cantracediag_to_peaklive_ux_delta`
- `item_010_deliver_multi_dbc_library_and_conflict_management`
- `item_011_upgrade_acquisition_setup_controls`
- `item_012_bring_the_signal_explorer_to_cantracediag_parity`
- `item_013_deliver_multi_graph_measurements_and_configurable_workspace_panels`
- `item_014_apply_the_cantracediag_instrument_visual_system_to_peaklive`
- `item_015_validate_the_ux_parity_delivery_with_bounded_hardware_evidence`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC7 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC8 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC9 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC2 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC4 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC8 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC9 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC3 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC6 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC8 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC9 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC4 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC6 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC7 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC8 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC9 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC5 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC6 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC7 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC8 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC9 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC1 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC7 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC8 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC8 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`
- request-AC9 -> This task. Proof: Implemented in dcfdac8: multi-DBC library/conflict handling, acquisition setup, grouped signal explorer, multi-graph cursors, collapsible workspace, instrument styling, and delta doc; validated with uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc. No live CAN bus test was required; optional hardware smoke remains capped at <=2 minutes. Source: `dcfdac8`

# Validation
- (no validation recorded yet)
- command: `uv run ruff check . && QT_QPA_PLATFORM=offscreen uv run python -m pytest && logics-manager i18n validate && logics-manager lint --require-status && logics-manager audit --group-by-doc` | result: passed | date: 2026-08-24
- Finish workflow executed on 2026-08-24.
- Linked backlog/request close verification passed.

# Report
- Not started.
- Finished on 2026-08-24.
- Linked backlog item(s): `item_009_analyze_the_cantracediag_to_peaklive_ux_delta`, `item_010_deliver_multi_dbc_library_and_conflict_management`, `item_011_upgrade_acquisition_setup_controls`, `item_012_bring_the_signal_explorer_to_cantracediag_parity`, `item_013_deliver_multi_graph_measurements_and_configurable_workspace_panels`, `item_014_apply_the_cantracediag_instrument_visual_system_to_peaklive`, `item_015_validate_the_ux_parity_delivery_with_bounded_hardware_evidence`
- Related request(s): `req_001_bring_peaklive_ux_to_cantracediag_parity`

# Links
- Request: `req_001_bring_peaklive_ux_to_cantracediag_parity`
- Product brief(s): `prod_002_peaklive_cantracediag_grade_diagnostic_workspace`
- Architecture decision(s): (none yet)
