## task_015_deliver_reusable_measurement_setups_recording_text_and_application_icon_identity - Deliver reusable measurement setups, recording text, and application icon identity
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-03 12:02:14

# AI Context
- Summary: Coordinates three dependent deliveries: independent profile copies, a safe text-bearing recording basename, and a package-aware desktop icon.
- Keywords: deliver, reusable, measurement, setups, recording, text, application, icon, identity
- Use when: Implementing the full request as one sequence while protecting existing capture evidence and unrelated worktree changes.
- Skip when: Working on a standalone replay, graph, DBC decoding, or general styling task.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Characterize current ProfileStore ownership, UI save paths, DBC reload behavior, recording naming/reservation flow, and PyInstaller resource conventions; establish test fixtures without touching unrelated worktree changes.
- [ ] 2. Implement and test the profile Save As lifecycle first, including deep-copy boundaries, atomic persistence, selector refresh/selection, validation, and non-destructive missing-DBC feedback.
- [ ] 3. Extend RecordingSettings and RecordingNaming with the safe {text} contract, migrate the recording dialog and localization, then verify preview/reservation/rotation/sidecar agreement and profile isolation.
- [ ] 4. Create the owned icon asset and connect it to the QApplication and Windows packaging specification, with resource and configuration tests appropriate to headless CI.
- [ ] 5. Run targeted and full tests, ruff, Logics validation, lint, and audit; record task-closeout evidence only after each acceptance criterion has traceable proof.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_050_add_persistent_save_as_and_loading_workflows_for_independent_measurement_setups`
- `item_051_add_a_safe_profile_scoped_recording_text_placeholder_and_editor_field`
- `item_052_create_and_package_the_peaklive_application_icon`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_050_add_persistent_save_as_and_loading_workflows_for_independent_measurement_setups`. Proof deferred to slice closeout.
- request-AC2 -> `item_050_add_persistent_save_as_and_loading_workflows_for_independent_measurement_setups`. Proof deferred to slice closeout.
- request-AC3 -> `item_050_add_persistent_save_as_and_loading_workflows_for_independent_measurement_setups`. Proof deferred to slice closeout.
- request-AC7 -> `item_050_add_persistent_save_as_and_loading_workflows_for_independent_measurement_setups`. Proof deferred to slice closeout.
- request-AC4 -> `item_051_add_a_safe_profile_scoped_recording_text_placeholder_and_editor_field`. Proof deferred to slice closeout.
- request-AC5 -> `item_051_add_a_safe_profile_scoped_recording_text_placeholder_and_editor_field`. Proof deferred to slice closeout.
- request-AC7 -> `item_051_add_a_safe_profile_scoped_recording_text_placeholder_and_editor_field`. Proof deferred to slice closeout.
- request-AC6 -> `item_052_create_and_package_the_peaklive_application_icon`. Proof deferred to slice closeout.
- request-AC7 -> `item_052_create_and_package_the_peaklive_application_icon`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_014_manage_reusable_peaklive_measurement_setups_recording_text_and_desktop_application_identity`
- Product brief(s): `prod_014_peaklive_reusable_measurement_setups_and_identifiable_recording_workspace`
- Architecture decision(s): (none yet)
