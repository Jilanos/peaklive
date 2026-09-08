## item_110_add_a_payload_blind_passive_pcan_traffic_and_capture_progress_oracle - Add a payload-blind passive PCAN traffic and capture-progress oracle
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Privacy-preserving load and recording evidence
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-08 16:18:31

# AI Context
- Summary: Establishes aggregate-only PCAN load and owned-artifact progress evidence while preventing any raw vehicle data or transmit path from entering the MVP.
- Keywords: add, payload, blind, passive, pcan, traffic, capture, progress, oracle
- Use when: Implementing passive traffic aggregates, no-transmit protection, capture-growth classification, and evidence redaction.
- Skip when: Decoding, retaining, exporting, or comparing individual vehicle frames or DBC information.

# Problem
- An active bus can be silent at the selected bitrate, while a capture file can exist yet stop growing under backpressure or a stalled worker.
- Raw trace inspection would expose unnecessary vehicle data and is not needed to qualify PeakLive runtime behaviour.

# Scope
- In:
  - Open one explicitly passive PCAN receive channel and collect count, rate, first/last monotonic receive time, and driver-error aggregate only.
  - Prohibit CAN send APIs and verify the selected configuration is receive-only before sampling.
  - Track capture and sidecar artifact existence, size growth, final/partial state, and final hash/size without parsing frame lines.
  - Define configurable minimum-traffic and minimum-growth thresholds based on aggregate counts rather than identifiers or payload values.
  - Test redaction and no-transmit guard with fake PCAN adapters.
- Out:
  - Persisting raw bus frames, frame IDs, payloads, signal values, DBC files, or event text in the qualification evidence.
  - Comparing protocol semantics between independent adapters.
  - Sending a probe, remote request, or any frame to the vehicle.

# Acceptance criteria
- AC1: The oracle can prove active aggregate traffic or report traffic-absent without recording a single raw frame attribute.
- AC2: Attempts to invoke a send operation fail closed and leave no transmitted traffic path in the MVP.
- AC3: Capture progress is considered healthy only when the owned artifact grows across configured observation samples and finalizes/recoverably partializes after Stop.
- AC4: JSON/Markdown reports cannot contain payload, arbitration-ID, signal, or DBC fields by schema or tests.

# AC Traceability
- request-AC2 -> This backlog slice. Proof: AC1: The oracle can prove active aggregate traffic or report traffic-absent without recording a single raw frame attribute.
- request-AC3 -> This backlog slice. Proof: AC2: Attempts to invoke a send operation fail closed and leave no transmitted traffic path in the MVP.
- request-AC4 -> This backlog slice. Proof: AC3: Capture progress is considered healthy only when the owned artifact grows across configured observation samples and finalizes/recoverably partializes after Stop.
- request-AC5 -> This backlog slice. Proof: AC4: JSON/Markdown reports cannot contain payload, arbitration-ID, signal, or DBC fields by schema or tests.
- request-AC6 -> This backlog slice. Proof: AC4: JSON/Markdown reports cannot contain payload, arbitration-ID, signal, or DBC fields by schema or tests.
- request-AC7 -> This backlog slice. Proof: AC4: JSON/Markdown reports cannot contain payload, arbitration-ID, signal, or DBC fields by schema or tests.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_020_peaklive_ten_minute_black_box_vehicle_load_qualification`
- Architecture decision(s): (none yet)
- Request: `req_021_automate_a_ten_minute_black_box_peaklive_vehicle_load_qualification`
- Primary task(s): `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`

# Priority
- Priority: High - the test needs to prove that PeakLive is receiving and recording a live load without inspecting the vehicle's messages.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`

# Notes
- Task `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp` was finished via `logics-manager flow finish task` on 2026-09-08.
