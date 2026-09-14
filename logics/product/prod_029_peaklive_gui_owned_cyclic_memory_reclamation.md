## prod_029_peaklive_gui_owned_cyclic_memory_reclamation - PeakLive GUI-owned cyclic memory reclamation
> Date: 2026-09-14
> Status: Proposed
> Related request: `req_031_prevent_qt_destruction_deadlocks_during_background_python_allocation`
> Related backlog: `item_138_own_cyclic_garbage_collection_on_the_qapplication_thread`
> Related task: `task_030_eliminate_the_qt_python_garbage_collection_lock_inversion`
> Related architecture: (none yet)
> Reminder: Update status, linked refs, scope, decisions, success signals, and open questions when you edit this doc.

# Overview
Prevent native Qt/Python lock inversion without moving DBC parsing back to the UI thread.

# Goals
- Retain responsive background workers and reclaim unreachable cycles on the GUI thread.

# Non-goals
- Change decoding results, acquisition ownership, or the user interface.

# Scope and guardrails
- In: scaffolded request, product, backlog, orchestration task, validation, and handoff context.
- Out: unrelated workflow docs and implementation of generated tasks.

# Key product decisions
- Use structured input as the source of truth for generated docs.
- Keep generated write paths local and repo-bounded.

# Success signals
- Generated docs pass lint and audit without broad manual rewrites.
- Context-pack output can be handed to an implementation agent directly.

# References
- Product back-reference: `req_031_prevent_qt_destruction_deadlocks_during_background_python_allocation`
- Task back-reference: `task_030_eliminate_the_qt_python_garbage_collection_lock_inversion`
