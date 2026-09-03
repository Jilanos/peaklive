## task_014_implement_configurable_collision_safe_peaklive_recording_names - Implement configurable, collision-safe PeakLive recording names
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-03 10:57:26

# AI Context
- Summary: Coordinates the service-first naming change with the profile-scoped Qt editor while preserving raw capture evidence semantics.
- Keywords: implement, configurable, collision, safe, peaklive, recording, names
- Use when: Delivering either recording naming reservation or its settings/preview UI as one integrated task.
- Skip when: Working on unrelated trace, graph, adapter, or export changes.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Characterize current RecordingSettings, recorder lifecycle, profile persistence, and ASC/TRC tests; introduce a clock-injectable naming/reservation contract with focused failure and concurrency fixtures.
- [x] 2. Wire reservation and next-iteration persistence into acquisition startup and recorder finalization without changing raw capture ordering, formats, rotations, or incomplete-capture evidence.
- [x] 3. Add the localized Recording settings action/editor with folder browse, validation, profile binding, reset, and immediate non-mutating preview.
- [x] 4. Run targeted unit/service/profile/offscreen UI tests, the full test suite and Logics validation; refresh the Logics index and leave unrelated worktree changes untouched.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_048_deliver_a_deterministic_recording_naming_and_reservation_service`
- `item_049_expose_profile_recording_settings_with_live_filename_preview`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> This task. Proof: `tests/test_recording_settings_ui.py::test_recording_settings_dialog_is_reachable_and_shows_the_profile` opens the Recording settings dialog from `MainWindow._open_recording_dialog` (wired to the View menu) and asserts every requested field and its accessible name are present.
- request-AC2 -> This task. Proof: `tests/test_recording_settings_ui.py::test_browse_cancellation_leaves_the_profile_unchanged`, `::test_browse_selection_commits_and_persists_the_chosen_folder`, and `::test_each_profile_keeps_its_own_independent_recording_settings` cover cancel, selection, persistence round-trip, and per-profile isolation.
- request-AC3 -> This task. Proof: `tests/test_recording_naming.py` covers `RecordingNaming.expand`/`preview` for every documented placeholder, numeric-width specs, and rejection of unsupported, empty, unmatched-brace, and path-escaping templates with an actionable `InvalidTemplateError`.
- request-AC4 -> This task. Proof: `tests/test_recording_settings_ui.py::test_preview_updates_live_and_never_creates_a_file` and `::test_invalid_template_shows_actionable_feedback_and_placeholder_preview` show the preview reacting immediately to template/iteration edits without touching disk.
- request-AC5 -> This task. Proof: `tests/test_recording_naming.py::test_reserve_skips_existing_final_and_partial_files`, `::test_reserve_skips_a_stale_reservation_marker_left_by_a_crash`, and `::test_two_competing_reservations_never_claim_the_same_candidate` prove the first-free search and the atomic `O_CREAT|O_EXCL` marker reservation.
- request-AC6 -> This task. Proof: `tests/test_recording_naming.py::test_reset_to_one_restarts_the_search_rather_than_permitting_an_overwrite`, `tests/test_acquisition.py::test_a_successful_start_advances_the_persisted_iteration_by_one`, and `tests/test_recording_settings_ui.py::test_reset_restarts_the_visible_iteration_at_one` cover the 012/013 occupied -> 014 used -> 015 next example and the Reset-to-one behaviour.
- request-AC7 -> This task. Proof: `tests/test_acquisition.py::test_start_skips_existing_evidence_and_uses_the_first_free_iteration` and `::test_a_failed_writer_start_releases_the_reservation_without_advancing_iteration` show `AcquisitionSession`/`AscRecorder` consuming the reservation unchanged and releasing it on a failed writer start; `tests/test_asc_recorder.py` and `tests/test_acquisition.py` regressions confirm raw-frame ordering, rotation, and the incomplete-capture contract are untouched.
- request-AC8 -> This task. Proof: `uv run ruff check .` (all checks passed) and `uv run python -m pytest` (356 passed) on 2026-09-03, including the new `tests/test_recording_naming.py`, `tests/test_recording_settings_ui.py`, and the extended `tests/test_acquisition.py`/`tests/test_worker.py` cases, alongside the full existing regression suite.

# Validation
- `uv run ruff check .` passed on 2026-09-03: All checks passed!
- `uv run python -m pytest` passed on 2026-09-03: 356 passed.
- Finish workflow executed on 2026-09-03.
- Linked backlog/request close verification passed.

# Report
- Delivered a Qt-independent `RecordingNaming` service (`src/peaklive/recording/naming.py`) that validates the documented placeholder grammar, previews filenames without touching disk, and atomically reserves the first free iteration via an exclusive `.reserved` marker.
- Wired the reservation into `AcquisitionSession.start`/`AscRecorder.start`: a successful reservation advances the persisted profile iteration and is consumed by the writer without duplicating template logic; a failed writer start releases the reservation instead of burning the candidate. Rotation, raw-frame ordering, ASC/TRC output, and the incomplete-capture contract are unchanged.
- Added a profile-scoped `RecordingSettingsDialog` (`src/peaklive/ui/dialogs/recording.py`) reachable from the View menu, binding enable/folder/template/iteration/reset/live preview directly to `MeasurementProfile.recording` with the existing immediate-persistence pattern used by `ColumnsDialog`.
- Added targeted unit, service, and offscreen UI tests; the full suite (356 tests) and `ruff check` pass. The worktree's unrelated replay/external-artifact changes were left untouched.
- Finished on 2026-09-03.
- Linked backlog item(s): `item_048_deliver_a_deterministic_recording_naming_and_reservation_service`, `item_049_expose_profile_recording_settings_with_live_filename_preview`
- Related request(s): `req_013_add_canalyzer_style_recording_configuration_and_collision_safe_acquisition_naming_to_peaklive`

# Links
- Request: `req_013_add_canalyzer_style_recording_configuration_and_collision_safe_acquisition_naming_to_peaklive`
- Product brief(s): `prod_013_peaklive_configurable_and_collision_safe_acquisition_recording`
- Architecture decision(s): (none yet)
