## item_105_create_an_isolated_powershell_qualification_harness_for_a_ci_built_peaklive_executable - Create an isolated PowerShell qualification harness for a CI-built PeakLive executable
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Reproducible executable preflight and evidence collection
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-08 14:14:11

# AI Context
- Summary: Establishes the safe, hash-verified PowerShell execution boundary and evidence contract shared by every Windows qualification lane.
- Keywords: create, isolated, powershell, qualification, harness, built, peaklive, executable
- Use when: Building the harness entry point, isolated data setup, result aggregation, or failure artifact collection.
- Skip when: Adding application feature tests that run directly from source and require no packaged-binary evidence.

# Problem
- The build metadata and executable sit outside the repository and the existing smoke instructions are manual.
- A bench run can accidentally use global application data, overwrite evidence, or report a stale executable without a hash-verified manifest.
- Failure evidence is not standardized across launch, UI, replay, and hardware cases.

# Scope
- In:
  - Implement a PowerShell entry point with explicit paths for executable, metadata, sandbox, artifacts, and test-lane selection.
  - Validate build metadata, file hash, free disk space, writable sandbox, and required fixtures before launch.
  - Create a unique artifact directory containing environment facts, structured case results, stdout/stderr where available, screenshots, and a final manifest.
  - Set PEAKLIVE_DATA_DIR only for the child executable and ensure cleanup never touches an operator profile directory.
  - Define stable case identifiers, timeout semantics, pass/fail/not-run/blocked status, and a non-zero exit code only for failed mandatory cases.
- Out:
  - Installing drivers or changing Windows security policy.
  - Deleting historical acceptance artifacts or user data.
  - Embedding test-only diagnostics into production release code.

# Acceptance criteria
- AC1: Given the supplied PeakLive.exe and PeakLive.build.txt, preflight rejects an identifier or SHA-256 mismatch before PeakLive launches.
- AC2: Each run creates a unique evidence root and cannot write outside its declared sandbox/artifact roots.
- AC3: The harness emits valid machine-readable summary and readable report even when a test times out or PowerShell encounters an exception.
- AC4: Harness unit/contract tests exercise metadata parsing, unsafe-path rejection, status aggregation, and failure collection.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Given the supplied PeakLive.exe and PeakLive.build.txt, preflight rejects an identifier or SHA-256 mismatch before PeakLive launches.
- request-AC2 -> This backlog slice. Proof: AC2: Each run creates a unique evidence root and cannot write outside its declared sandbox/artifact roots.
- request-AC6 -> This backlog slice. Proof: AC3: The harness emits valid machine-readable summary and readable report even when a test times out or PowerShell encounters an exception.
- request-AC7 -> This backlog slice. Proof: AC4: Harness unit/contract tests exercise metadata parsing, unsafe-path rejection, status aggregation, and failure collection.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_019_peaklive_windows_executable_qualification_kit`
- Architecture decision(s): (none yet)
- Request: `req_020_qualify_the_peaklive_ci_windows_executable_with_a_reproducible_functional_test_battery`
- Primary task(s): `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`

# Priority
- Priority: High - without a binary-first, isolated harness, results can be attributed to stale profiles, a different executable, or a source environment rather than the CI artifact.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`

# Notes
- Task `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery` was finished via `logics-manager flow finish task` on 2026-09-08.
