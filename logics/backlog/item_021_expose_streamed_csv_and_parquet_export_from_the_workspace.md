## item_021_expose_streamed_csv_and_parquet_export_from_the_workspace - Expose streamed CSV and Parquet export from the workspace
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Export
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-25 12:29:44

# AI Context
- Summary: Makes the existing peaklive.analysis.export writers reachable: an export dialog with signal selection, CSV or Parquet output, and A-B / visible-window / full-buffer scopes, streamed with bounded memory, reporting progress, and cancellable without leaving a partial file that looks complete.
- Keywords: export dialog, csv, parquet, export scope, A-B range, visible window, cancellation
- Use when: Wiring export from the UI, defining or changing export scopes, streaming and batching behavior, export progress and cancellation, or export error reporting.
- Skip when: Exporting raw undecoded frames to a new trace format, scheduled or recurring export, and any cloud or network destination.

# Problem
- peaklive.analysis.export provides export_csv and export_parquet, but no UI code path calls either, so the documented CSV/Parquet capability is unreachable.
- An analyst who has placed cursors has no way to get that exact range out of the application.

# Scope
- In:
  - Add an export dialog selecting the signals to export, the output format (CSV or Parquet), the destination path, and the range scope.
  - Support the range between cursors A and B, the visible time window, and the full retained buffer as scopes.
  - Stream rows into the existing batched writers so memory stays bounded for large ranges.
  - Report progress during export and allow cancellation, leaving no partial file presented as complete.
  - Report the written row count on success and the reason inline on failure, without echoing unexpected local paths into error text.
  - Default the signal selection to the currently shown signals.
- Out:
  - Export of raw undecoded frames to a new trace format.
  - Scheduled, recurring, or automated export.
  - Cloud or network export destinations.

# Acceptance criteria
- AC1: The export dialog is reachable from the workspace and defaults to the shown signals.
- AC2: Each of the three scopes produces exactly the rows in that range, verified against a fixture series.
- AC3: CSV and Parquet outputs are both produced and readable, with matching row counts.
- AC4: A large export streams with bounded memory and reports progress.
- AC5: Cancelling an export leaves no file that could be mistaken for a complete export, and the UI states the cancellation.
- AC6: A failing export reports the reason inline and keeps the workspace usable.
- AC7: Headless offscreen tests cover the dialog, all three scopes, both formats, cancellation, and failure.

# AC Traceability
- request-AC6 -> This backlog slice. Proof: AC1: The export dialog is reachable from the workspace and defaults to the shown signals.
- request-AC12 -> This backlog slice. Proof: AC2: Each of the three scopes produces exactly the rows in that range, verified against a fixture series.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_003_peaklive_analyst_measurement_and_reporting_workspace`
- Architecture decision(s): (none yet)
- Request: `req_002_complete_the_peaklive_analyst_workspace_to_cantracediag_parity`
- Primary task(s): `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Priority
- Priority: High - the export engine already exists and is unreachable from the UI.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Notes
- Task `task_003_deliver_the_peaklive_analyst_workspace_parity_wave` was finished via `logics-manager flow finish task` on 2026-08-25.
