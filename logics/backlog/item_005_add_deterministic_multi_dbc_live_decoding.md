## item_005_add_deterministic_multi_dbc_live_decoding - Add deterministic multi-DBC live decoding
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: DBC decoding
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-22 11:48:50

# AI Context
- Summary: Adds a content-addressed multi-DBC catalog, explicit arbitration-ID conflict resolution, and demand-driven live decoding without changing raw frames.
- Keywords: add, deterministic, multi, dbc, live, decoding
- Use when: Implementing DBC import, selection, conflicts, multiplexing, physical values, enums, decode failures, or live decode performance.
- Skip when: Working only on raw acquisition/recording, plot rendering mechanics, replay parsing, or Windows packaging.

# Problem
- Multiple DBCs may define the same arbitration ID differently, and decoding all signals on every frame wastes live compute.

# Scope
- In:
  - Content-addressed DBC catalog, parse diagnostics, ordered databases, and deterministic conflict resolution.
  - Correct signed, scaled, endian, enum, and multiplexed signal decoding supported by the selected library.
  - Demand-driven live decode for visible columns, inspected messages, selected plots, and exports.
  - DBC library and selection persistence without copying private DBCs into the repository.
- Out:
  - DBC editing, network databases, and diagnostic protocol interpretation.

# Acceptance criteria
- AC1: Users can load, order, disable, remove, and inspect multiple DBC files with actionable parse diagnostics.
- AC2: Non-equivalent arbitration-ID conflicts block ambiguous decoding until a deterministic mapping is selected.
- AC3: Fixture tests cover signed, scaled, endian, enum, multiplexed, unknown, malformed, and conflicting definitions.
- AC4: Decode failures never mutate or discard the raw frame and are isolated to the affected definition.
- AC5: Live decoding is demand-driven and exposes throughput/latency measurements under the reference load.

# AC Traceability
- request-AC8 -> This backlog slice. Proof: AC1: Users can load, order, disable, remove, and inspect multiple DBC files with actionable parse diagnostics.
- request-AC9 -> This backlog slice. Proof: AC2: Non-equivalent arbitration-ID conflicts block ambiguous decoding until a deterministic mapping is selected.
- request-AC11 -> This backlog slice. Proof: AC3: Fixture tests cover signed, scaled, endian, enum, multiplexed, unknown, malformed, and conflicting definitions.
- request-AC12 -> This backlog slice. Proof: AC4: Decode failures never mutate or discard the raw frame and are isolated to the affected definition.
- request-AC14 -> This backlog slice. Proof: AC5: Live decoding is demand-driven and exposes throughput/latency measurements under the reference load.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_001_peaklive_windows_can_workstation`
- Architecture decision(s): (none yet)
- Request: `req_000_deliver_the_peaklive_windows_can_workstation_mvp`
- Primary task(s): `task_001_orchestrate_the_peaklive_windows_can_workstation_mvp`

# Priority
- Priority: High — decoded engineering values are required before live plots or useful exports can ship.
- Rationale: Set by scaffold input or defaulted for grooming.
