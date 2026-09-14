## req_031_prevent_qt_destruction_deadlocks_during_background_python_allocation - Prevent Qt destruction deadlocks during background Python allocation
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 100%
> Confidence: 90%
> Complexity: Medium
> Theme: Runtime reliability
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.

# AI Context
- Summary: Prevent worker-triggered cyclic GC from destroying Qt wrappers and deadlocking the GUI against the Python GIL.
- Keywords: prevent, destruction, deadlocks, during, background, python, allocation
- Use when: Investigating DBC worker hangs or changing QApplication cyclic collection ownership.
- Skip when: Changing decoding semantics or ordinary reference-counted object cleanup.

# Needs
- Keep cyclic garbage collection of Qt wrappers on the GUI thread while workers parse or ingest data.

# Context
- GitHub run 34858021301 timed out inside the rapid consecutive DBC operations test.
- A Linux reproduction after menu lifetime repairs showed the GUI thread blocked in QObject destruction while the parser thread waited in Shiboken GilState::acquire during destruction of collected Qt wrappers.
- Menu leak repairs alone did not eliminate the reproduced deadlock. The native pytest watchdog now exits with stacks after 120 seconds.

# Acceptance criteria
- Background allocation cannot automatically collect GUI-owned Python cycles; Qt wrapper destruction from scheduled collection runs on the GUI thread.
- Collection remains enabled through a threshold-aware GUI timer owned once per QApplication, without one collector per window or collection after application destruction.
- Regression tests verify destruction thread ownership and collector reuse; full Linux and relevant Windows tests and Ruff pass.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_029_peaklive_gui_owned_cyclic_memory_reclamation`
- Architecture decision(s): (none yet)

# References
- src/peaklive/ui/main_window.py
- src/peaklive/services/dbc_worker.py
- .github/workflows/ci.yml

# Backlog
- `item_138_own_cyclic_garbage_collection_on_the_qapplication_thread`
