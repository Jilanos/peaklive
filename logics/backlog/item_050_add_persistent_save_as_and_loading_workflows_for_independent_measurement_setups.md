## item_050_add_persistent_save_as_and_loading_workflows_for_independent_measurement_setups - Add persistent Save As and loading workflows for independent measurement setups
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Measurement profile lifecycle
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-03 12:02:14

# AI Context
- Summary: Establishes profile duplication as a deliberate persistence operation rather than an accidental by-product of the selector.
- Keywords: add, persistent, save, loading, workflows, independent, measurement, setups
- Use when: Working on ProfileStore copy semantics, the profile selector, Save As validation, or non-destructive DBC restoration.
- Skip when: Adding recording-template fields or application packaging assets alone.

# Problem
- The app persists profiles internally but an operator cannot create a named copy of the current configuration through the UI.
- Existing selector behavior can only expose profiles that were pre-populated outside the supported workflow, and setup ownership/copy boundaries are undocumented in behavior.

# Scope
- In:
  - Define a profile-store operation that deep-copies supported configuration with a new identifier and validates a unique, non-blank operator-facing name.
  - Add a localized Save As action and small modal naming interaction reachable from the profile selector or a clearly discoverable menu location.
  - Append, select, save, and restore profiles through the existing ProfileStore atomic persistence path.
  - Document and test the exact copied fields: CAN options, DBC paths and choices, signal state, trace/view preferences, workspace layout, and recording settings.
  - Keep unavailable DBC paths on load and give clear non-destructive feedback while loading all other profile state.
  - Provide offscreen Qt and domain/persistence tests for valid saves, duplicates, whitespace-only values, cancel, isolation, switch/restart, and missing DBC paths.
- Out:
  - Profile deletion, rename, reordering, merging, import/export, or external sharing.
  - Duplicating active capture data, event history, pending reservations, or any hardware I/O state.
  - Modifying DBC parsing, conflict precedence, or CAN adapter behavior.

# Acceptance criteria
- AC1: Save As duplicates the active setup only after a valid unique name is confirmed; it immediately selects and persists the new independent setup.
- AC2: Cancel, blank input, and duplicate names make no persisted or in-memory configuration change and give accessible feedback where appropriate.
- AC3: After a restart, selecting each saved setup restores the documented configuration without cross-profile mutation.
- AC4: A missing DBC reference is reported without deleting it, blocking unrelated setup restoration, or altering DBC source-content ownership.
- AC5: Tests exercise all copy boundaries and the profile selector's update/selection behavior headlessly.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Save As duplicates the active setup only after a valid unique name is confirmed; it immediately selects and persists the new independent setup.
- request-AC2 -> This backlog slice. Proof: AC2: Cancel, blank input, and duplicate names make no persisted or in-memory configuration change and give accessible feedback where appropriate.
- request-AC3 -> This backlog slice. Proof: AC3: After a restart, selecting each saved setup restores the documented configuration without cross-profile mutation.
- request-AC7 -> This backlog slice. Proof: AC4: A missing DBC reference is reported without deleting it, blocking unrelated setup restoration, or altering DBC source-content ownership.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_014_peaklive_reusable_measurement_setups_and_identifiable_recording_workspace`
- Architecture decision(s): (none yet)
- Request: `req_014_manage_reusable_peaklive_measurement_setups_recording_text_and_desktop_application_identity`
- Primary task(s): `task_015_deliver_reusable_measurement_setups_recording_text_and_application_icon_identity`

# Priority
- Priority: High - reusable named setups are the primary operator workflow and must be reliable before its dependent recording settings are trusted.
- Rationale: Set by scaffold input or defaulted for grooming.
