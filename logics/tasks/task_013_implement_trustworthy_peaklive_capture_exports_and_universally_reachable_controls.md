## task_013_implement_trustworthy_peaklive_capture_exports_and_universally_reachable_controls - Implement trustworthy PeakLive capture exports and universally reachable controls
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: Codex
> Indicators reviewed: 2026-09-02 15:06:27

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: implement, trustworthy, peaklive, capture, exports, universally, reachable, controls
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Establish focused fixtures and tests that distinguish bounded decoded export from lossless raw capture, characterize ASC/TRC interoperability, and define complete versus incomplete capture evidence.
- [x] 2. Implement the raw capture writer and profile/session choice, then preserve existing CSV/Parquet exports with clear scope language and integrity feedback.
- [x] 3. Recompose mode selection so it remains authoritative and reachable in all modes; remove selection-popup animation and make mode labels fit translated text.
- [x] 4. Run a systematic all-mode, supported-viewport control geometry and accessibility audit, correct failures, then execute targeted and full local CI validation, Logics validation, commit, and push the completed corpus.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_046_deliver_explicit_lossless_asc_and_trc_acquisition_capture_export`
- `item_047_make_every_workspace_selector_and_visible_control_legible_stable_and_reachable`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> This task. Proof: Implemented in 9680ac9; validated by 323 passing tests with QT_QPA_PLATFORM=offscreen uv run ruff check . && logics-manager i18n validate && QT_QPA_PLATFORM=offscreen uv run python -m pytest. Source: `9680ac9`
- request-AC2 -> This task. Proof: Implemented in 9680ac9; validated by 323 passing tests with QT_QPA_PLATFORM=offscreen uv run ruff check . && logics-manager i18n validate && QT_QPA_PLATFORM=offscreen uv run python -m pytest. Source: `9680ac9`
- request-AC3 -> This task. Proof: Implemented in 9680ac9; validated by 323 passing tests with QT_QPA_PLATFORM=offscreen uv run ruff check . && logics-manager i18n validate && QT_QPA_PLATFORM=offscreen uv run python -m pytest. Source: `9680ac9`
- request-AC4 -> This task. Proof: Implemented in 9680ac9; validated by 323 passing tests with QT_QPA_PLATFORM=offscreen uv run ruff check . && logics-manager i18n validate && QT_QPA_PLATFORM=offscreen uv run python -m pytest. Source: `9680ac9`
- request-AC5 -> This task. Proof: Implemented in 9680ac9; validated by 323 passing tests with QT_QPA_PLATFORM=offscreen uv run ruff check . && logics-manager i18n validate && QT_QPA_PLATFORM=offscreen uv run python -m pytest. Source: `9680ac9`
- request-AC9 -> This task. Proof: Implemented in 9680ac9; validated by 323 passing tests with QT_QPA_PLATFORM=offscreen uv run ruff check . && logics-manager i18n validate && QT_QPA_PLATFORM=offscreen uv run python -m pytest. Source: `9680ac9`
- request-AC6 -> This task. Proof: Implemented in 9680ac9; validated by 323 passing tests with QT_QPA_PLATFORM=offscreen uv run ruff check . && logics-manager i18n validate && QT_QPA_PLATFORM=offscreen uv run python -m pytest. Source: `9680ac9`
- request-AC7 -> This task. Proof: Implemented in 9680ac9; validated by 323 passing tests with QT_QPA_PLATFORM=offscreen uv run ruff check . && logics-manager i18n validate && QT_QPA_PLATFORM=offscreen uv run python -m pytest. Source: `9680ac9`
- request-AC8 -> This task. Proof: Implemented in 9680ac9; validated by 323 passing tests with QT_QPA_PLATFORM=offscreen uv run ruff check . && logics-manager i18n validate && QT_QPA_PLATFORM=offscreen uv run python -m pytest. Source: `9680ac9`
- request-AC9 -> This task. Proof: Implemented in 9680ac9; validated by 323 passing tests with QT_QPA_PLATFORM=offscreen uv run ruff check . && logics-manager i18n validate && QT_QPA_PLATFORM=offscreen uv run python -m pytest. Source: `9680ac9`

# Validation
- (no validation recorded yet)
- command: `QT_QPA_PLATFORM=offscreen uv run ruff check . && logics-manager i18n validate && QT_QPA_PLATFORM=offscreen uv run python -m pytest` | result: passed | date: 2026-09-02
- Finish workflow executed on 2026-09-02.
- Linked backlog/request close verification passed.

# Report
- Not started.
- Finished on 2026-09-02.
- Linked backlog item(s): `item_046_deliver_explicit_lossless_asc_and_trc_acquisition_capture_export`, `item_047_make_every_workspace_selector_and_visible_control_legible_stable_and_reachable`
- Related request(s): `req_012_make_peaklive_lossless_capture_export_and_workspace_controls_trustworthy`

# Links
- Request: `req_012_make_peaklive_lossless_capture_export_and_workspace_controls_trustworthy`
- Product brief(s): `prod_012_peaklive_trustworthy_raw_captures_and_universally_reachable_workspace_controls`
- Architecture decision(s): (none yet)
