## task_033_deliver_complete_persistent_french_and_english_language_switching_in_peaklive - Deliver complete persistent French and English language switching in PeakLive
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 45%
> Complexity: High
> Theme: Bilingual operator interface delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-21 13:59:59
> Owner: maintainer@example.invalid

# AI Context
- Summary: Orchestrate four implementation waves for complete, state-preserving French/English language selection.
- Keywords: deliver, complete, persistent, french, english, language, switching, peaklive
- Use when: delivering and validating the bilingual feature end to end.
- Skip when: only changing README screenshot labels or translating DBC content.

# Context
- Deliver the request's ten acceptance criteria through four ordered implementation slices. Existing English semantic keys are a foundation, not proof that already constructed widgets, dynamic messages or report prose support switching.
- Keep acquisition/replay workers, source data and profile ownership independent from UI locale. English remains the first-run default; language is a persistent application preference.

# Priority
- Medium - complete operator-facing capability; schedule after existing High-priority acquisition/replay integrity work. Execute the foundation before UI retranslation, dynamic-text completion and final qualification.

# Plan
- [ ] 1. Preflight: read this request and all four slices, inspect current actions/workers touched by active tasks, and inventory every app-owned text surface. Confirm Medium sequencing behind existing High-priority integrity work. This corpus is planning only; start the task through flow start when implementation begins.
- [ ] 2. Wave 1: deliver the locale service, full French/English catalogs, safe app-scoped ui-settings persistence and startup initialization. Extend the i18n contract and validate fallback, key parity and formatting before wiring the selector.
- [ ] 3. Wave 2 (depends on wave 1): add Setup > Language, retranslate existing and deferred widgets in place, preserve stable action/item identities and verify no session reset during en/fr switching. Include standard Qt dialog localization and responsive geometry.
- [ ] 4. Wave 3 (depends on waves 1 and 2): complete dynamic analysis, error and report rendering, retaining semantic parameters and untranslated technical details. Validate human-readable report language and unchanged machine-readable exports.
- [ ] 5. Wave 4 (depends on all earlier waves): complete bilingual coverage tests and operator docs, build and smoke-test the Windows package, run targeted and full regression/Ruff/i18n checks, and capture proof for every request AC and backlog slice.
- [ ] 6. At each completed wave, update affected Logics evidence and progress through the CLI and commit a coherent code/tests/docs checkpoint. Use flow closeout only after the final checks and Windows evidence are available, settling the linked product brief through the lifecycle CLI.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Commit each completed coherent wave according to repository instructions, without forcing a separate commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_146_establish_bilingual_catalogs_and_an_application_scoped_locale_preference`
- `item_147_add_a_language_menu_and_retranslate_the_workspace_without_resetting_sessions`
- `item_148_localize_dynamic_analysis_text_validation_and_human_readable_reports`
- `item_149_qualify_bilingual_coverage_windows_packaging_and_operator_documentation`

# Definition of Done (DoD)
- [ ] All ten request acceptance criteria and all four backlog slices have implementation and test evidence; creating the corpus alone does not complete this task.
- [ ] Both complete catalogs ship, locale preference survives restart independently of profiles, and missing-resource/storage errors behave as specified.
- [ ] Static and dynamic surfaces, dialogs, accessibility text and human-readable reports switch languages without restarting or losing state.
- [ ] Repeated language changes preserve capture/replay/export operations and all measurement, user-content and machine-readable format contracts.
- [ ] French and English pass supported geometry, accented-character, keyboard and Windows packaged-dialog checks.
- [ ] Focused and full headless tests, Ruff and i18n validation pass; actual Windows build/smoke evidence is recorded separately from simulated/headless evidence.
- [ ] README and product scope describe the delivered feature; Logics validation, lint and audit pass and the product brief is settled through closeout.
- [ ] ADR 009 waves have updated evidence, CLI-managed progress and coherent commits; the handoff pack reflects the current implementation context.

# AC Traceability
- request-AC1 -> `item_146_establish_bilingual_catalogs_and_an_application_scoped_locale_preference`. Proof deferred to slice closeout.
- request-AC3 -> `item_146_establish_bilingual_catalogs_and_an_application_scoped_locale_preference`. Proof deferred to slice closeout.
- request-AC4 -> `item_146_establish_bilingual_catalogs_and_an_application_scoped_locale_preference`. Proof deferred to slice closeout.
- request-AC6 -> `item_146_establish_bilingual_catalogs_and_an_application_scoped_locale_preference`. Proof deferred to slice closeout.
- request-AC8 -> `item_146_establish_bilingual_catalogs_and_an_application_scoped_locale_preference`. Proof deferred to slice closeout.
- request-AC10 -> `item_146_establish_bilingual_catalogs_and_an_application_scoped_locale_preference`. Proof deferred to slice closeout.
- request-AC1 -> `item_147_add_a_language_menu_and_retranslate_the_workspace_without_resetting_sessions`. Proof deferred to slice closeout.
- request-AC2 -> `item_147_add_a_language_menu_and_retranslate_the_workspace_without_resetting_sessions`. Proof deferred to slice closeout.
- request-AC3 -> `item_147_add_a_language_menu_and_retranslate_the_workspace_without_resetting_sessions`. Proof deferred to slice closeout.
- request-AC5 -> `item_147_add_a_language_menu_and_retranslate_the_workspace_without_resetting_sessions`. Proof deferred to slice closeout.
- request-AC6 -> `item_147_add_a_language_menu_and_retranslate_the_workspace_without_resetting_sessions`. Proof deferred to slice closeout.
- request-AC9 -> `item_147_add_a_language_menu_and_retranslate_the_workspace_without_resetting_sessions`. Proof deferred to slice closeout.
- request-AC10 -> `item_147_add_a_language_menu_and_retranslate_the_workspace_without_resetting_sessions`. Proof deferred to slice closeout.
- request-AC2 -> `item_148_localize_dynamic_analysis_text_validation_and_human_readable_reports`. Proof deferred to slice closeout.
- request-AC4 -> `item_148_localize_dynamic_analysis_text_validation_and_human_readable_reports`. Proof deferred to slice closeout.
- request-AC5 -> `item_148_localize_dynamic_analysis_text_validation_and_human_readable_reports`. Proof deferred to slice closeout.
- request-AC6 -> `item_148_localize_dynamic_analysis_text_validation_and_human_readable_reports`. Proof deferred to slice closeout.
- request-AC7 -> `item_148_localize_dynamic_analysis_text_validation_and_human_readable_reports`. Proof deferred to slice closeout.
- request-AC8 -> `item_148_localize_dynamic_analysis_text_validation_and_human_readable_reports`. Proof deferred to slice closeout.
- request-AC10 -> `item_148_localize_dynamic_analysis_text_validation_and_human_readable_reports`. Proof deferred to slice closeout.
- request-AC1 -> `item_149_qualify_bilingual_coverage_windows_packaging_and_operator_documentation`. Proof deferred to slice closeout.
- request-AC2 -> `item_149_qualify_bilingual_coverage_windows_packaging_and_operator_documentation`. Proof deferred to slice closeout.
- request-AC3 -> `item_149_qualify_bilingual_coverage_windows_packaging_and_operator_documentation`. Proof deferred to slice closeout.
- request-AC4 -> `item_149_qualify_bilingual_coverage_windows_packaging_and_operator_documentation`. Proof deferred to slice closeout.
- request-AC5 -> `item_149_qualify_bilingual_coverage_windows_packaging_and_operator_documentation`. Proof deferred to slice closeout.
- request-AC6 -> `item_149_qualify_bilingual_coverage_windows_packaging_and_operator_documentation`. Proof deferred to slice closeout.
- request-AC7 -> `item_149_qualify_bilingual_coverage_windows_packaging_and_operator_documentation`. Proof deferred to slice closeout.
- request-AC8 -> `item_149_qualify_bilingual_coverage_windows_packaging_and_operator_documentation`. Proof deferred to slice closeout.
- request-AC9 -> `item_149_qualify_bilingual_coverage_windows_packaging_and_operator_documentation`. Proof deferred to slice closeout.
- request-AC10 -> `item_149_qualify_bilingual_coverage_windows_packaging_and_operator_documentation`. Proof deferred to slice closeout.

# Validation
- Planning validation on 2026-09-21: request-chain dry-run and scaffold passed; flow validate reported zero findings; lint --require-status passed. Implementation, automated feature tests and Windows packaging smoke tests have not been started. Record feature evidence during delivery, not from corpus generation.

# Report
- Not started.

# Links
- Request: `req_035_add_persistent_french_and_english_language_selection_across_peaklive`
- Product brief(s): `prod_032_peaklive_french_and_english_operator_experience`
- Architecture decision(s): (none yet)
