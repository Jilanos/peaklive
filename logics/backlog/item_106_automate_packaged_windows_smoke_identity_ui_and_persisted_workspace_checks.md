## item_106_automate_packaged_windows_smoke_identity_ui_and_persisted_workspace_checks - Automate packaged Windows smoke, identity, UI, and persisted-workspace checks
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: High
> Theme: Packaged application functional smoke
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-08 14:14:11

# AI Context
- Summary: Proves that the delivered desktop executable starts, identifies itself, exposes usable controls, and safely persists only isolated test profiles.
- Keywords: automate, packaged, windows, smoke, identity, persisted, workspace, checks
- Use when: Implementing or reviewing non-hardware Windows UI automation and viewport evidence.
- Skip when: Testing CAN input, replay fixtures, output files, or cosmetic changes outside required command reachability.

# Problem
- Current coverage is predominantly source-run/offscreen and cannot prove that the packaged executable presents a working Windows desktop application.
- Build identity and layout requirements are documented but not captured as executable-specific release evidence.
- Profile persistence and corrupt-store recovery need verification with an isolated local Windows data directory.

# Scope
- In:
  - Select a maintained Windows UI-automation mechanism compatible with the artifact and document the dependency/setup boundary.
  - Automate launch, visible main-window readiness, disconnected initial state, About identity, clean close, restart, and isolated profile persistence/recovery.
  - Exercise documented keyboard shortcuts and reachable command surfaces without requiring a CAN adapter.
  - Capture layout screenshots and minimum geometry/assertions at 1024x768, 1280x720, and 1600x900 at 100/125/150 percent scaling.
  - Record automation limitations explicitly and leave subjective readability decisions as guided checks with screenshot evidence.
- Out:
  - Pixel-perfect visual regression across all GPUs/themes.
  - Automated verification of Windows accessibility tools beyond accessible-name/control discovery.
  - Live CAN acquisition or replay/export fixtures.

# Acceptance criteria
- AC1: The packaged executable launches and closes cleanly under a fresh sandbox, with no Python interpreter dependency in the launch path.
- AC2: The About dialog and status identity match the verified build metadata and identify packaged execution.
- AC3: Each required viewport/scale produces a screenshot, and automation flags clipped, inaccessible, or unreachable mandatory controls.
- AC4: A saved isolated profile survives restart; a deliberately corrupt test-only store follows the documented recovery behaviour without touching any real profile store.

# AC Traceability
- request-AC2 -> This backlog slice. Proof: AC1: The packaged executable launches and closes cleanly under a fresh sandbox, with no Python interpreter dependency in the launch path.
- request-AC3 -> This backlog slice. Proof: AC2: The About dialog and status identity match the verified build metadata and identify packaged execution.
- request-AC6 -> This backlog slice. Proof: AC3: Each required viewport/scale produces a screenshot, and automation flags clipped, inaccessible, or unreachable mandatory controls.
- request-AC7 -> This backlog slice. Proof: AC4: A saved isolated profile survives restart; a deliberately corrupt test-only store follows the documented recovery behaviour without touching any real profile store.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_019_peaklive_windows_executable_qualification_kit`
- Architecture decision(s): (none yet)
- Request: `req_020_qualify_the_peaklive_ci_windows_executable_with_a_reproducible_functional_test_battery`
- Primary task(s): `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`

# Priority
- Priority: High - the most basic release failures are launch, stale build identity, unusable layout, or profile corruption before CAN hardware is involved.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`

# Notes
- Task `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery` was finished via `logics-manager flow finish task` on 2026-09-08.
