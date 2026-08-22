## item_003_build_the_complete_and_recoverable_recording_pipeline - Build the complete and recoverable recording pipeline
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 35%
> Complexity: High
> Theme: Capture integrity
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-22 12:10:33

# AI Context
- Summary: Persists every adapter-delivered frame and observable acquisition event before display filtering, with explicit integrity and crash-recovery state.
- Keywords: build, complete, recoverable, recording, pipeline
- Use when: Implementing ASC output, event sidecars, writer backpressure, partial-session recovery, disk failures, or recorder benchmarks.
- Skip when: Changing only the bounded live presentation, offline reader, DBC decoder, plots, or installer shell.

# Problem
- UI pressure and filtering must not silently remove frames or errors from saved sessions.

# Scope
- In:
  - Dedicated bounded recorder queue and worker, interoperable ASC writer, JSONL event sidecar, flush policy, and metrics.
  - Partial-session markers, atomic finalization, interrupted-session detection, and recovery workflow.
  - Profile-controlled recording lifecycle, collision-safe date/time/profile/configurable-iteration/segment filename expansion, 2 GiB default rotation, and configurable 10 GiB warning/2 GiB stop free-space thresholds.
  - Disk-full, permission, driver-loss, and recorder-overflow behaviour.
  - Reference-load benchmark and capture-integrity comparison harness.
- Out:
  - Compressed proprietary formats and cloud-backed capture storage.

# Acceptance criteria
- AC1: When enabled by the visible profile, Start Acquisition opens recording before UI filtering and Stop Acquisition finalizes it; every adapter-delivered frame is written to ASC.
- AC2: Driver, connection, and recording events are represented in ASC comments where portable and in a same-basename JSONL sidecar.
- AC3: An overrun, queue overflow, disk error, or unclean close marks the session incomplete and is never reported as a clean capture.
- AC4: Restart detects partial sessions and offers non-destructive recovery/finalization while preserving original artifacts.
- AC5: Deterministic saturated/error traffic plus the available real capture baseline support a documented 60-minute load test that demonstrates recorder integrity and records queue high-water and driver-loss evidence.
- AC6: Default 2 GiB rotation produces ordered session segments without overwrite; low space warns at 10 GiB, stops recording at 2 GiB, and marks the session incomplete while thresholds remain configurable.

# AC Traceability
- request-AC4 -> This backlog slice. Proof: AC1: Recording receives normalized events before all UI filtering and writes every adapter-delivered frame to ASC.
- request-AC5 -> This backlog slice. Proof: AC2: Driver, connection, and recording events are represented in ASC comments where portable and in a same-basename JSONL sidecar.
- request-AC6 -> This backlog slice. Proof: AC3: An overrun, queue overflow, disk error, or unclean close marks the session incomplete and is never reported as a clean capture.
- request-AC13 -> This backlog slice. Proof: AC4: Restart detects partial sessions and offers non-destructive recovery/finalization while preserving original artifacts.
- request-AC14 -> This backlog slice. Proof: AC5: The documented 60-minute reference load demonstrates recorder integrity and records queue high-water and driver-loss evidence.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_001_peaklive_windows_can_workstation`
- Architecture decision(s): (none yet)
- Request: `req_000_deliver_the_peaklive_windows_can_workstation_mvp`
- Primary task(s): `task_001_orchestrate_the_peaklive_windows_can_workstation_mvp`

# Priority
- Priority: High — trustworthy evidence must exist before visualization work can be accepted.
- Rationale: Set by scaffold input or defaulted for grooming.
