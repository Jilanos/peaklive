## req_014_manage_reusable_peaklive_measurement_setups_recording_text_and_desktop_application_identity - Manage reusable PeakLive measurement setups, recording text, and desktop application identity
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Reusable measurement setups and desktop identity
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-03 12:02:13

# AI Context
- Summary: Defines the operator-facing boundary between a reusable setup, its external DBC references, its safe capture label, and the packaged desktop identity.
- Keywords: manage, reusable, peaklive, measurement, setups, recording, text, desktop, application, identity
- Use when: Adding a supported workflow to duplicate and select persistent measurement profiles, extending a recording-name placeholder, or setting the application icon.
- Skip when: Changing CAN transport, DBC decoding, trace import, or capture content without a profile-management or desktop-identity concern.

# Needs
- Let an operator create and save a reusable measurement setup from the currently active setup through a visible Save As action, then load a saved setup directly from the profile selector.
- Make the full persisted scope of a measurement setup intentional: CAN connection settings, DBC references and their local choices, signal presentation choices, trace/workspace preferences, and recording policy should round-trip together without copying capture history or runtime state.
- Add a profile-scoped free-text recording label immediately below Next iteration. The default recording template must include a {text} placeholder so the label appears in new capture filenames and their live preview.
- Give the running application and packaged Windows executable a distinctive PeakLive icon so it is identifiable in the taskbar, window chrome, and distribution artifact.

# Context
- MeasurementProfile is already an atomic, local-only persisted object in profiles.json. It stores channel, bitrate, controller mode, DBC paths, DBC filtering/conflict choices, shown and favorite signals, trace filters/columns, workspace layout, and RecordingSettings.
- The current profile selector can switch profiles already present in ProfileState, but the application exposes no supported UI for creating, naming, duplicating, importing, exporting, or otherwise managing profiles. A new installation creates only Default measurement.
- Profile persistence stores DBC paths, not DBC file contents. A setup must report unavailable DBC files clearly and retain the stored path rather than silently changing the setup or embedding proprietary source data.
- RecordingNaming accepts only date, time, profile, iteration, and segment placeholders. Its preview, expansion, collision reservation, ASC/TRC writers, and sidecar naming must receive the same safe text value without weakening the no-overwrite contract.
- RecordingSettingsDialog already edits a profile in place, persists immediately through MainWindow, and places Next iteration above a non-mutating preview. It is the established location for the requested text field.
- The native PySide6 entry point creates QApplication without an application icon, and the PyInstaller specification has no icon asset configured. The source tree currently has no owned application icon asset.
- The repository has unrelated uncommitted replay/import artifacts. Delivery must not modify, stage, discard, or absorb them.

# Acceptance criteria
- AC1: The active measurement setup can be duplicated through a localized, keyboard-accessible Save As action. The operator supplies a non-empty, unique display name; cancellation or invalid/duplicate input leaves all existing setups unchanged; success creates a new identifier, selects the copy, and persists it atomically.
- AC2: A newly saved setup is an independent deep copy of the supported measurement configuration: channel, bitrate, controller mode, DBC paths plus enabled/conflict choices, shown/favorite signals, trace filters and columns, workspace layout, and recording settings. Later changes to either setup do not mutate the other. Runtime acquisition state, trace/event contents, recorder reservations, and capture files are never copied.
- AC3: The selector loads each saved setup and restores its persisted configuration reliably. Missing or unreadable DBC files are surfaced as non-destructive operator feedback; they do not prevent the rest of the setup from loading and do not delete stored references.
- AC4: Recording settings expose a localized accessible free-text field directly below Next iteration. RecordingSettings persists this value independently per setup, and the default template becomes {date}_{time}_{profile}_{text}_{iteration:03d}_{segment:03d}.asc for new profiles while existing templates remain unchanged unless the operator edits them.
- AC5: RecordingNaming accepts the documented {text} placeholder only as a text field, sanitizes it deterministically into one safe filename component, and uses exactly the same expanded value for preview, final/partial/reservation files, rotations, and event sidecars. Empty text produces a deliberate stable result and malformed/unsafe templates remain rejected.
- AC6: A bundled, license-safe PeakLive icon is assigned before MainWindow creation so the running desktop application has an icon in supported taskbars and window chrome. The Windows PyInstaller build embeds the same icon in the executable, and packaged resource discovery works from source and from the frozen application.
- AC7: New and changed UI text is localized with accessible names/tooltips. Focused profile, naming, resource, packaging-manifest, and offscreen Qt tests cover Save As success/cancellation/validation, deep-copy isolation, persistence and loading, unavailable DBC feedback, text sanitization and collision reservation, preview non-mutation, taskbar/window icon assignment, and build-asset inclusion without regressing capture semantics.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_014_peaklive_reusable_measurement_setups_and_identifiable_recording_workspace`
- Architecture decision(s): (none yet)

# References
- src/peaklive/domain/models.py
- src/peaklive/services/profiles.py
- src/peaklive/recording/naming.py
- src/peaklive/ui/main_window.py
- src/peaklive/ui/actions.py
- src/peaklive/ui/panels/acquisition_bar.py
- src/peaklive/ui/dialogs/recording.py
- src/peaklive/app.py
- peaklive.spec
- scripts/build-windows.ps1
- src/peaklive/i18n/en.json
- tests/test_profiles.py
- tests/test_recording_naming.py
- tests/test_recording_settings_ui.py
- tests/test_ui.py

# Backlog
- `item_050_add_persistent_save_as_and_loading_workflows_for_independent_measurement_setups`
- `item_051_add_a_safe_profile_scoped_recording_text_placeholder_and_editor_field`
- `item_052_create_and_package_the_peaklive_application_icon`
