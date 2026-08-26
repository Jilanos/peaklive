## task_005_implement_the_peaklive_graph_centric_compact_workspace - Implement the PeakLive graph-centric compact workspace
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-08-26 18:38:11
> Owner: Codex

# AI Context
- Summary: Build and verify the shared-axis graph presentation and compact collapsed rails described by item_029.
- Keywords: implement, peaklive, graph, centric, compact, workspace
- Use when: Implementing the single ready backlog slice for the graph-centric workspace request.
- Skip when: Adding any unrelated workspace feature or changing the separately tracked Trace filter-header layout.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Inspect the current collapsed-panel and graph rendering geometry, then add focused regression tests for the observed rail and multi-signal layout defects.
- [x] 2. Implement the safe compact rail affordance and the shared-time graph composition while preserving existing graph interactions and persisted state.
- [x] 3. Rebalance graph controls and workspace mode layout around the graph surface at the supported desktop resolutions.
- [x] 4. Run offscreen UI and full-project validation, record the delivery evidence, close out the Logics task, then commit and push the complete delivery.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_029_deliver_a_compact_shared_axis_graph_workspace_and_robust_collapsed_rails`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> This task. Proof: Implemented in 0152656; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (222 passed), uv run ruff check ., and logics-manager i18n validate. Source: `0152656`
- request-AC2 -> This task. Proof: Implemented in 0152656; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (222 passed), uv run ruff check ., and logics-manager i18n validate. Source: `0152656`
- request-AC3 -> This task. Proof: Implemented in 0152656; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (222 passed), uv run ruff check ., and logics-manager i18n validate. Source: `0152656`
- request-AC4 -> This task. Proof: Implemented in 0152656; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (222 passed), uv run ruff check ., and logics-manager i18n validate. Source: `0152656`
- request-AC5 -> This task. Proof: Implemented in 0152656; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (222 passed), uv run ruff check ., and logics-manager i18n validate. Source: `0152656`
- request-AC6 -> This task. Proof: Implemented in 0152656; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (222 passed), uv run ruff check ., and logics-manager i18n validate. Source: `0152656`

# Validation
- (no validation recorded yet)
- 222 passed in 42.51s
- uv run ruff check . passed
- logics-manager i18n validate passed
- command: `QT_QPA_PLATFORM=offscreen uv run python -m pytest` | result: passed | date: 2026-08-26
- Finish workflow executed on 2026-08-26.
- Linked backlog/request close verification passed.

# Report
- Not started.
- Finished on 2026-08-26.
- Linked backlog item(s): `item_029_deliver_a_compact_shared_axis_graph_workspace_and_robust_collapsed_rails`
- Related request(s): `req_005_make_the_peaklive_workspace_graph_centric_and_compact`

# Links
- Request: `req_005_make_the_peaklive_workspace_graph_centric_and_compact`
- Product brief(s): `prod_005_peaklive_graph_centric_diagnostic_workspace`
- Architecture decision(s): (none yet)
