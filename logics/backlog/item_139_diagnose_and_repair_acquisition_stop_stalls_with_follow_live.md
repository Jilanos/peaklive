## item_139_diagnose_and_repair_acquisition_stop_stalls_with_follow_live - Diagnose and repair acquisition stop stalls with Follow live
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Stop responsiveness and lifecycle correctness
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-16 12:17:37

# AI Context
- Summary: Diagnose and repair acquisition stop stalls with Follow live.
- Keywords: diagnose, repair, acquisition, stalls, follow, live
- Use when: Implementing or validating the responsive-stop and measurement-workspace follow-up to task_029 and task_030.
- Skip when: Changing unrelated decoding, recording formats, or data retention policies.

# Problem
- The operator reports a freeze when stopping acquisition, apparently more often with Follow live; no root cause is confirmed.
- An asynchronous stop request alone does not prove the GUI remains responsive during completion and historical rendering.

# Scope
- In:
  - Build a repeatable synthetic/fake-adapter reproduction with bounded timeouts, many frames and multiple displayed lanes; compare all three follow configurations and visible/hidden measurement statistics.
  - Instrument click-to-feedback, GUI heartbeat, worker stop acknowledgment, ingestion backlog/drain, recording flush, history readiness and final graph/statistics rendering. Capture thread stacks on a stall and distinguish deadlock, starvation and expensive GUI computation.
  - Choose the smallest repair justified by evidence; keep GUI widget access on its thread, prevent unbounded GUI waits and bound/coalesce presentation work without discarding accepted acquisition/history/recording data.
  - Define terminal follow behavior: stop scheduling live presentation after completion, retain the final extent/samples and current follow preference, and preserve a manually selected viewport.
  - Exercise delayed completion, worker timeout/recovery, recording on/off, history failure, empty sessions, rapid duplicate Stop and repeated restarts; retain GUI-owned GC and generation fencing.
  - Record before/after evidence and add a regression that exposes the diagnosed defect. Hardware confirmation is supplementary if the original adapter is unavailable; state that limitation.
- Out:
  - Assuming Follow live or GC is the cause without evidence.
  - Suppressing the symptom by globally disabling Follow live or dropping retained samples.
  - Unrelated worker or plotting rewrites.

# Acceptance criteria
- AC1: A documented fixture compares Follow off/full/trailing and records diagnostic stage timings and stack evidence.
- AC2: Under the recorded stress fixture, feedback is at most 200 ms and maximum GUI heartbeat gap is at most 250 ms during stop; driver latency can exceed these bounds without blocking the GUI.
- AC3: Final data and recording checks match accepted input; a timeout keeps unsafe restart disabled and stale callbacks cannot change a newer generation.
- AC4: A meaningful regression fails without the repair and passes with it; final graph access, A/B values and subsequent start/stop remain usable.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: A documented fixture compares Follow off/full/trailing and records diagnostic stage timings and stack evidence.
- request-AC2 -> This backlog slice. Proof: AC2: Under the recorded stress fixture, feedback is at most 200 ms and maximum GUI heartbeat gap is at most 250 ms during stop; driver latency can exceed these bounds without blocking the GUI.
- request-AC3 -> This backlog slice. Proof: AC3: Final data and recording checks match accepted input; a timeout keeps unsafe restart disabled and stale callbacks cannot change a newer generation.
- request-AC8 -> This backlog slice. Proof: AC4: A meaningful regression fails without the repair and passes with it; final graph access, A/B values and subsequent start/stop remain usable.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_030_peaklive_responsive_stop_and_readable_measurement_controls`
- Architecture decision(s): (none yet)
- Request: `req_032_restore_responsive_acquisition_stop_and_polish_the_measurement_workspace`
- Primary task(s): `task_031_deliver_responsive_stop_and_polished_measurement_workspace_controls`

# Priority
- Priority: High - an unresponsive stop blocks the operator and obscures acquisition safety.
- Rationale: Set by scaffold input or defaulted for grooming.
