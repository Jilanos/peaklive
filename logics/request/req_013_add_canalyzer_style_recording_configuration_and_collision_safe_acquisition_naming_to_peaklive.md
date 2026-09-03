## req_013_add_canalyzer_style_recording_configuration_and_collision_safe_acquisition_naming_to_peaklive - Add CANalyzer-style recording configuration and collision-safe acquisition naming to PeakLive
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Operator-configurable, collision-safe acquisition recording
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-03 10:57:26

# AI Context
- Summary: Defines the profile-level naming contract and safe capture-start reservation, including the narrow placeholder grammar and no-overwrite invariant.
- Keywords: add, canalyzer, style, recording, configuration, collision, safe, acquisition, naming, peaklive
- Use when: Adding recording configuration, filename-template handling, capture-target reservation, or related profile persistence.
- Skip when: Changing capture formats, raw-frame semantics, rotation thresholds, replay, or decoded export behaviour alone.

# Needs
- Give the operator one clear Recording settings route for each measurement profile, with recording enablement, output folder selection, filename template, visible iteration control, reset action, and immediate filename preview.
- Use a small domain naming service rather than Qt widgets or the acquisition controller to interpret recording templates and produce safe capture paths.
- Prevent an acquisition from overwriting prior evidence: select the first free iteration at acquisition start, reserve it atomically before the recorder writes, and persist the next suggested iteration.
- Keep the existing receive-only acquisition, ASC/TRC writer behaviour, rotation, profile persistence, localization, and headless Qt testability intact.

# Context
- MeasurementProfile already persists RecordingSettings with enabled, directory, filename_template, iteration, capture_format, and rotation thresholds. The default template currently contains date, time, profile, iteration, and segment fields.
- AscRecorder currently expands its own template and uses a suffix-based collision fallback. That protects a single target but does not implement the requested visible iteration progression, first-free search, or an atomic reservation shared with session start.
- AcquisitionSession starts the recorder before it passes frames to presentation, so filename resolution and reservation belong immediately before recorder start, not in the UI or after a bounded display buffer.
- AcquisitionBar exposes profile, channel, bitrate, capture format, lifecycle, and export controls, but offers no Recording settings action or editor. Existing profile changes are persisted through the window/controller path.
- The app is a native PySide6 desktop application. QFileDialog.getExistingDirectory is the appropriate folder chooser, while business logic must remain usable without Qt and be covered by deterministic filesystem tests.
- The worktree has unrelated replay and external-artifact changes. Delivery must not modify, stage, or discard them.

# Acceptance criteria
- AC1: A profile-scoped Recording settings surface is reachable from the application menu or acquisition controls before acquisition starts and exposes enable recording, Folder with Browse, Filename template, iteration, Reset, format-aware read-only preview, validation feedback, and localized accessible labels/tooltips.
- AC2: Browse opens a directory-only QFileDialog and commits only a selected folder; cancelling leaves the profile unchanged. Recording fields round-trip through profile persistence and switching profiles restores each profile's independent values.
- AC3: A Qt-independent RecordingNaming service expands only the documented placeholders {date}, {time}, {profile}, {iteration:03}, optional Python-compatible numeric widths, and {segment:02}; it yields a safe filename below the selected directory and reports malformed, unsupported, empty, or path-escaping templates clearly.
- AC4: The preview reacts immediately to template, folder, profile, iteration, segment, and capture-format changes, uses a clearly defined preview clock, never creates a file, and shows the same filename syntax that acquisition will use.
- AC5: On acquisition start, the service searches from the profile iteration for the first unoccupied filename, considering final files and in-progress reservation/partial files. It atomically reserves that exact candidate before the writer opens it, so concurrent starts or a crash cannot overwrite an existing acquisition.
- AC6: After a successful reservation, the persisted profile iteration becomes the next candidate. If files for 012 and 013 exist and 014 is free, recording uses 014 and the next visible iteration is 015. Reset restarts the search at one rather than permitting an overwrite.
- AC7: SessionController and the recorder consume the reservation without duplicating template parsing or changing raw-frame ordering, ASC/TRC output, rotation semantics, error handling, or the existing incomplete-capture truthfulness contract. Failed startup releases an unused reservation or leaves recoverable evidence that is never mistaken for a completed capture.
- AC8: Focused unit, service, profile-persistence, and offscreen UI tests cover formatting, sanitization and rejection cases, preview non-mutation, first-free search, atomic collision handling, restart after a reserved/partial file, reset behaviour, directory cancellation, profile switching, accessibility, and regression of current acquisition/ASC tests.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_013_peaklive_configurable_and_collision_safe_acquisition_recording`
- Architecture decision(s): (none yet)

# References
- src/peaklive/domain/models.py
- src/peaklive/services/profiles.py
- src/peaklive/services/acquisition.py
- src/peaklive/recording/asc.py
- src/peaklive/ui/main_window.py
- src/peaklive/ui/session_controller.py
- src/peaklive/ui/panels/acquisition_bar.py
- src/peaklive/ui/actions.py
- src/peaklive/i18n/en.json
- tests/test_profiles.py
- tests/test_acquisition.py
- tests/test_asc_recorder.py
- tests/test_ui_parity.py
- tests/test_ui_lifecycle.py

# Backlog
- `item_048_deliver_a_deterministic_recording_naming_and_reservation_service`
- `item_049_expose_profile_recording_settings_with_live_filename_preview`
