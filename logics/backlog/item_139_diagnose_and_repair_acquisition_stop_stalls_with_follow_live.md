## item_139_diagnose_and_repair_acquisition_stop_stalls_with_follow_live - Diagnose and repair acquisition stop stalls with Follow live
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 95%
> Complexity: High
> Theme: Stop responsiveness and lifecycle correctness
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-16 14:38:21

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

# Findings

## Diagnosed cause
- `WorkspaceSession._acquisition_finished` settled the whole live presentation queue inside the worker's `finished` slot (`while _presentation_queue_pending(): _drain_presentation_frames()`). Each 256-frame slice repainted every curve and could block the GUI thread for `HistoryWriter.submit`'s full 5 s backpressure budget, so no paint and no input were processed for the entire drain. Up to 4096 frames could be queued, so the stall scaled with the write cost the operator's disk was paying.
- Follow live is not a factor. Off, full and trailing produce the same wind-down behaviour before and after the repair, so the operator's hypothesis is not supported by the measurements below.
- Secondary: the pre-repair wind-down reached `stopped` with history batches still unwritten, so the shell reported a success it had not yet earned.

## Fixture
- Synthetic only; no physical adapter. `BurstAdapter` saturates the bus through the ordinary acquisition/worker/handoff lifecycle, an 8-message DBC gives 9 displayed lanes, and `HistoricalSignalStore.append_many` is delayed to stand in for the SQL cost of a dense capture on a slow disk. The external `.asc`/sidecar captures were inspected but hold no stop-click timestamp or Follow-live state, so none of them reproduces a live stop; replaying one exercises the replay path, not this one.
- Regression coverage lives in `tests/test_stop_responsiveness.py`; 6 of its 9 cases fail against the pre-repair commit and all 9 pass with the repair.

## Measured evidence (Linux, offscreen Qt, 6 s saturated run, 120 ms per persisted batch)
| Build | Follow | Click-to-feedback | Max GUI heartbeat gap | Total wind-down | History batches settled/submitted |
| --- | --- | --- | --- | --- | --- |
| Before | off | 128 ms | 2218 ms | 2.25 s | 55/64 |
| Before | full | 133 ms | 2197 ms | 2.23 s | 56/65 |
| Before | trailing | 129 ms | 2191 ms | 2.23 s | 57/66 |
| After | off | 5 ms | 90 ms | 3.35 s | 64/64 |
| After | full | 27 ms | 87 ms | 3.42 s | 65/65 |
| After | trailing | 28 ms | 90 ms | 3.42 s | 64/64 |

- Worst single event-loop turn after the repair, by stage: `_ingest_frames` 57 ms, `_finalize_step` 17 ms, `_settle_presentation` 7 ms.
- Slower disk (400 ms per batch): before, 6957 ms frozen; after, 97 ms maximum gap across an 11.0 s wind-down with the progress bar visible from 8 ms.
- Deliberately delayed path (1500 ms per batch, 30 s run): 39.2 s wind-down, 108 ms maximum heartbeat gap, progress visible from 13 ms, all 46 batches durably settled before `stopped`. The stall bound measures absence of progress rather than elapsed time, so a legitimately slow save is never cut off.

## Remaining limits
- No confirmation on the operator's own PCAN hardware; the original adapter was not available. The synthetic fixture drives the same worker, handoff, ingest and persistence path, but driver-side latency is not reproduced.
- The operator's own Follow-live state and stop-click timestamp at the time of the reported freeze remain unknown.

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
