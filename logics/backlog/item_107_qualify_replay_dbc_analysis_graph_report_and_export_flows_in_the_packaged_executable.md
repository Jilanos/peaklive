## item_107_qualify_replay_dbc_analysis_graph_report_and_export_flows_in_the_packaged_executable - Qualify replay, DBC analysis, graph, report, and export flows in the packaged executable
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: High
> Theme: Fixture-driven end-to-end analysis
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-08 14:14:11

# AI Context
- Summary: Uses copied deterministic files to qualify the complete offline analysis path of the packaged executable and to preserve output evidence.
- Keywords: qualify, replay, dbc, analysis, graph, report, export, flows, packaged, executable
- Use when: Adding fixture-driven replay, DBC, analysis, graph, report, or export qualification cases.
- Skip when: Performing live PCAN acquisition or modifying decoder behaviour unrelated to the packaged acceptance workflow.

# Problem
- The repository has ASC and DBC inputs but no packaged-executable acceptance lane that proves a user can complete the core analysis workflow.
- Exports, cancellation, graphs, filters, and report are sensitive cross-layer flows that should leave tangible artifacts and screenshots.
- Fixtures must not be loaded or modified directly from the repository evidence directories.

# Scope
- In:
  - Curate small deterministic ASC/TRC and DBC fixture copies, including at least one event record and decoded signal.
  - Automate or guide open/replay, DBC load, filter changes, trace and inspector selection, signal selection, graph navigation, cursors, measurements, and diagnostic report.
  - Export CSV and Parquet into the run sandbox; validate schema, row count, expected signal identity, and no unintended overwrite on cancellation/failure paths.
  - Create screenshots and evidence links for each workflow checkpoint and compare output only against fixture-derived expectations.
- Out:
  - Benchmarking every possible DBC/capture size.
  - Changing decoder semantics, adding file formats, or testing unsupported captures.
  - Using production customer traces as committed test fixtures.

# Acceptance criteria
- AC1: The packaged executable completes the representative replay-to-report workflow from copied fixtures without a crash or a modal dead end.
- AC2: CSV and Parquet exports validate as readable outputs with the requested scope and do not replace a pre-existing sandbox sentinel during cancellation/failure tests.
- AC3: Trace, inspector, signal explorer, graphs, cursors, measurements, filters, and report each have an observable assertion or guided checkpoint.
- AC4: The lane records its fixture hashes, output hashes, screenshots, and expected-versus-observed result in the evidence manifest.

# AC Traceability
- request-AC4 -> This backlog slice. Proof: AC1: The packaged executable completes the representative replay-to-report workflow from copied fixtures without a crash or a modal dead end.
- request-AC6 -> This backlog slice. Proof: AC2: CSV and Parquet exports validate as readable outputs with the requested scope and do not replace a pre-existing sandbox sentinel during cancellation/failure tests.
- request-AC7 -> This backlog slice. Proof: AC3: Trace, inspector, signal explorer, graphs, cursors, measurements, filters, and report each have an observable assertion or guided checkpoint.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_019_peaklive_windows_executable_qualification_kit`
- Architecture decision(s): (none yet)
- Request: `req_020_qualify_the_peaklive_ci_windows_executable_with_a_reproducible_functional_test_battery`
- Primary task(s): `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`

# Priority
- Priority: High - replay and local analysis let the release prove most operator workflows deterministically without depending on a live bus.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`

# Notes
- Task `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery` was finished via `logics-manager flow finish task` on 2026-09-08.
