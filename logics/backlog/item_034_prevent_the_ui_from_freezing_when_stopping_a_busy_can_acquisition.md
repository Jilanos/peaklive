## item_034_prevent_the_ui_from_freezing_when_stopping_a_busy_can_acquisition - Prevent the UI from freezing when stopping a busy CAN acquisition
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 90%
> Complexity: High
> Theme: Operator workflow and runtime integration
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-28 09:36:11

# AI Context
- Summary: Bound GUI presentation work so a busy acquisition cannot defer Stop
  or terminal lifecycle feedback, without weakening lossless recording.
- Keywords: CAN, acquisition, stop, GUI, Qt, queued signals, coalescing,
  backpressure
- Use when: A high-rate live bus leaves Stop or UI feedback delayed by queued
  frame rendering.
- Skip when: The only delay is inside adapter connect/disconnect with no visual
  frame backlog.

# Problem
Keep all received frames durably recorded while bounding presentation work sent to the GUI thread.
Make Stop actionable promptly on a busy bus and ensure the GUI event loop remains responsive throughout shutdown.
Prevent obsolete queued visual updates from delaying the terminal lifecycle state after Stop.

# Scope
- In:
  - A bounded, coalesced worker-to-GUI frame delivery path that keeps recording
    before presentation and never drops worker-owned acquisition data.
  - Generation-aware invalidation of obsolete presentation work after Stop and
    prompt terminal lifecycle delivery.
  - A deterministic offscreen 20,000-frame burst test with Stop latency and
    event-loop responsiveness assertions.
- Out:
  - CAN configuration, PCAN driver changes, transmission, workspace redesign,
    and changes to recording formats or capture completeness.

# Acceptance criteria
- AC1: Under a deterministic high-rate burst, the GUI processes a Stop request within a bounded interval and continues servicing a responsiveness timer while acquisition stops.
- AC2: Frames handed to the acquisition worker continue to be recorded losslessly; only stale or coalesced presentation work may be dropped or superseded.
- AC3: Once Stop is requested, queued visual frame updates from that generation cannot indefinitely delay the stopped, failed, or degraded lifecycle state.
- AC4: Normal-rate acquisition, display-only filtering, trace selection, graphs, recording, and PCAN adapter semantics remain unchanged.
- AC5: Headless regression coverage reproduces the burst condition and proves the timing bound without requiring connected hardware.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Under a deterministic high-rate burst, the GUI processes a Stop request within a bounded interval and continues servicing a responsiveness timer while acquisition stops.
- request-AC2 -> This backlog slice. Proof: AC2: Frames handed to the acquisition worker continue to be recorded losslessly; only stale or coalesced presentation work may be dropped or superseded.
- request-AC3 -> This backlog slice. Proof: AC3: Once Stop is requested, queued visual frame updates from that generation cannot indefinitely delay the stopped, failed, or degraded lifecycle state.
- request-AC4 -> This backlog slice. Proof: AC4: Normal-rate acquisition, display-only filtering, trace selection, graphs, recording, and PCAN adapter semantics remain unchanged.
- request-AC5 -> This backlog slice. Proof: AC5: Headless regression coverage reproduces the burst condition and proves the timing bound without requiring connected hardware.

# Decision framing
- Product framing: Not needed
- Product signals: (none detected)
- Product follow-up: No product brief follow-up is expected based on current signals.
- Architecture framing: Not needed
- Architecture signals: (none detected)
- Architecture follow-up: No architecture decision follow-up is expected based on current signals.

# Links
- Product brief(s): `prod_007_prevent_the_ui_from_freezing_when_stopping_a_busy_can_acquisition`
- Architecture decision(s): (none yet)
- Request: `req_007_prevent_ui_freeze_when_stopping_busy_can_acquisition`
- Primary task(s): `task_008_prevent_the_ui_from_freezing_when_stopping_a_busy_can_acquisition`

# Priority
- Priority: High
- Rationale: A busy bus can make the only stop control unavailable for more
  than 20 seconds, blocking safe bench operation.

# Notes
- Hybrid rationale: Derived from request `req_007_prevent_ui_freeze_when_stopping_busy_can_acquisition` and kept bounded to one coherent delivery slice.
- Source file: `logics/request/req_007_prevent_ui_freeze_when_stopping_busy_can_acquisition.md`.
- Generated locally by logics-manager.

# Tasks
- `task_008_prevent_the_ui_from_freezing_when_stopping_a_busy_can_acquisition`
