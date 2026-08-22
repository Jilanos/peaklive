## item_007_implement_incremental_asc_and_trc_replay_with_decoded_export - Implement incremental ASC and TRC replay with decoded export
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 85%
> Complexity: High
> Theme: Offline analysis
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-22 12:10:33

# AI Context
- Summary: Opens ASC and supported text TRC captures incrementally, preserves anomalies, supports bounded navigation, and streams decoded CSV/Parquet exports.
- Keywords: implement, incremental, asc, trc, replay, decoded, export
- Use when: Implementing offline readers, indexes, malformed-record handling, time navigation, chunked decode, cancellation, or decoded exports.
- Skip when: Changing live adapter behaviour, active recording, display-only live filters, plot rendering, or installer mechanics.

# Problem
- Engineers need one installed tool for live work and large offline captures without browser memory limits.

# Scope
- In:
  - Incremental ASC and supported text TRC readers normalized to domain events.
  - Progressive indexing, time-window navigation, anomaly retention, and cancelable file opening.
  - Chunked decode and streamed CSV/Parquet export for selected signals and time ranges.
  - Compatibility fixtures shared conceptually with the companion reader.
- Out:
  - Every proprietary capture format and full-file eager decode.

# Acceptance criteria
- AC1: Valid ASC and supported text TRC fixtures normalize to equivalent domain frames and preserve timestamps and flags.
- AC2: Malformed lines become navigable anomalies when safe and never shift or corrupt subsequent valid frames.
- AC3: Large traces open and navigate without loading the complete file or decoded dataset into UI memory.
- AC4: CSV and Parquet exports stream selected signals and time ranges and are validated against decoded fixture values.
- AC5: Replay and export operate without network access and expose cancel/progress/error states.

# AC Traceability
- request-AC8 -> This backlog slice. Proof: AC1: Valid ASC and supported text TRC fixtures normalize to equivalent domain frames and preserve timestamps and flags.
- request-AC10 -> This backlog slice. Proof: AC2: Malformed lines become navigable anomalies when safe and never shift or corrupt subsequent valid frames.
- request-AC11 -> This backlog slice. Proof: AC3: Large traces open and navigate without loading the complete file or decoded dataset into UI memory.
- request-AC13 -> This backlog slice. Proof: AC4: CSV and Parquet exports stream selected signals and time ranges and are validated against decoded fixture values.
- request-AC14 -> This backlog slice. Proof: AC5: Replay and export operate without network access and expose cancel/progress/error states.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_001_peaklive_windows_can_workstation`
- Architecture decision(s): (none yet)
- Request: `req_000_deliver_the_peaklive_windows_can_workstation_mvp`
- Primary task(s): `task_001_orchestrate_the_peaklive_windows_can_workstation_mvp`

# Priority
- Priority: Medium — installed offline analysis completes the product but can build on the live domain pipeline.
- Rationale: Set by scaffold input or defaulted for grooming.
