## item_149_qualify_bilingual_coverage_windows_packaging_and_operator_documentation - Qualify bilingual coverage, Windows packaging and operator documentation
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Bilingual regression proof and Windows handoff
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-21 16:04:44

# AI Context
- Summary: Prove bilingual completeness, packaged Windows behavior and data continuity.
- Keywords: qualify, bilingual, coverage, windows, packaging, operator, documentation
- Use when: qualifying the finished bilingual feature and its documentation.
- Skip when: claiming hardware acceptance from simulated tests.

# Problem
- The current i18n test checks two English strings and the UI structure guard only scans a subset of literal translation calls.
- Source-level catalog success does not prove packaged Windows dialogs, dynamically created views or longer French labels are translated and usable.

# Scope
- In:
  - Create a complete surface-by-surface localization checklist with explicit technical/user-data exceptions and French/English expected-copy assertions for both normal and failure workflows.
  - Parameterize representative UI integration tests by locale, reset locale between tests, verify placeholder parity and catch regression to hardcoded app-owned English prose outside the existing UI-only scan.
  - Exercise live and offline workflows, open non-modal dialogs, modal dialogs created after switching, deferred views, repeated language changes and storage failure; record state/data continuity evidence from deterministic adapters and fixtures.
  - Verify both catalogs and any required Qt translation resources are included in the Windows bundle; perform a Windows smoke run at supported sizes with French accents and keyboard navigation.
  - Run targeted tests, full headless regression tests, Ruff, logics-manager i18n validate, flow validate, lint and audit; record actual outputs and distinguish unavailable Windows evidence from passed checks.
  - Update README and docs/product-scope.md during implementation to replace the English-only scope, explain the menu/default/persistence behavior and preserve the distinction between translated UI and untouched user/CAN data.
- Out:
  - Physical hardware qualification or performance claims based only on headless/simulated tests.
  - Additional languages, a general translation-management platform or rewriting historical product decisions.
  - Closing this corpus before all acceptance and packaging evidence is recorded.

# Acceptance criteria
- AC1: Every in-scope UI surface has verified French and English copy, with a reviewed allowlist limited to genuine technical literals and externally supplied content.
- AC2: Focused and full regression suites pass for the required scenarios, catalog parity and formatting checks pass, and language changes preserve measured session/data invariants.
- AC3: A built Windows executable includes both catalogs and needed dialog resources; a documented smoke run proves French/English selection, restart persistence, dialogs, layout and a simulated or replay workflow.
- AC4: README and product scope document the delivered bilingual feature and exclusions; the i18n contract and Logics validation are clean before task closeout.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Every in-scope UI surface has verified French and English copy, with a reviewed allowlist limited to genuine technical literals and externally supplied content.
- request-AC2 -> This backlog slice. Proof: AC2: Focused and full regression suites pass for the required scenarios, catalog parity and formatting checks pass, and language changes preserve measured session/data invariants.
- request-AC3 -> This backlog slice. Proof: AC3: A built Windows executable includes both catalogs and needed dialog resources; a documented smoke run proves French/English selection, restart persistence, dialogs, layout and a simulated or replay workflow.
- request-AC4 -> This backlog slice. Proof: AC4: README and product scope document the delivered bilingual feature and exclusions; the i18n contract and Logics validation are clean before task closeout.
- request-AC5 -> This backlog slice. Proof: AC4: README and product scope document the delivered bilingual feature and exclusions; the i18n contract and Logics validation are clean before task closeout.
- request-AC6 -> This backlog slice. Proof: AC4: README and product scope document the delivered bilingual feature and exclusions; the i18n contract and Logics validation are clean before task closeout.
- request-AC7 -> This backlog slice. Proof: AC4: README and product scope document the delivered bilingual feature and exclusions; the i18n contract and Logics validation are clean before task closeout.
- request-AC8 -> This backlog slice. Proof: AC4: README and product scope document the delivered bilingual feature and exclusions; the i18n contract and Logics validation are clean before task closeout.
- request-AC9 -> This backlog slice. Proof: AC4: README and product scope document the delivered bilingual feature and exclusions; the i18n contract and Logics validation are clean before task closeout.
- request-AC10 -> This backlog slice. Proof: AC4: README and product scope document the delivered bilingual feature and exclusions; the i18n contract and Logics validation are clean before task closeout.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_032_peaklive_french_and_english_operator_experience`
- Architecture decision(s): (none yet)
- Request: `req_035_add_persistent_french_and_english_language_selection_across_peaklive`
- Primary task(s): `task_033_deliver_complete_persistent_french_and_english_language_switching_in_peaklive`

# Priority
- Priority: Medium - final completeness gate after catalog, UI and dynamic-text delivery; prevents shipping a partially translated workflow.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_033_deliver_complete_persistent_french_and_english_language_switching_in_peaklive`

# Notes
- Task `task_033_deliver_complete_persistent_french_and_english_language_switching_in_peaklive` was finished via `logics-manager flow finish task` on 2026-09-21.
