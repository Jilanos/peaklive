## item_032_expose_a_trustworthy_in_application_build_identifier - Expose a trustworthy in-application build identifier
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 70%
> Complexity: Medium
> Theme: Build traceability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-27 13:45:19

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: expose, trustworthy, application, build, identifier
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Operators cannot currently verify which installed or copied PeakLive executable they are exercising, and the version declaration is duplicated across package files.

# Scope
- In:
  - One authoritative runtime version/build metadata path used by package metadata, application UI, About dialog, and PyInstaller packaging.
  - A discreet always-visible identifier and richer About display that remain legible on supported Windows display scaling.
  - A documented version/build suffix convention for test rebuilds and a Windows packaged-executable smoke check.
  - Automated tests that assert metadata/UI consistency.
- Out:
  - Automatic update delivery, online version checks, licensing, telemetry, or a release portal.
  - A prominent diagnostic banner that consumes workspace needed for CAN analysis.

# Acceptance criteria
- AC1: A subtle version/build identifier is visible in the normal application chrome and available in About without covering operational controls.
- AC2: Package metadata, runtime value, visible UI, About information, and PyInstaller build resolve to the same authoritative identifier.
- AC3: The build convention can distinguish a test rebuild from a prior executable and is documented for the operator who supplies test feedback.
- AC4: Unit/UI tests and a packaged Windows smoke procedure demonstrate that the shown identifier matches the executable under test.

# AC Traceability
- request-AC8 -> This backlog slice. Proof: AC1: A subtle version/build identifier is visible in the normal application chrome and available in About without covering operational controls.
- request-AC9 -> This backlog slice. Proof: AC2: Package metadata, runtime value, visible UI, About information, and PyInstaller build resolve to the same authoritative identifier.
- request-AC10 -> This backlog slice. Proof: AC3: The build convention can distinguish a test rebuild from a prior executable and is documented for the operator who supplies test feedback.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_006_peaklive_responsive_runtime_and_identifiable_builds`
- Architecture decision(s): (none yet)
- Request: `req_006_keep_peaklive_responsive_during_acquisition_dbc_changes_and_test_build_verification`
- Primary task(s): `task_006_deliver_responsive_peaklive_lifecycle_dbc_operations_and_build_identity`

# Priority
- Priority: Medium - identifying the exact executable materially improves test feedback, after acquisition reliability is restored.
- Rationale: Set by scaffold input or defaulted for grooming.
