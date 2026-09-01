## item_040_give_the_application_a_diagnostic_voice_before_changing_its_behaviour - Give the application a diagnostic voice before changing its behaviour
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 55%
> Complexity: Medium
> Theme: Runtime observability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-01 11:40:43

# AI Context
- Summary: Adds the local rotating log, the process-wide and per-thread exception hooks, the guarded profile write, and the console build target, so a freeze or a half-applied state leaves evidence on the operator's machine.
- Keywords: application, diagnostic, voice, before, changing, behaviour
- Use when: Diagnosing why the application wedged with no message, or before landing any other correction in this request, since each one needs evidence.
- Skip when: Adding remote crash reporting, telemetry, an in-application log viewer, or changing the default windowed packaging.

# Problem
- There is no logging in src/, no sys.excepthook and no threading.excepthook, and the packaged build has no console, so an unhandled exception in a Qt slot is swallowed into a stderr that does not exist. Verified on PySide6 6.11.2: a slot exception is printed and swallowed, leaving state half-applied, while a virtual-override exception terminates the process.
- The observable consequence is indistinguishable from a deliberate dead end: an exception swallowed in _acquisition_finished or _worker_phase_changed leaves the lifecycle unsettled, so Start stays disabled with no message and nothing to diagnose from.
- _save() writes profiles.json with no try/except and is reached from pointer-drag slots, where a scanner lock or a full disk raises OSError on a path the operator will never see.

# Scope
- In:
  - A local rotating diagnostic log at a documented path under the platform user-data directory, honouring PEAKLIVE_DATA_DIR, with the build identifier and the session start recorded.
  - Process-wide and per-thread exception hooks that log the traceback, and a visible non-blocking operator note when an exception reaches a UI path.
  - Guarded profile persistence: an I/O failure becomes a logged, visible, non-fatal note rather than a silent loss or a terminated process.
  - A documented console-enabled build target for bench diagnosis alongside the existing windowed build, and the py-spy live-attach procedure recorded in the runbook.
  - Tests that assert a raising slot leaves a log entry and a visible note, and that a failing profile write does not terminate the application or lose the in-memory state.
- Out:
  - Remote crash reporting, telemetry, or any network transmission of diagnostics.
  - A log viewer inside the application, or user-facing log level configuration UI.
  - Changing the windowed build's default packaging shape.

# Acceptance criteria
- AC1: The application writes a rotating diagnostic log to a documented local path, records the build identifier and session start, and creates no network dependency.
- AC2: Process-wide and per-thread exception hooks are installed before the first window is shown; a deliberately raising slot produces a log entry with a traceback and a visible operator note rather than a silent half-applied state.
- AC3: A deliberately failing profile write surfaces a visible non-fatal note, reaches the log, keeps the in-memory state, and does not terminate the application.
- AC4: A worker still running at application exit is named in the log with its identity and last known phase.
- AC5: The runbook documents the log path, the console build target, and the live-attach procedure for capturing a freeze in progress.

# AC Traceability
- request-AC4 -> This backlog slice. Proof: AC1: The application writes a rotating diagnostic log to a documented local path, records the build identifier and session start, and creates no network dependency.
- request-AC7 -> This backlog slice. Proof: AC2: Process-wide and per-thread exception hooks are installed before the first window is shown; a deliberately raising slot produces a log entry with a traceback and a visible operator note rather than a silent half-applied state.
- request-AC8 -> This backlog slice. Proof: AC3: A deliberately failing profile write surfaces a visible non-fatal note, reaches the log, keeps the in-memory state, and does not terminate the application.
- request-AC15 -> This backlog slice. Proof: AC4: A worker still running at application exit is named in the log with its identity and last known phase.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_011_peaklive_freeze_free_and_self_diagnosing_workstation`
- Architecture decision(s): (none yet)
- Request: `req_011_eliminate_the_remaining_peaklive_freezes_dead_ends_and_silent_failures_found_by_the_ui_thread_audit`
- Primary task(s): `task_012_deliver_a_freeze_free_self_diagnosing_peaklive_runtime`

# Priority
- Priority: High - every other correction in this request is an untestable hypothesis while a freeze leaves no trace on the operator's machine.
- Rationale: Set by scaffold input or defaulted for grooming.
