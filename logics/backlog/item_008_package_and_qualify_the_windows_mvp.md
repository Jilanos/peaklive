## item_008_package_and_qualify_the_windows_mvp - Package and qualify the Windows MVP
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Windows delivery
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-22 11:49:07

# AI Context
- Summary: Produces the self-contained Windows installer and repeatable clean-machine/hardware evidence required for the three-user MVP rollout.
- Keywords: package, qualify, windows, mvp
- Use when: Building distributable artifacts, detecting prerequisites, handling uninstall/local data, recording notices/provenance, or executing release qualification.
- Skip when: Developing unfinished domain, acquisition, recording, decoding, trace, plot, replay, or export functionality.

# Problem
- Source execution is not an acceptable delivery path for the target engineering users.

# Scope
- In:
  - Pinned production build, bundled Python/Qt runtime, Windows x64 installer, shortcuts, uninstall, and local-data retention policy.
  - Driver prerequisite detection and actionable launch diagnostics.
  - Clean-machine install smoke test, dependency notices, operator quick start, and repeatable hardware acceptance runbook.
  - Reference-load performance and reconnect qualification.
- Out:
  - Automatic updates, mandatory executable signing, enterprise deployment tooling, and public support commitments.

# Acceptance criteria
- AC1: The installer deploys, launches, and uninstalls on a clean supported Windows x64 machine without a separate Python installation.
- AC2: Missing or incompatible hardware drivers produce an actionable diagnostic while offline replay remains usable.
- AC3: Uninstall behaviour clearly offers or documents retention of captures, DBC references, and user settings.
- AC4: The documented hardware runbook verifies connect, 60-minute load, display latency, record integrity, physical reconnect, replay, and export.
- AC5: The release artifact contains version/build provenance and required third-party notices and passes the automated install smoke test.

# AC Traceability
> Shared proof: AC13, AC14, AC9

- request-AC1 -> This backlog slice. Proof: AC1: The installer deploys, launches, and uninstalls on a clean supported Windows x64 machine without a separate Python installation.
- request-AC2 -> This backlog slice. Proof: AC2: Missing or incompatible hardware drivers produce an actionable diagnostic while offline replay remains usable.
- request-AC4 -> This backlog slice. Proof: AC3: Uninstall behaviour clearly offers or documents retention of captures, DBC references, and user settings.
- request-AC6 -> This backlog slice. Proof: AC4: The documented hardware runbook verifies connect, 60-minute load, display latency, record integrity, physical reconnect, replay, and export.
- request-AC9 -> This backlog slice. Proof: AC5: The release artifact contains version/build provenance and required third-party notices and passes the automated install smoke test.
- request-AC13 -> This backlog slice. Proof: AC5: The release artifact contains version/build provenance and required third-party notices and passes the automated install smoke test.
- request-AC14 -> This backlog slice. Proof: AC5: The release artifact contains version/build provenance and required third-party notices and passes the automated install smoke test.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_001_peaklive_windows_can_workstation`
- Architecture decision(s): (none yet)
- Request: `req_000_deliver_the_peaklive_windows_can_workstation_mvp`
- Primary task(s): `task_001_orchestrate_the_peaklive_windows_can_workstation_mvp`

# Priority
- Priority: Medium — distribution follows feature integration but is required for the three-user rollout.
- Rationale: Set by scaffold input or defaulted for grooming.
