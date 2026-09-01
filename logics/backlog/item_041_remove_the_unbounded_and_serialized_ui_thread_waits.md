## item_041_remove_the_unbounded_and_serialized_ui_thread_waits - Remove the unbounded and serialized UI-thread waits
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 55%
> Complexity: High
> Theme: Bounded UI thread
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-01 11:40:43

# AI Context
- Summary: Removes the only two operator-reachable paths where the Qt event loop stops: the untimed catalog wait reached from a profile switch or a DBC load, and the four chained waits in closeEvent totalling up to 16 s.
- Keywords: remove, unbounded, serialized, thread, waits
- Use when: Touching catalog_controller's synchronous preparation paths, the close path, or anything that calls QThread.wait() from the UI thread.
- Skip when: Trying to interrupt a cantools parse mid-file, replace the DBC parser, or forcefully terminate an external driver's thread.

# Problem
- ui/catalog_controller.py:82 waits on the catalog worker with no timeout, reached from _load_profile_dbcs and _load_dbc_path. The preceding cancel cannot interrupt an in-progress cantools parse, because the cancel flag is only tested between files, so the wait lasts as long as the parse: measured at 129 ms per 1000 messages, meaning seconds for a real vehicle DBC.
- ui/main_window.py:371-400 chains four bounded waits totalling up to 16 s on the UI thread, which an operator reads as a hung application and answers by force-closing it.
- Workers that do not return within their wait are abandoned to outlive the window, but nothing observes them before interpreter exit, so a worker blocked in the driver leaves a windowless process holding the CAN channel.

# Scope
- In:
  - Route profile-restore and single-path DBC loading through the existing serialized catalog operation queue, so the synchronous preparation paths and their waits disappear.
  - Generation-guarded asynchronous commit for those paths, preserving the atomic adoption of catalog, profile, panels, selection, and graphs.
  - A close path that returns control immediately: request shutdown from every worker, hide the window, and settle under one documented global budget before quitting.
  - Exit-time reporting of any worker still alive, and a documented operator outcome for the case where an external driver never returns.
  - Tests with deliberately slow catalog preparation that assert UI ticks continue during a profile switch and during close, and that no wait is unbounded.
- Out:
  - Interrupting cantools mid-parse or replacing the DBC parser.
  - Forcefully terminating an external driver's thread or process.
  - Changing the bounded-retention capacities or the decode behaviour.

# Acceptance criteria
- AC1: No operator-reachable UI-thread path waits on a worker without a bounded timeout; a deliberately slow catalog operation cannot stop event processing during startup, a profile switch, or a DBC load.
- AC2: A superseded or cancelled catalog operation leaves the catalog, profile, panels, selection, and graphs consistent, and the last commit wins deterministically under rapid consecutive operations.
- AC3: Closing the window returns control within one documented global budget rather than a sum of per-worker waits, and recording evidence is finalized or explicitly marked incomplete.
- AC4: Any worker alive at exit is reported in the diagnostic log, and the documented exit path leaves no windowless process unexplained.
- AC5: Offscreen tests prove sustained event processing during profile switch, DBC load, and close, using controllably slow preparation.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: No operator-reachable UI-thread path waits on a worker without a bounded timeout; a deliberately slow catalog operation cannot stop event processing during startup, a profile switch, or a DBC load.
- request-AC2 -> This backlog slice. Proof: AC2: A superseded or cancelled catalog operation leaves the catalog, profile, panels, selection, and graphs consistent, and the last commit wins deterministically under rapid consecutive operations.
- request-AC3 -> This backlog slice. Proof: AC3: Closing the window returns control within one documented global budget rather than a sum of per-worker waits, and recording evidence is finalized or explicitly marked incomplete.
- request-AC4 -> This backlog slice. Proof: AC4: Any worker alive at exit is reported in the diagnostic log, and the documented exit path leaves no windowless process unexplained.
- request-AC15 -> This backlog slice. Proof: AC5: Offscreen tests prove sustained event processing during profile switch, DBC load, and close, using controllably slow preparation.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_011_peaklive_freeze_free_and_self_diagnosing_workstation`
- Architecture decision(s): (none yet)
- Request: `req_011_eliminate_the_remaining_peaklive_freezes_dead_ends_and_silent_failures_found_by_the_ui_thread_audit`
- Primary task(s): `task_012_deliver_a_freeze_free_self_diagnosing_peaklive_runtime`

# Priority
- Priority: High - these are the only remaining paths where the Qt event loop stops outright, and they are reached by two routine actions: switching profiles and closing the window.
- Rationale: Set by scaffold input or defaulted for grooming.
