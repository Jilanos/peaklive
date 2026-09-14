## task_030_eliminate_the_qt_python_garbage_collection_lock_inversion - Eliminate the Qt Python garbage collection lock inversion
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: eliminate, python, garbage, collection, lock, inversion
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Record the native lock inversion evidence and add a deterministic thread-ownership regression.
- [ ] 2. Implement application-owned GUI collection with threshold-aware scheduling.
- [ ] 3. Validate Linux full suite and Windows regressions, record results, commit and push.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_138_own_cyclic_garbage_collection_on_the_qapplication_thread`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_138_own_cyclic_garbage_collection_on_the_qapplication_thread`. Proof deferred to slice closeout.
- request-AC2 -> `item_138_own_cyclic_garbage_collection_on_the_qapplication_thread`. Proof deferred to slice closeout.
- request-AC3 -> `item_138_own_cyclic_garbage_collection_on_the_qapplication_thread`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_031_prevent_qt_destruction_deadlocks_during_background_python_allocation`
- Product brief(s): `prod_029_peaklive_gui_owned_cyclic_memory_reclamation`
- Architecture decision(s): (none yet)
