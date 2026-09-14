## task_030_eliminate_the_qt_python_garbage_collection_lock_inversion - Eliminate the Qt Python garbage collection lock inversion
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: Codex
> Indicators reviewed: 2026-09-14 18:15:53

# AI Context
- Summary: Prevent worker-triggered cyclic GC from destroying Qt wrappers and deadlocking the GUI against the Python GIL.
- Keywords: eliminate, python, garbage, collection, lock, inversion
- Use when: Investigating DBC worker hangs or changing QApplication cyclic collection ownership.
- Skip when: Changing decoding semantics or ordinary reference-counted object cleanup.

# Context
- Complete the native Qt/Python lock inversion repair identified in GitHub run 34858021301 and reproduced under Linux after the menu lifetime fixes.

# Plan
- [x] 1. Record the native lock inversion evidence and add a deterministic thread-ownership regression.
- [x] 2. Implement application-owned GUI collection with threshold-aware scheduling.
- [x] 3. Validate Linux full suite and Windows regressions, record results, commit and push.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_138_own_cyclic_garbage_collection_on_the_qapplication_thread`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_138_own_cyclic_garbage_collection_on_the_qapplication_thread`. Proof deferred to slice closeout.
- request-AC2 -> `item_138_own_cyclic_garbage_collection_on_the_qapplication_thread`. Proof deferred to slice closeout.
- request-AC3 -> `item_138_own_cyclic_garbage_collection_on_the_qapplication_thread`. Proof deferred to slice closeout.

# Validation
- 2026-09-14 Windows: `uv run python -m pytest -ra -o faulthandler_timeout=120 -o faulthandler_exit_on_timeout=true` with `QT_QPA_PLATFORM=offscreen`: 671 passed, 1 skipped, 9 xfailed, 3 xpassed in 323.88s; all exclusions are existing Windows offscreen layout quarantines.
- 2026-09-14 Linux (WSL Ubuntu, matching source and tests): same pytest command, 684 passed in 310.28s, including rapid consecutive DBC operations.
- `uv run ruff check .` passed on Windows and Linux; Logics lint and scoped flow validation passed; audit has no blockers (two unrelated existing warnings).
- command: `uv run python -m pytest -ra -o faulthandler_timeout=120 -o faulthandler_exit_on_timeout=true` | result: passed | date: 2026-09-14 | note: 2026-09-14 QT_QPA_PLATFORM=offscreen: Linux 684 passed in 310.28s; Windows 671 passed, 1 skipped, 9 xfailed, 3 xpassed in 323.88s. Ruff passed on both platforms. Implementation commit 58dbe1d.
- Finish workflow executed on 2026-09-14.
- Linked backlog/request close verification passed.

# Report
- Implemented one QApplication-owned, threshold-aware collection timer, installed before MainWindow starts workers. Automatic cyclic GC is disabled until application destruction restores the previous policy; reference counting is unchanged.
- Regression coverage verifies worker allocations do not reclaim Qt cycles, GUI-thread destruction, timer reuse, generation selection, and application teardown.
- Full Windows and Linux suites passed. The regression verifies destruction thread ownership deterministically; the Linux full suite also completes beyond the formerly hanging DBC test.
- Remaining limitation: explicit third-party `gc.collect()` calls and reference-counted destruction are outside this automatic cyclic collection policy.
- Finished on 2026-09-14.
- Linked backlog item(s): `item_138_own_cyclic_garbage_collection_on_the_qapplication_thread`
- Related request(s): `req_031_prevent_qt_destruction_deadlocks_during_background_python_allocation`

# Links
- Request: `req_031_prevent_qt_destruction_deadlocks_during_background_python_allocation`
- Product brief(s): `prod_029_peaklive_gui_owned_cyclic_memory_reclamation`
- Architecture decision(s): (none yet)
