## item_049_expose_profile_recording_settings_with_live_filename_preview - Expose profile recording settings with live filename preview
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Recording configuration usability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-03 10:57:27

# AI Context
- Summary: Makes the profile's recording policy operable and observable while delegating path semantics to the naming service.
- Keywords: expose, profile, recording, settings, live, filename, preview
- Use when: Adding the recording settings action, editor binding, folder chooser, or live preview.
- Skip when: Implementing filename reservation internals or altering CAN acquisition semantics.

# Problem
- The acquisition bar has no route to configure recording enablement, directory, template, or iteration even though the profile model already stores them.
- Without a live preview and validation, template mistakes are discovered only at start, and the user cannot see the collision-safe next name.

# Scope
- In:
  - Add a localized, keyboard-accessible Recording settings menu action and compact PySide6 editor appropriate to the existing instrument UI.
  - Bind enablement, folder, template, iteration, reset, and format-aware read-only preview to the selected MeasurementProfile without moving naming policy into Qt.
  - Use QFileDialog.getExistingDirectory for Browse; cancellation changes nothing, while a chosen directory is normalized and persisted through existing profile save paths.
  - Give immediate invalid-template feedback, disable or guard start according to the existing error-reporting convention, and preserve edits when switching profiles only after their normal persistence point.
  - Cover offscreen layout, accessible names, keyboard focus, preview updates, reset, browse cancellation/selection, profile switching, and current acquisition-bar behaviour.
- Out:
  - A general profile-management redesign, editing rotation/free-space thresholds, or a capture-history UI.
  - Changing CAN channel, bitrate, controller mode, or raw-export controls beyond keeping their current persistence intact.

# Acceptance criteria
- AC1: Every selected profile has an operable Recording settings route with all requested fields and localized accessibility metadata.
- AC2: Folder selection and profile persistence have correct cancel, selection, and profile-switch semantics.
- AC3: Preview is instant, read-only, and non-mutating, and it agrees with the domain naming service for valid input.
- AC4: Reset and visible next iteration accurately reflect collision-safe acquisition naming without overwriting previous files.
- AC5: Offscreen UI and persistence regression tests cover accessible interaction and preserve existing acquisition-bar behaviour.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Every selected profile has an operable Recording settings route with all requested fields and localized accessibility metadata.
- request-AC2 -> This backlog slice. Proof: AC2: Folder selection and profile persistence have correct cancel, selection, and profile-switch semantics.
- request-AC4 -> This backlog slice. Proof: AC3: Preview is instant, read-only, and non-mutating, and it agrees with the domain naming service for valid input.
- request-AC6 -> This backlog slice. Proof: AC4: Reset and visible next iteration accurately reflect collision-safe acquisition naming without overwriting previous files.
- request-AC8 -> This backlog slice. Proof: AC5: Offscreen UI and persistence regression tests cover accessible interaction and preserve existing acquisition-bar behaviour.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_013_peaklive_configurable_and_collision_safe_acquisition_recording`
- Architecture decision(s): (none yet)
- Request: `req_013_add_canalyzer_style_recording_configuration_and_collision_safe_acquisition_naming_to_peaklive`
- Primary task(s): `task_014_implement_configurable_collision_safe_peaklive_recording_names`

# Priority
- Priority: High - the existing recording policy is persisted but invisible, so an operator cannot deliberately choose the evidence destination or understand the next filename.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_014_implement_configurable_collision_safe_peaklive_recording_names`

# Notes
- Task `task_014_implement_configurable_collision_safe_peaklive_recording_names` was finished via `logics-manager flow finish task` on 2026-09-03.
