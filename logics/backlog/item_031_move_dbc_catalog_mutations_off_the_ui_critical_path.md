## item_031_move_dbc_catalog_mutations_off_the_ui_critical_path - Move DBC catalog mutations off the UI critical path
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 35%
> Complexity: High
> Theme: Responsive DBC catalog
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-27 13:45:19

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: move, dbc, catalog, mutations, off, critical, path
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- DBC parse and catalog rebuild work runs synchronously from UI callbacks, then triggers multiple dependent view updates. Slow files or repeated mutations can block interaction and risk partial state updates.

# Scope
- In:
  - Background preparation for DBC parsing and derived catalog data, with UI-thread-only widget updates.
  - Serialized or generation-aware add/remove/enable/conflict operations, visible progress, cancellation before commit, and actionable parse/I/O errors.
  - Atomic commit of catalog, profile persistence, selected signals, conflicts, explorer, graph, and library-panel changes.
  - Synthetic large/slow/malformed DBC regression tests plus responsive UI assertions.
- Out:
  - Editing DBC source files, adding a DBC authoring workflow, or changing decode rules.
  - Loading DBCs from cloud services or network synchronization.

# Acceptance criteria
- AC1: Add, remove, enable, disable, and conflict-resolution workflows retain event-loop responsiveness under delayed parsing and expensive derived-data preparation.
- AC2: Progress and errors identify the operation and file; cancellation before commit leaves the prior catalog and persisted profile unchanged.
- AC3: Successful mutations atomically update the catalog, profile, DBC panel, signal explorer, selected signals, and graphs without stale callbacks or invalid Qt item access.
- AC4: Existing multi-DBC ordering, conflict behavior, raw-frame preservation, and profile restoration tests remain valid.
- AC5: Automated tests cover slow, malformed, and rapid consecutive DBC operations, proving both UI responsiveness and consistent final state.

# AC Traceability
- request-AC5 -> This backlog slice. Proof: AC1: Add, remove, enable, disable, and conflict-resolution workflows retain event-loop responsiveness under delayed parsing and expensive derived-data preparation.
- request-AC6 -> This backlog slice. Proof: AC2: Progress and errors identify the operation and file; cancellation before commit leaves the prior catalog and persisted profile unchanged.
- request-AC7 -> This backlog slice. Proof: AC3: Successful mutations atomically update the catalog, profile, DBC panel, signal explorer, selected signals, and graphs without stale callbacks or invalid Qt item access.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_006_peaklive_responsive_runtime_and_identifiable_builds`
- Architecture decision(s): (none yet)
- Request: `req_006_keep_peaklive_responsive_during_acquisition_dbc_changes_and_test_build_verification`
- Primary task(s): `task_006_deliver_responsive_peaklive_lifecycle_dbc_operations_and_build_identity`

# Priority
- Priority: High - loading or changing DBCs is a routine analysis action and must not turn the workstation into a non-responding application.
- Rationale: Set by scaffold input or defaulted for grooming.
