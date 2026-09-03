## task_015_deliver_reusable_measurement_setups_recording_text_and_application_icon_identity - Deliver reusable measurement setups, recording text, and application icon identity
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-03 12:17:13

# AI Context
- Summary: Coordinates three dependent deliveries: independent profile copies, a safe text-bearing recording basename, and a package-aware desktop icon.
- Keywords: deliver, reusable, measurement, setups, recording, text, application, icon, identity
- Use when: Implementing the full request as one sequence while protecting existing capture evidence and unrelated worktree changes.
- Skip when: Working on a standalone replay, graph, DBC decoding, or general styling task.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Characterize current ProfileStore ownership, UI save paths, DBC reload behavior, recording naming/reservation flow, and PyInstaller resource conventions; establish test fixtures without touching unrelated worktree changes.
- [x] 2. Implement and test the profile Save As lifecycle first, including deep-copy boundaries, atomic persistence, selector refresh/selection, validation, and non-destructive missing-DBC feedback.
- [x] 3. Extend RecordingSettings and RecordingNaming with the safe {text} contract, migrate the recording dialog and localization, then verify preview/reservation/rotation/sidecar agreement and profile isolation.
- [x] 4. Create the owned icon asset and connect it to the QApplication and Windows packaging specification, with resource and configuration tests appropriate to headless CI.
- [x] 5. Run targeted and full tests, ruff, Logics validation, lint, and audit; record task-closeout evidence only after each acceptance criterion has traceable proof.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_050_add_persistent_save_as_and_loading_workflows_for_independent_measurement_setups`
- `item_051_add_a_safe_profile_scoped_recording_text_placeholder_and_editor_field`
- `item_052_create_and_package_the_peaklive_application_icon`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_050_add_persistent_save_as_and_loading_workflows_for_independent_measurement_setups`. Proof: `tests/test_profile_save_as_ui.py` covers the localized, Ctrl+Shift+S menu action and the acquisition-bar button, unique-name validation, cancellation, and atomic selection of the new setup.
- request-AC2 -> `item_050_add_persistent_save_as_and_loading_workflows_for_independent_measurement_setups`. Proof: `tests/test_profiles.py::test_a_saved_copy_carries_every_documented_configuration_field` and `::test_editing_one_setup_never_reaches_the_other` pin the copied fields and the isolation of later edits.
- request-AC3 -> `item_050_add_persistent_save_as_and_loading_workflows_for_independent_measurement_setups`. Proof: `tests/test_profile_save_as_ui.py::test_the_selector_reloads_each_saved_setup_after_a_restart` and `::test_an_unavailable_dbc_is_reported_without_dropping_the_reference`.
- request-AC7 -> `item_050_add_persistent_save_as_and_loading_workflows_for_independent_measurement_setups`. Proof: `tests/test_profile_save_as_ui.py::test_the_save_as_affordance_is_reachable_and_labelled` checks the localized accessible name, tooltip, and shortcut.
- request-AC4 -> `item_051_add_a_safe_profile_scoped_recording_text_placeholder_and_editor_field`. Proof: `tests/test_recording_naming.py::test_the_default_template_carries_the_operator_text` and `tests/test_recording_settings_ui.py::test_the_text_field_sits_directly_below_next_iteration`.
- request-AC5 -> `item_051_add_a_safe_profile_scoped_recording_text_placeholder_and_editor_field`. Proof: `tests/test_recording_naming.py` sanitization, reservation, and collision cases plus `tests/test_asc_recorder.py::test_every_rotated_segment_and_sidecar_carries_the_operator_text`.
- request-AC7 -> `item_051_add_a_safe_profile_scoped_recording_text_placeholder_and_editor_field`. Proof: `tests/test_recording_settings_ui.py::test_the_text_field_sits_directly_below_next_iteration` and `::test_the_text_belongs_to_one_setup_only` run offscreen.
- request-AC6 -> `item_052_create_and_package_the_peaklive_application_icon`. Proof: `tests/test_application_icon.py` covers the owned asset, its size table, source and frozen resolution, QApplication badging before MainWindow, and the spec's icon and resource references.
- request-AC7 -> `item_052_create_and_package_the_peaklive_application_icon`. Proof: `tests/test_application_icon.py::test_the_application_is_badged_before_any_window_is_built` runs headlessly under the offscreen platform.

# Validation
- `uv run ruff check .` passes.
- `QT_QPA_PLATFORM=offscreen uv run python -m pytest` passes: 395 tests.
- The Windows packaging step is exercised by the Windows CI job; the icon and
- uv run ruff check . passed on 2026-09-03; QT_QPA_PLATFORM=offscreen uv run python -m pytest passed on 2026-09-03: 395 passed
- Finish workflow executed on 2026-09-03.
- Linked backlog/request close verification passed.
  resource references it consumes are asserted from Linux by
  `tests/test_application_icon.py`.

# Report
- Measurement setups: `ProfileState.duplicate_selected` and `ProfileStore.save_as`
- Finished on 2026-09-03.
- Linked backlog item(s): `item_050_add_persistent_save_as_and_loading_workflows_for_independent_measurement_setups`, `item_051_add_a_safe_profile_scoped_recording_text_placeholder_and_editor_field`, `item_052_create_and_package_the_peaklive_application_icon`
- Related request(s): `req_014_manage_reusable_peaklive_measurement_setups_recording_text_and_desktop_application_identity`
  own validation, deep copy, selection, and atomic persistence with rollback on a
  failed write; the shell exposes them through an acquisition-bar button and a
  File menu action. The profile lifecycle moved into
  `src/peaklive/ui/profile_controller.py` so the shell stays inside its module
  line budget.
- Recording text: `RecordingSettings.text` persists per setup, `{text}` joined the
  closed naming grammar with the same one-component sanitization as `{profile}`
  and a documented `unnamed` fallback, and preview, reservation, partial, final,
  rotated, and sidecar paths all derive from the same expansion. The default
  template for a new setup now carries `{text}`; stored templates are untouched.
- Desktop identity: an original SVG and the multi-size ICO generated from it by
  `scripts/generate_icon.py` live in `src/peaklive/resources`, are resolved from
  source or from a frozen build, are assigned to the QApplication before
  MainWindow, and are embedded in the executable by `peaklive.spec`.

# Links
- Request: `req_014_manage_reusable_peaklive_measurement_setups_recording_text_and_desktop_application_identity`
- Product brief(s): `prod_014_peaklive_reusable_measurement_setups_and_identifiable_recording_workspace`
- Architecture decision(s): (none yet)
