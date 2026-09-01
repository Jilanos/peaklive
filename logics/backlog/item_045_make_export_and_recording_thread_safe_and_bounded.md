## item_045_make_export_and_recording_thread_safe_and_bounded - Make export and recording thread-safe and bounded
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Thread-safe data paths
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: Replaces the lazy cross-thread read of the series store with a stable snapshot, gives the export worker an owner that closeEvent knows about, and moves the recording free-space probe onto a documented interval.
- Keywords: export, recording, thread, safe, bounded
- Use when: Working on the export hand-off, export worker ownership, the SignalSeries snapshot caches, or the recorder's per-frame space guard.
- Skip when: Changing export formats or the row schema, the capture format and rotation policy, the disk thresholds themselves, or making SeriesStore a generally lock-protected structure.

# Problem
- dialogs/export.py:173-174 hands a lazy generator to the export thread, whose body reads series.times, values and slice(), which write the snapshot caches in series.py:79-134 while the UI thread appends and invalidates during a live acquisition. Two threads mutate shared state with no lock, so zip(..., strict=True) can raise and an export can interleave two snapshots - an inconsistent export being worse than a failed one.
- ExportWorker is parented to a non-modal dialog and closeEvent does not know about it, so destroying a running QThread makes Qt abandon the process: closing the application during an export is a clean crash.
- recording/asc.py:74-76 calls shutil.disk_usage() per frame written. The cost belongs to the recording target, so on a removable, network or scanned path the acquisition thread blocks in storage, the driver RX queue overruns, and frames are lost under the driver_overrun condition the adapter already names.

# Scope
- In:
  - A stable snapshot taken on the UI thread before the export worker starts, or an immutable hand-off, so no series state is mutated from two threads.
  - Export worker ownership known to the window, so it is stopped and abandoned with the others on close, and a cancelled or interrupted export never leaves a partial file presented as complete.
  - An interval-based recording space guard - every N frames, N bytes written, or N milliseconds - with the interval documented and the warn-once, stop-below-floor, keep-acquiring semantics unchanged.
  - Tests for an export started during a live acquisition, for closing during an export, and for sustained recording throughput against a deliberately slow free-space probe.
- Out:
  - Changing the export formats, the row schema, the range scopes, or the parquet batching.
  - Changing the capture format, the segment rotation policy, or the disk thresholds themselves.
  - Making the series store generally thread-safe as a lock-protected shared structure; the scope is a safe hand-off at the export boundary.

# Acceptance criteria
- AC1: An export started during a live acquisition produces an internally consistent file, and no series state is written from two threads.
- AC2: Closing the window during an export neither aborts the process nor leaves a partial file that looks complete; the export worker is stopped and abandoned like the others.
- AC3: The recording space guard runs on a documented bounded interval, and sustained capture throughput against a deliberately slow free-space probe stays above the documented floor.
- AC4: The guard's protective semantics are unchanged: warn once, stop below the floor, and keep the acquisition running receive-only with an operator notice.
- AC5: Existing export, recorder, and capture-integrity coverage remains valid.

# AC Traceability
- request-AC12 -> This backlog slice. Proof: AC1: An export started during a live acquisition produces an internally consistent file, and no series state is written from two threads.
- request-AC13 -> This backlog slice. Proof: AC2: Closing the window during an export neither aborts the process nor leaves a partial file that looks complete; the export worker is stopped and abandoned like the others.
- request-AC15 -> This backlog slice. Proof: AC3: The recording space guard runs on a documented bounded interval, and sustained capture throughput against a deliberately slow free-space probe stays above the documented floor.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_011_peaklive_freeze_free_and_self_diagnosing_workstation`
- Architecture decision(s): (none yet)
- Request: `req_011_eliminate_the_remaining_peaklive_freezes_dead_ends_and_silent_failures_found_by_the_ui_thread_audit`
- Primary task(s): `task_012_deliver_a_freeze_free_self_diagnosing_peaklive_runtime`

# Priority
- Priority: Medium - the export path is a clean crash rather than a freeze, and the recording guard costs throughput only on a slow target, but both are data-integrity risks.
- Rationale: Set by scaffold input or defaulted for grooming.
