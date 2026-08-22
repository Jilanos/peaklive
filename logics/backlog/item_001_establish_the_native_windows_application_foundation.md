## item_001_establish_the_native_windows_application_foundation - Establish the native Windows application foundation
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 85%
> Complexity: Medium
> Theme: Desktop foundation
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-22 12:10:33

# AI Context
- Summary: Creates the native Qt shell, clean domain boundaries, local settings contract, fake adapter, and continuous test baseline used by every later slice.
- Keywords: establish, native, windows, application, foundation
- Use when: Bootstrapping the executable application, core package layout, visual workspace, settings, logging, or baseline CI.
- Skip when: Adding physical hardware access, production recording, DBC semantics, replay, or installer qualification after the foundation exists.

# Problem
- The repository has no executable desktop skeleton, dependency contract, application state model, or test harness.

# Scope
- In:
  - Python and PySide6 package layout with domain, application, adapter, infrastructure, and UI boundaries.
  - Local path policy, named measurement-profile schema, last-profile restoration without auto-connect, English UI, structured logging, fake adapter, and CI test baseline.
  - Instrument-style shell matching the companion product's visual vocabulary.
- Out:
  - Physical CAN acquisition, complete feature panels, and production installer polish.

# Acceptance criteria
- AC1: A developer can create the pinned environment, run the desktop shell, and execute unit and Qt smoke tests from documented commands.
- AC2: Domain modules do not import Qt or a concrete vendor API, and a deterministic fake adapter can drive the shell.
- AC3: Settings use documented local paths, persist schema-versioned named profiles, restore the last selected profile, and never auto-connect at startup.
- AC4: The shell establishes the trace, signal explorer, plots, and inspector workspace regions with keyboard-accessible navigation.
- AC5: CI enforces formatting, static checks, unit tests, and a headless UI launch test.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: A developer can create the pinned environment, run the desktop shell, and execute unit and Qt smoke tests from documented commands.
- request-AC12 -> This backlog slice. Proof: AC2: Domain modules do not import Qt or a concrete vendor API, and a deterministic fake adapter can drive the shell.
- request-AC13 -> This backlog slice. Proof: AC3: Settings use documented local paths, persist schema-versioned non-sensitive state, and never auto-connect at startup.
- request-AC14 -> This backlog slice. Proof: AC4: The shell establishes the trace, signal explorer, plots, and inspector workspace regions with keyboard-accessible navigation.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_001_peaklive_windows_can_workstation`
- Architecture decision(s): (none yet)
- Request: `req_000_deliver_the_peaklive_windows_can_workstation_mvp`
- Primary task(s): `task_001_orchestrate_the_peaklive_windows_can_workstation_mvp`

# Priority
- Priority: High — every vertical feature depends on a deterministic desktop runtime and domain boundary.
- Rationale: Set by scaffold input or defaulted for grooming.
