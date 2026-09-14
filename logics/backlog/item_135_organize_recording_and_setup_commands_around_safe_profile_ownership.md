## item_135_organize_recording_and_setup_commands_around_safe_profile_ownership - Organize recording and setup commands around safe profile ownership
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 95%
> Confidence: 95%
> Progress: 100%
> Complexity: High
> Theme: Menu ownership and acquisition configuration
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-14 16:30:50
> Owner: paul.mondou@circle-mobility.com

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: organize, recording, setup, commands, around, safe, profile, ownership
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- View duplicates lifecycle and recording actions, while File owns profile save-as and the top bar exposes configuration that does not need permanent screen space.
- Channel, bitrate, controller mode, and capture format have different profile ownership and safety constraints but are presented together without a clear menu hierarchy.

# Scope
- In:
  - Create the three confirmed top-level menu-bar menus Recording, Setup, and DBC; remove Start, Stop, and Recording settings from View and move Save measurement setup from File to Setup without changing its profile save-as behavior.
  - Keep compact header Start/Stop controls as the direct lifecycle surface; style Stop with an explicit destructive/running semantic only while its lifecycle action is enabled.
  - Represent channel, bitrate, and acquisition mode as Setup cascading menus whose immediate choices are selectable by mouse hover/pointer and keyboard arrows/Enter, with check state or another unambiguous current-value marker.
  - Move ASC/TRC selection into Recording settings and remove its top-bar selector; persist it with the existing recording profile contract and prevent mid-session edits from mutating an active worker profile.
  - Remove or relocate superseded top-bar controls while retaining profile selection, session state, load/open/export access, accessibility names, shortcuts, and safe lifecycle gating.
  - Add i18n keys and headless assertions for menu membership, submenus, selected state, persistence, keyboard activation, and Start/Stop phase styling.
- Out:
  - Adding hardware channel discovery, arbitrary custom bitrates, or additional controller modes beyond the supported profile model.
  - Changing acquisition worker ownership, recording file contents, or adapter connection behavior.
  - Changing the profile save-as behavior behind Save measurement setup.

# Acceptance criteria
- AC1: File no longer contains Save measurement setup and View no longer contains Start, Stop, or Recording settings; Recording, Setup, and DBC are top-level menu-bar menus, and the relocated commands preserve their existing behavior.
- AC2: Setup's channel, bitrate, and mode choices are cascading submenus with persistent current selection, keyboard navigation, accessible labels, and disabled/gated states while a session makes edits unsafe.
- AC3: Recording settings own ASC/TRC selection; no capture-format selector remains in the top bar and a recording starts with the stored selected format.
- AC4: Header Stop is red and enabled only in a stoppable acquisition phase, returns to its non-running appearance outside that phase, and menu and header actions remain synchronized.
- AC5: Existing profile save, profile switching, invalid recording-template handling, replay/acquisition mutual exclusion, and passive-mode tests remain green.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: File no longer contains Save measurement setup and View no longer contains Start, Stop, or Recording settings; Recording, Setup, and DBC are top-level menu-bar menus, and the relocated commands preserve their existing behavior.
- request-AC2 -> This backlog slice. Proof: AC2: Setup's channel, bitrate, and mode choices are cascading submenus with persistent current selection, keyboard navigation, accessible labels, and disabled/gated states while a session makes edits unsafe.
- request-AC3 -> This backlog slice. Proof: AC3: Recording settings own ASC/TRC selection; no capture-format selector remains in the top bar and a recording starts with the stored selected format.
- request-AC9 -> This backlog slice. Proof: AC5: Existing profile save, profile switching, invalid recording-template handling, replay/acquisition mutual exclusion, and passive-mode tests remain green.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_028_peaklive_focused_operator_controls_and_bounded_measurement_canvas`
- Architecture decision(s): (none yet)
- Request: `req_030_refine_peaklive_operator_menus_catalog_access_and_graph_navigation`
- Primary task(s): `task_029_deliver_peaklive_operator_menu_catalog_and_graph_canvas_refinement`

# Priority
- Priority: High - misplaced lifecycle and bus controls make critical operator actions harder to find and consume measurement workspace.
- Rationale: Set by scaffold input or defaulted for grooming.

# Validation
- Wave 1 implemented: Recording/Setup top-level menus added, Save measurement setup moved to Setup, Start/Stop/Recording settings moved to Recording, capture-format (ASC/TRC) relocated from AcquisitionBar into RecordingSettingsDialog, channel/bitrate/controller-mode mirrored as Setup cascading submenus (keyboard/pointer accessible, check-marked, gated by lifecycle), header Stop styled red only while stoppable. Evidence: full pytest suite green except one pre-existing timing-flaky perf test (test_trace_performance.py, also fails intermittently on the unmodified tree); ruff clean.

# Tasks
- `task_029_deliver_peaklive_operator_menu_catalog_and_graph_canvas_refinement`

# Notes
- Task `task_029_deliver_peaklive_operator_menu_catalog_and_graph_canvas_refinement` was finished via `logics-manager flow finish task` on 2026-09-14.
