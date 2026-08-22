## item_002_integrate_robust_classic_usb_can_acquisition - Integrate robust Classic USB CAN acquisition
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 15%
> Complexity: High
> Theme: CAN acquisition
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-22 12:10:33

# AI Context
- Summary: Adds the first capability-driven Windows Classic USB CAN adapter with explicit controller modes, assisted bitrate scan, bus states, and reconnect behaviour.
- Keywords: integrate, robust, classic, usb, can, acquisition
- Use when: Working on device discovery, bitrate/controller configuration, receive workers, timestamps, driver errors, disconnect, or hardware acceptance.
- Skip when: Implementing UI-only filtering, DBC decoding, replay formats, plotting, or frame transmission.

# Problem
- The application needs reliable access to the initial Windows USB CAN adapter without coupling the UI to one vendor API.

# Scope
- In:
  - Capability-driven adapter port and first Classic USB Windows implementation.
  - Channel discovery, manual 125/250/500/1000 kbit/s rates, normal receive and passive listen-only when supported.
  - Advisory bitrate scan, timestamps, bus/error events, disconnect, bounded retry, and reconnect.
  - Fake and hardware-in-loop acceptance harnesses.
- Out:
  - CAN FD, multiple active channels, frame transmission, and non-initial production adapters.

# Acceptance criteria
- AC1: The adapter enumerates supported channels and capability flags and rejects unsupported configurations explicitly.
- AC2: Start Acquisition applies a visible saved profile and connects at 125/250/500/1000 kbit/s, while Stop Acquisition closes the session; both produce normalized state events without touching Qt objects from the adapter worker.
- AC3: Assisted scan evaluates configured common rates in passive mode when supported and returns evidence, confidence, and inconclusive reasons.
- AC4: Disconnect, reconnect, warning, passive, bus-off, and driver overrun scenarios produce deterministic domain events and actionable UI state.
- AC5: Receive-only and passive listen-only semantics are named and tested independently; no transmit API is reachable from the MVP UI.

# AC Traceability
- request-AC2 -> This backlog slice. Proof: AC1: The adapter enumerates supported channels and capability flags and rejects unsupported configurations explicitly.
- request-AC3 -> This backlog slice. Proof: AC2: Manual bitrate connection produces normalized frames and state events without touching Qt objects from the adapter worker.
- request-AC4 -> This backlog slice. Proof: AC3: Assisted scan evaluates configured common rates in passive mode when supported and returns evidence, confidence, and inconclusive reasons.
- request-AC14 -> This backlog slice. Proof: AC4: Disconnect, reconnect, warning, passive, bus-off, and driver overrun scenarios produce deterministic domain events and actionable UI state.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_001_peaklive_windows_can_workstation`
- Architecture decision(s): (none yet)
- Request: `req_000_deliver_the_peaklive_windows_can_workstation_mvp`
- Primary task(s): `task_001_orchestrate_the_peaklive_windows_can_workstation_mvp`

# Priority
- Priority: High — live hardware access and transparent bus state are the defining MVP capability.
- Rationale: Set by scaffold input or defaulted for grooming.
