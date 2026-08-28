## task_008_prevent_the_ui_from_freezing_when_stopping_a_busy_can_acquisition - Prevent the UI from freezing when stopping a busy CAN acquisition
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 60%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-08-28 09:36:11
> Owner: Codex

# AI Context
- Summary: Implement coalesced, generation-aware UI delivery so Stop stays
  responsive under a busy CAN receive loop while recording remains lossless.
- Keywords: Qt, QThread, queued signals, acquisition, Stop, GUI, coalescing
- Use when: Implementing the high-rate acquisition shutdown responsiveness fix.
- Skip when: Investigating slow native adapter shutdown without queued UI frame
  work.

# Definition of Done (DoD)
- [ ] The backlog scope is implemented.
- [ ] Acceptance criteria are covered.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# Backlog
- `item_034_prevent_the_ui_from_freezing_when_stopping_a_busy_can_acquisition`

# Acceptance criteria
- AC1: Under a deterministic high-rate burst, the GUI processes a Stop request within a bounded interval and continues servicing a responsiveness timer while acquisition stops.
- AC2: Frames handed to the acquisition worker continue to be recorded losslessly; only stale or coalesced presentation work may be dropped or superseded.
- AC3: Once Stop is requested, queued visual frame updates from that generation cannot indefinitely delay the stopped, failed, or degraded lifecycle state.
- AC4: Normal-rate acquisition, display-only filtering, trace selection, graphs, recording, and PCAN adapter semantics remain unchanged.
- AC5: Headless regression coverage reproduces the burst condition and proves the timing bound without requiring connected hardware.

# Plan
- [ ] Add a failing synthetic-burst regression around the acquisition worker and
  session controller: request Stop at 0.5 s during 20,000 frames, assert the
  callback runs within one second and a 10 ms UI probe continues to tick.
- [ ] Separate durable recording from UI presentation delivery, coalesce pending
  visual batches per acquisition generation, and retain all existing
  normal-rate frame/decode behavior.
- [ ] Give Stop and terminal lifecycle transitions priority by invalidating
  superseded visual work for the stopping generation; preserve stale-generation
  guards and bounded native-shutdown behavior.
- [ ] Run focused offscreen lifecycle/UI tests plus the full test and lint
  suite; record the measured timing proof before closing the task.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_007_prevent_ui_freeze_when_stopping_busy_can_acquisition`
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)
