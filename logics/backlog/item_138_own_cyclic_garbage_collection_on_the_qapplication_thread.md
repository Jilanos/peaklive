## item_138_own_cyclic_garbage_collection_on_the_qapplication_thread - Own cyclic garbage collection on the QApplication thread
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Runtime reliability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: own, cyclic, garbage, collection, qapplication, thread
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- CPython automatic collection can destroy Qt wrappers inside a parser worker while the GUI thread is also destroying Qt objects.

# Scope
- In:
  - Install one GUI collection scheduler before window workers start.
  - Respect collection thresholds and application lifetime.
  - Verify thread ownership with a deterministic regression and rerun Linux CI tests.
- Out:
  - Disable garbage collection permanently.
  - Change parser semantics or move parsing onto the GUI thread.

# Acceptance criteria
- Worker allocations leave GUI cycles for GUI-thread collection.
- Repeated window construction reuses one timer and application destruction restores the prior automatic-GC setting.
- Linux suite, targeted Windows regressions, and Ruff pass.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: Worker allocations leave GUI cycles for GUI-thread collection.
- request-AC2 -> This backlog slice. Proof: Repeated window construction reuses one timer and application destruction restores the prior automatic-GC setting.
- request-AC3 -> This backlog slice. Proof: Linux suite, targeted Windows regressions, and Ruff pass.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_029_peaklive_gui_owned_cyclic_memory_reclamation`
- Architecture decision(s): (none yet)
- Request: `req_031_prevent_qt_destruction_deadlocks_during_background_python_allocation`
- Primary task(s): `task_030_eliminate_the_qt_python_garbage_collection_lock_inversion`

# Priority
- Priority: High - A reproduced native lock inversion freezes the application and blocks CI.
- Rationale: Set by scaffold input or defaulted for grooming.
