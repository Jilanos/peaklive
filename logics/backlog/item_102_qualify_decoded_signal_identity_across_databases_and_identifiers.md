## item_102_qualify_decoded_signal_identity_across_databases_and_identifiers - Qualify decoded signal identity across databases and identifiers
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: High
> Theme: Stable decoded-signal provenance
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-07 15:06:53

# AI Context
- Summary: Replace human-name-only signal keys with stable database-and-frame-qualified identities across selection, persistence, decode, series, graphs, measurements, and export.
- Keywords: signal-identity, dbc-provenance, duplicate-name, series-key, profile-migration, unit-isolation
- Use when: Changing SignalRef, signal explorer state, decoded series, graph selection, measurement/export keys, or legacy favorite/displayed-signal migration.
- Skip when: Renaming source DBC definitions, merging signals semantically, or changing CAN frame identity without touching decoded-signal keys.

# Problem
- The selection key and series key are message.signal even though the explorer can display multiple database definitions containing that name.
- Different frame identifiers, database hashes, units, and values can therefore share one favorite, one shown state, one SeriesStore entry, one graph, and one export stream.
- Persisted profiles need a deterministic compatibility path from legacy unqualified names.

# Scope
- In:
  - Define one stable provenance-qualified signal identifier covering database definition and CAN message identity independently of the human-readable label.
  - Use the identifier consistently in references, explorer actions, profile persistence, live decode, deferred decode, series, graph synchronization, measurements, and export.
  - Keep concise labels while exposing enough provenance to distinguish collisions to operators and assistive technology.
  - Provide a deterministic migration or explicit ambiguity outcome for legacy displayed and favorite signal names.
  - Prepare duplicate-name and profile-migration regression coverage for final-phase execution only.
- Out:
  - Renaming source DBC messages or signals, changing decoded values, or forcing verbose provenance into every compact label.
  - Merging semantically similar signals automatically across different definitions.
  - Executing tests before cross-layer signal identity implementation is complete.

# Acceptance criteria
- AC1: Same-named signals from different database definitions or frame identities remain distinct in selection, persistence, series, graphs, measurements, and export.
- AC2: Each distinct signal retains its own decoded values and unit, and the operator can identify its provenance when names collide.
- AC3: Legacy unqualified profile entries migrate deterministically when unique and produce an explicit safe outcome when ambiguous.
- AC4: Duplicate-name, unit-isolation, deferred-decode, and persistence tests execute only at the final verification gate.

# AC Traceability
- request-AC10 -> This backlog slice. Proof: AC1: Same-named signals from different database definitions or frame identities remain distinct in selection, persistence, series, graphs, measurements, and export.
- request-AC13 -> This backlog slice. Proof: AC4: Duplicate-name, unit-isolation, deferred-decode, and persistence tests execute only at the final verification gate.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_018_peaklive_trustworthy_measurement_identity_and_recoverable_local_evidence`
- Architecture decision(s): (none yet)
- Request: `req_019_eliminate_peaklive_second_pass_integrity_identity_and_recovery_gaps`
- Primary task(s): `task_019_implement_every_second_pass_peaklive_integrity_and_recovery_correction`

# Priority
- Priority: High - same-named definitions can currently merge unrelated values and units into one analytical series without warning.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_019_implement_every_second_pass_peaklive_integrity_and_recovery_correction`

# Notes
- Task `task_019_implement_every_second_pass_peaklive_integrity_and_recovery_correction` was finished via `logics-manager flow finish task` on 2026-09-07.
