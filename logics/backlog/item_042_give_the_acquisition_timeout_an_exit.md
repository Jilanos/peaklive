## item_042_give_the_acquisition_timeout_an_exit - Give the acquisition timeout an exit
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Recoverable acquisition lifecycle
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: Makes the TIMED_OUT phase recoverable in-process and gives a slow or absent adapter connect a bounded, restartable failure instead of a phase with no exit.
- Keywords: acquisition, timeout, exit
- Use when: Working on AcquisitionLifecycle phase policy, the shutdown timeout, the connect path, or the wording the UI uses about a driver that has not returned.
- Skip when: Claiming the driver handle was released, reclaiming an OS resource held by a blocked driver call, or adding acquisition modes.

# Problem
- services/lifecycle.py:36-41 excludes TIMED_OUT from both STARTABLE_PHASES and STOPPABLE_PHASES, so an overrun shutdown disables Start permanently and refuses Stop, with closing the application as the documented remedy.
- The usual entry is upstream and not the timeout's fault: session.start() calls can.Bus(), which is not interruptible, so a stop requested while starting has no effect until the driver returns, and the timeout is unavoidable.
- The generation model already makes a late signal from an abandoned worker harmless, so the dead end is a policy choice rather than a safety requirement.

# Scope
- In:
  - An explicit operator action that leaves TIMED_OUT and returns to a startable state without restarting the process, abandoning the old worker through the existing mechanism and opening a fresh adapter.
  - A UI statement of what remains uncertain after that action, specifically that the previous driver handle may still be held.
  - A bounded connect path so that an absent or unresponsive adapter resolves into a restartable failure state instead of a timeout dead end, and a stop requested while starting is honoured or explained.
  - Lifecycle tests for the recovery action, for a stop during starting, and for a connect that never returns.
- Out:
  - Guaranteeing that the driver released its handle, or reclaiming an operating-system resource held by a blocked driver call.
  - Adding new acquisition modes, bitrate behaviour, or adapter vendors.
  - Changing the meaning of the settled, failed, and stopped phases.

# Acceptance criteria
- AC1: From TIMED_OUT, a documented operator action returns the application to a startable state in the same process, and a subsequent acquisition runs on a fresh adapter and a new generation.
- AC2: The UI states plainly what is uncertain after that recovery, without claiming the previous driver handle was released.
- AC3: A connect that is slow, absent, or failing resolves into a bounded restartable failure state, and a Stop issued during the starting phase is either honoured or explained to the operator.
- AC4: Lifecycle tests cover recovery from timeout, stop during starting, connect that never returns, and repeated start attempts after each, with no orphan worker and no duplicate terminal result.
- AC5: A late signal from an abandoned worker after recovery cannot alter the state of the newer generation.

# AC Traceability
- request-AC5 -> This backlog slice. Proof: AC1: From TIMED_OUT, a documented operator action returns the application to a startable state in the same process, and a subsequent acquisition runs on a fresh adapter and a new generation.
- request-AC6 -> This backlog slice. Proof: AC2: The UI states plainly what is uncertain after that recovery, without claiming the previous driver handle was released.
- request-AC15 -> This backlog slice. Proof: AC3: A connect that is slow, absent, or failing resolves into a bounded restartable failure state, and a Stop issued during the starting phase is either honoured or explained to the operator.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_011_peaklive_freeze_free_and_self_diagnosing_workstation`
- Architecture decision(s): (none yet)
- Request: `req_011_eliminate_the_remaining_peaklive_freezes_dead_ends_and_silent_failures_found_by_the_ui_thread_audit`
- Primary task(s): `task_012_deliver_a_freeze_free_self_diagnosing_peaklive_runtime`

# Priority
- Priority: High - a live application whose only remaining action is to close it is the reported symptom, and closing it is the path this request is also repairing.
- Rationale: Set by scaffold input or defaulted for grooming.
