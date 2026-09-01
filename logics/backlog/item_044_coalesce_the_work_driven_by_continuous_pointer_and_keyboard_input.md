## item_044_coalesce_the_work_driven_by_continuous_pointer_and_keyboard_input - Coalesce the work driven by continuous pointer and keyboard input
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Input-rate coalescing
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: Introduces one shared coalescing window for the filtered-table projection, the profile write, and the A-B statistics, so typing in the filter and dragging a cursor or splitter no longer pay per input event.
- Keywords: coalesce, work, driven, continuous, pointer, keyboard, input
- Use when: Touching anything connected to textChanged, splitterMoved, cursors_changed or sigPositionChanged, or anything that calls _save() from a slot.
- Skip when: Migrating the trace table to QTableView, or changing filter semantics, the persisted profile schema, or the statistics definitions.

# Problem
- trace_filters.py:169 connects textChanged, and trace_view.py:95 rebuilds the whole filtered table synchronously, one QTableWidgetItem per cell, with no debounce: measured at 104 ms on a full buffer with no DBC loaded, and markedly worse on Windows with a loaded DBC.
- _save() serializes every profile, writes a temporary file and does an atomic replace, and is connected to splitterMoved and to cursors_changed, which graph_stack.py:278 raises on every sigPositionChanged: a disk write per pointer event, at 2-20 ms each on a scanned NTFS volume.
- graph_stack.py:271-280 additionally rebuilds the measurement table and re-slices every plotted series through three Python passes on those same pointer events.

# Scope
- In:
  - One coalescing mechanism, with a documented window, shared by the filtered-table projection, the profile persistence, and the A-B statistics recalculation.
  - Immediate lightweight feedback preserved during the gesture - the cursor summary and the filter text - with the expensive projection following the gesture.
  - A guaranteed final write on close and on profile switch, so coalescing never loses a setting.
  - Tests that count projections and profile writes across a burst of synthetic input events and assert at most one per window, and that assert no write occurs per event.
- Out:
  - Migrating the trace table to QTableView with a model over the bounded buffer; the scope is bounding the current projection's rate.
  - Changing the filter semantics, the column configuration, or the persisted profile schema.
  - Changing the statistics definitions or the measurement table contents.

# Acceptance criteria
- AC1: A burst of synthetic filter keystrokes produces at most one filtered-table projection per documented coalescing window, and the filter text stays responsive throughout.
- AC2: A burst of synthetic cursor and splitter drag events produces at most one profile write per window and no write per event, while the cursor summary still tracks the gesture.
- AC3: The A-B statistics and the measurement table are recalculated at most once per window during a drag, and their values after the gesture are identical to those the per-event path produced.
- AC4: Close and profile switch flush any pending write, so no setting is lost to coalescing.
- AC5: Tests assert the projection and write counts by count, not by elapsed time.

# AC Traceability
- request-AC11 -> This backlog slice. Proof: AC1: A burst of synthetic filter keystrokes produces at most one filtered-table projection per documented coalescing window, and the filter text stays responsive throughout.
- request-AC15 -> This backlog slice. Proof: AC2: A burst of synthetic cursor and splitter drag events produces at most one profile write per window and no write per event, while the cursor summary still tracks the gesture.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_011_peaklive_freeze_free_and_self_diagnosing_workstation`
- Architecture decision(s): (none yet)
- Request: `req_011_eliminate_the_remaining_peaklive_freezes_dead_ends_and_silent_failures_found_by_the_ui_thread_audit`
- Primary task(s): `task_012_deliver_a_freeze_free_self_diagnosing_peaklive_runtime`

# Priority
- Priority: Medium - these are visible stutters on routine gestures rather than hard freezes, and they share one coalescing mechanism.
- Rationale: Set by scaffold input or defaulted for grooming.
