## item_011_upgrade_acquisition_setup_controls - Upgrade acquisition setup controls
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 95%
> Confidence: 90%
> Progress: 70%
> Complexity: Medium
> Theme: Acquisition configuration UX
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-24 14:35:25

# AI Context
- Summary: Exposes bitrate, channel, passive listen-only, normal receive with ACK, recording, and receive-only safety state before live acquisition starts.
- Keywords: upgrade, acquisition, setup, controls
- Use when: Changing the acquisition setup panel, controller mode labels, bitrate selection, profile persistence for acquisition options, or no-transmit UI guarantees.
- Skip when: Implementing DBC catalog behavior, signal explorer hierarchy, plotting, or purely offline replay workflows.

# Problem
- PeakLive exposes acquisition start/stop but not a complete configuration surface for bitrate and controller acknowledgement semantics.
- Operators need a safe distinction between application receive-only, passive listen-only, and normal receive with ACK.

# Scope
- In:
  - Add a compact acquisition setup panel with channel, bitrate, controller mode, recording enabled state, and profile summary.
  - Expose passive listen-only and normal receive with controller acknowledgement as explicit mutually exclusive controller modes.
  - Show application receive-only status as a non-toggleable MVP safety invariant and keep transmit controls absent.
  - Support bitrate selection from supported common rates and clear unsupported-configuration feedback.
  - Persist acquisition options in named profiles and restore them without initiating hardware connection.
  - Optionally run a live PCAN smoke test capped at 2 minutes for channel/mode feedback; fake-adapter tests remain the acceptance baseline.
- Out:
  - Adding any transmit API, transmit button, cyclic transmit, or frame editor.
  - Requiring a long load test or bus-disruptive normal receive validation on an unsafe bus.
  - Adding CAN FD, LIN, or multiple active channels.

# Acceptance criteria
- AC1: The setup panel presents channel, bitrate, passive listen-only, normal receive with ACK, recording, and application receive-only status before Start Acquisition.
- AC2: Starting acquisition applies the visible options and emits clear connected/error status without mutating Qt widgets from adapter code.
- AC3: Unsupported bitrate or unavailable controller mode produces an actionable, non-crashing UI message.
- AC4: Profile persistence restores acquisition options and still never auto-connects on startup.
- AC5: Tests cover option persistence, mode labelling, unsupported configuration, and absence of transmit affordances.

# AC Traceability
- request-AC3 -> This backlog slice. Proof: AC1: The setup panel presents channel, bitrate, passive listen-only, normal receive with ACK, recording, and application receive-only status before Start Acquisition.
- request-AC6 -> This backlog slice. Proof: AC2: Starting acquisition applies the visible options and emits clear connected/error status without mutating Qt widgets from adapter code.
- request-AC8 -> This backlog slice. Proof: AC3: Unsupported bitrate or unavailable controller mode produces an actionable, non-crashing UI message.
- request-AC9 -> This backlog slice. Proof: AC4: Profile persistence restores acquisition options and still never auto-connects on startup.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_002_peaklive_cantracediag_grade_diagnostic_workspace`
- Architecture decision(s): (none yet)
- Request: `req_001_bring_peaklive_ux_to_cantracediag_parity`
- Primary task(s): `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta`

# Priority
- Priority: High - operators must understand hardware mode before starting live capture.
- Rationale: Set by scaffold input or defaulted for grooming.
