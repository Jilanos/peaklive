## item_010_deliver_multi_dbc_library_and_conflict_management - Deliver multi-DBC library and conflict management
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 95%
> Confidence: 90%
> Progress: 0%
> Complexity: High
> Theme: DBC workflow
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: Adds an operator-facing multi-DBC library with multi-select loading, enable/remove state, parse diagnostics, duplicates, and deterministic conflict resolution.
- Keywords: deliver, multi, dbc, library, conflict, management
- Use when: Working on DBC loading, profile DBC state, DBC library UI, parse diagnostics, duplicate handling, or arbitration-ID conflict workflows.
- Skip when: Changing only acquisition controls, graph rendering, panel layout, or visual styling that does not affect DBC state or decoding ambiguity.

# Problem
- PeakLive currently has a basic single-file load action and does not expose a full operator-facing DBC library workflow.
- Real sessions need multiple loaded DBCs, visible origin, add/remove/disable state, and deterministic conflict handling.

# Scope
- In:
  - Support selecting and loading multiple DBC files in one UI action.
  - Maintain a profile/session DBC library with ordered DBC entries, active/enabled state, parse status, content hash, source filename, and loaded signal counts.
  - Expose clickable DBC rows or headers so operators can enable, disable, remove, and inspect DBCs without losing selected plots unnecessarily.
  - Surface parse diagnostics, encoding fallback behavior, duplicate detection, and unsupported file errors as panel-local messages.
  - Provide a conflict resolution UI for non-equivalent arbitration-ID definitions, with deterministic saved choices in the profile.
  - Keep raw frames intact when decoding is ambiguous, disabled, or failed.
- Out:
  - Editing DBC file contents.
  - Copying private DBC contents into the repository.
  - Network DBC libraries, cloud catalogs, or automatic online DBC lookup.

# Acceptance criteria
- AC1: Operators can load at least three DBC files in one operation and see each DBC with filename, enabled state, signal count, parse state, and duplicate/conflict indicators.
- AC2: Removing or disabling a DBC updates decode availability and signal navigation while preserving raw trace data and unaffected plotted signals.
- AC3: Non-equivalent message conflicts block ambiguous decoding until the operator selects a DBC mapping; equivalent definitions do not create noisy conflicts.
- AC4: Conflict choices persist in the selected profile and restore without auto-connecting to hardware.
- AC5: Tests cover multi-select loading, CP-1252/Latin-1 DBC text, duplicate handling, enable/disable/remove behavior, and conflict resolution.

# AC Traceability
- request-AC2 -> This backlog slice. Proof: AC1: Operators can load at least three DBC files in one operation and see each DBC with filename, enabled state, signal count, parse state, and duplicate/conflict indicators.
- request-AC4 -> This backlog slice. Proof: AC2: Removing or disabling a DBC updates decode availability and signal navigation while preserving raw trace data and unaffected plotted signals.
- request-AC8 -> This backlog slice. Proof: AC3: Non-equivalent message conflicts block ambiguous decoding until the operator selects a DBC mapping; equivalent definitions do not create noisy conflicts.
- request-AC9 -> This backlog slice. Proof: AC4: Conflict choices persist in the selected profile and restore without auto-connecting to hardware.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_002_peaklive_cantracediag_grade_diagnostic_workspace`
- Architecture decision(s): (none yet)
- Request: `req_001_bring_peaklive_ux_to_cantracediag_parity`
- Primary task(s): `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta`

# Priority
- Priority: High - DBC workflow is the first operator-facing blocker after live acquisition.
- Rationale: Set by scaffold input or defaulted for grooming.
