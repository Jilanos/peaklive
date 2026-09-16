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
> Indicators reviewed: 2026-09-16 13:45:24

# AI Context
- Summary: Diagnose and repair acquisition stop stalls with Follow live.
- Keywords: diagnose, repair, acquisition, stalls, follow, live
- Use when: Implementing or validating the responsive-stop and measurement-workspace follow-up to task_029 and task_030.
- Skip when: Changing unrelated decoding, recording formats, or data retention policies.

# Problem
- The operator reports a freeze when stopping acquisition, apparently more often with Follow live; no root cause is confirmed.
- An asynchronous stop request alone does not prove the GUI remains responsive during completion and historical rendering.

- Operator clarification (2026-09-16): the observed stop can leave the application unresponsive for more than 30 seconds. Feedback within 200 ms is accepted. The operation must either finish in less than 3 seconds or show an explicit saving/finalization popup or progress bar by the 3-second mark, while the GUI remains responsive.

# Scope
- In:
  - Start diagnosis from the external timestamp-prefix candidates and their matching sidecars, inspect any adjacent save-directory logs, and preserve original files unchanged. Use the existing freeze-diagnostics runbook as an investigation aid. Replaying an ASC alone does not reproduce live stop: feed representative data through the acquisition/fake-adapter lifecycle, compare Follow off/full/trailing, and record which original settings remain unknown. Do not commit raw captures; record anonymized metadata and derive a bounded regression fixture.
  - Implement a localized popup or progress bar for saving/finalization that is visible no later than 3 seconds after Stop if finalization is still pending; an inline progress bar is the default implementation choice. Show the actual phase, use measured progress when a total is known and indeterminate activity otherwise, and keep repaint/input processing alive. Never display fake percentages or success before durable recording/history completion; dismiss on success and show actionable timeout/error state on failure. Test both completion below 3 seconds and a deliberately delayed path beyond 30 seconds with visible ongoing feedback, plus the existing stuck-worker timeout policy. A progress indicator does not excuse blocking the GUI.
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
- AC2: Under the recorded stress fixture, feedback is at most 200 ms and maximum GUI heartbeat gap is at most 250 ms during stop. Completion takes less than 3 seconds or an explicit saving/finalization popup or progress bar appears by 3 seconds and stays responsive until completion or a surfaced timeout/error. Verify fast, delayed-over-30-second and stuck-worker paths; never report success before durable finalization.
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
