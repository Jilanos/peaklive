## item_051_add_a_safe_profile_scoped_recording_text_placeholder_and_editor_field - Add a safe profile-scoped recording text placeholder and editor field
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Recording filename configuration
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-03 12:02:14

# AI Context
- Summary: Extends the closed recording filename grammar with one operator label while preserving deterministic preview and atomic reservation behavior.
- Keywords: add, safe, profile, scoped, recording, text, placeholder, editor, field
- Use when: Changing RecordingSettings, RecordingNaming, recording preview, or filename-related persistence for the new text label.
- Skip when: Changing profile lifecycle mechanics or desktop icon packaging without a filename grammar change.

# Problem
- The default template can distinguish date, time, setup, iteration, and rotation segment but cannot carry an operator-defined capture label.
- The filename service has a closed placeholder grammar, so a new text value must be introduced consistently rather than interpolated in the dialog or recorder.

# Scope
- In:
  - Add a persisted free-text field to RecordingSettings and preserve backward compatibility for existing profiles.
  - Set the default new-profile template to {date}_{time}_{profile}_{text}_{iteration:03d}_{segment:03d}.asc while retaining existing stored templates verbatim.
  - Add {text} to the Qt-independent naming grammar, deterministic component sanitization, expansion, preview, reservation, rotated filenames, and sidecar derivation.
  - Place a localized text editor directly below Next iteration in RecordingSettingsDialog, with an accessible name, tooltip, immediate non-mutating preview, and per-profile persistence.
  - Specify the empty-text behavior and ensure it produces no unsafe separators, path traversal, malformed filename, or collision ambiguity.
  - Test text validation/sanitization, old-profile migration, preview, reservation collisions, rotation, profile isolation, and existing ASC/TRC behavior.
- Out:
  - Arbitrary executable template expressions, directory paths, arbitrary format specifications, or shell expansion.
  - Changing existing capture format, rotation, disk-space, sidecar, or no-overwrite policies.
  - Recording only selected decoded signals instead of raw received frames.

# Acceptance criteria
- AC1: A new profile defaults to the documented template with {text}, and existing profile templates are not silently rewritten.
- AC2: The text editor is immediately beneath iteration, updates only the selected profile, survives restart and setup switching, and refreshes the preview without creating files.
- AC3: Preview, normal capture, reservation markers, partial files, rotated segments, and event sidecars agree on the sanitized text-bearing basename.
- AC4: Empty and unsafe text values have documented deterministic safe outcomes; unsafe templates remain rejected by the same domain service.
- AC5: Focused non-Qt and offscreen Qt tests protect the grammar and regression-sensitive recording behavior.

# AC Traceability
- request-AC4 -> This backlog slice. Proof: AC1: A new profile defaults to the documented template with {text}, and existing profile templates are not silently rewritten.
- request-AC5 -> This backlog slice. Proof: AC2: The text editor is immediately beneath iteration, updates only the selected profile, survives restart and setup switching, and refreshes the preview without creating files.
- request-AC7 -> This backlog slice. Proof: AC3: Preview, normal capture, reservation markers, partial files, rotated segments, and event sidecars agree on the sanitized text-bearing basename.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_014_peaklive_reusable_measurement_setups_and_identifiable_recording_workspace`
- Architecture decision(s): (none yet)
- Request: `req_014_manage_reusable_peaklive_measurement_setups_recording_text_and_desktop_application_identity`
- Primary task(s): `task_015_deliver_reusable_measurement_setups_recording_text_and_application_icon_identity`

# Priority
- Priority: High - capture identification must be correct, persistent, and collision-safe across every recorder path.
- Rationale: Set by scaffold input or defaulted for grooming.
