## req_011_eliminate_the_remaining_peaklive_freezes_dead_ends_and_silent_failures_found_by_the_ui_thread_audit - Eliminate the remaining PeakLive freezes, dead ends, and silent failures found by the UI-thread audit
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Freeze-free, self-diagnosing runtime
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-01 12:05:20

# AI Context
- Summary: Corrects the twelve interruption causes found by the UI-thread and threading audit at commit d6605ef: unbounded UI-thread waits, lifecycle states with no exit, absent diagnostics, lost replay backpressure, per-input-event disk and statistics work, and two cross-thread data paths.
- Keywords: eliminate, remaining, peaklive, freezes, dead, ends, silent, failures, found, thread, audit
- Use when: Working on anything that can stop the Qt event loop, on the acquisition or close lifecycle, on replay backpressure, on input-rate coalescing, or on the export and recording thread boundaries.
- Skip when: Adding CAN transmission, adapter vendors, decode or DBC conflict rules, capture formats, retention capacities, or any remote diagnostics; those stay as they are.

# Needs
- Remove every remaining code path where the UI thread stops processing events without a bound, so the operator is never left with a non-responding window that has to be force-closed.
- Remove the states the application can enter and never leave, so a slow or absent CAN driver never turns a live application into one whose only remaining action is to close it.
- Give the application a voice: a local diagnostic log and process-wide exception hooks, so a freeze or a half-applied state can be diagnosed after the fact instead of only reproduced.
- Restore the bounds the responsive-ingestion design already intends but does not hold in practice during a long replay, and keep continuous pointer and keyboard input off the disk and off the statistics path.

# Context
- A targeted audit of the UI and threading paths at commit d6605ef found twelve distinct causes of interruption, ranked by their likelihood of explaining the reported 'application stops responding, I have to force-close it'. This request delivers their correction; the audit is the evidence base, not part of the scope.
- F1 - ui/catalog_controller.py:82 calls QThread.wait() with no timeout on the UI thread, reached from _load_profile_dbcs (profile switch, startup) and _load_dbc_path. The cancel that precedes it cannot interrupt an in-progress cantools parse: dbc_worker.py:104 only tests the cancel flag between files. Measured DbcCatalog.load(): 14 ms per 100 messages, 129 ms per 1000 messages, so a 2-10 MB vehicle DBC freezes the window for 2 to 15 seconds.
- F2 - services/lifecycle.py:36-41 leaves the TIMED_OUT phase out of both STARTABLE_PHASES and STOPPABLE_PHASES, so a shutdown that overruns its 5 s budget disables Start permanently and refuses Stop. The documented remedy is to close the application. The usual way in is upstream: session.start() calls can.Bus(), which is not interruptible, so request_stop() has no effect while the driver holds the thread.
- F3 - ui/main_window.py:371-400 chains four bounded waits on the UI thread (5 s + 5 s + 5 s + 1 s), so closing can freeze the window for up to 16 s. Workers that do not return are then placed in _ABANDONED_WORKERS to outlive the window, but nothing waits on them before interpreter exit, so a worker blocked in the driver leaves a process with no window holding the CAN channel open.
- F4 - There is no logging anywhere in src/, no sys.excepthook, and the PyInstaller build sets console=False. Verified on the pinned PySide6 6.11.2: an unhandled exception inside a slot is printed to a stderr the packaged executable does not have and then swallowed, leaving state half-applied; an unhandled exception inside a virtual override terminates the process. An exception swallowed in _acquisition_finished or _worker_phase_changed therefore leaves the lifecycle unsettled and Start disabled with no message and no trace. main_window.py:237 _save() writes profiles.json with no try/except and is reached from drag slots.
- F5 - services/replay_worker.py:107 ignores the return value of _pending_batches.acquire(timeout=0.25) and dispatches the batch anyway, while the UI still calls batch_rendered() for it, which releases a permit that was never taken. The semaphore count therefore grows permanently on every timeout, so MAX_PENDING_BATCHES stops bounding anything after the first UI slowdown and the parser floods the Qt event queue - exactly the failure the comment at lines 25-32 describes.
- F6 - ui/panels/trace_filters.py:169 connects textChanged, and ui/panels/trace_view.py:95 rebuilds the whole filtered table synchronously with one QTableWidgetItem per cell, up to 5000 rows by 8 visible columns, with no debounce, and also persists the profile on the same signal. Measured on a full buffer with no DBC loaded: refresh() 104 ms, three keystrokes 42 ms; QTableWidget is markedly slower on Windows and a loaded DBC fills the message and signal columns.
- F7 - _save() serializes every profile to indented JSON, writes a temporary file and does an atomic replace, and is connected to drag signals that emit at pointer-event rate: main_window.py:166 splitterMoved, workspace_center.py:41 cursors_changed (raised by graph_stack.py:278 on every sigPositionChanged) and workspace_center.py:60. Measured at 0.1 ms on tmpfs; 2-20 ms is realistic on NTFS with a scanner inspecting each replace, and a slow or network profile path makes dragging unusable.
- F8 - On the same signals, ui/panels/graph_stack.py:271-280 clears and refills the measurement table and re-slices every plotted series (up to 20000 samples) through three Python passes in analysis/statistics.py:34, per pointer event and per graph refresh tick.
- F9 - ui/dialogs/export.py:173-174 hands a lazy generator to the export thread; its body reads series.times / values / slice(), which write the _time_snapshot and _value_snapshot caches in analysis/series.py:79-134 while the UI thread calls append() and _invalidate() during a live acquisition. Two threads mutate the same state with no lock, so zip(..., strict=True) at series.py:111 can raise and an export can interleave two snapshots. Separately, ExportWorker is parented to a non-modal dialog and main_window.py:371 closeEvent does not know about it, so destroying a running QThread aborts the process.
- F10 - recording/asc.py:74-76 calls _ensure_space() per frame written, which calls shutil.disk_usage() at asc.py:190-191. Measured at 1.3 us per call on tmpfs, but the cost belongs to the recording target: on a removable, network or scanned path it reaches milliseconds, so at 5-10 k frames per second the acquisition thread blocks in storage, the driver RX queue overruns and frames are lost as the driver_overrun condition the adapter already names at pcan.py:127.
- F11 - ui/ingest_controller.py:303-343 runs cantools decode, trace projection, series projection and session facts entirely on the UI thread, one whole batch per timer tick, so the floor on click latency is the cost of a batch. The presentation work is carefully bounded (MAX_ROWS_PER_FLUSH, the 50 ms graph timer, the 1 ms replay timer) but the decode work is not. Measured: 149 ms for 5000 frames with no DBC, about 15 ms per 512-frame replay batch before real DBC decode.
- F12 - ui/session_controller.py:168 creates a new QTimer parented to the window on every _open_trace and never destroys the previous one, so timers and their connections accumulate for the session in a component whose every other retention is explicitly bounded.
- The generation model in services/lifecycle.py is already rigorous and makes a late signal from an abandoned worker harmless; tests/test_ui_lifecycle.py already counts UI-thread timer ticks, so 'still responsive' is already expressed as a measurement. Both are the foundation this request builds on rather than replaces.
- Every retention is already bounded and reports what it dropped (trace 5000, series 20000, frame cache 50000), the profiler is already disabled by default at one attribute read, and the acquisition worker already isolates each shutdown step. None of that is in scope to change.
- Measurements in the audit were taken in this repository's venv on Linux with Qt offscreen on tmpfs, so they are floors: Windows, NTFS and a real DBC each degrade the measured paths. No hardware test was performed, so the PCAN driver behaviour behind F2 and F10 is inferred from the adapter code rather than observed.

# Acceptance criteria
- AC1: No UI-thread code path waits on a worker thread without a bounded timeout. Loading a DBC, switching profiles, or starting up while a catalog operation is in flight keeps the Qt event loop processing events, proven by UI-thread tick counting, whatever the parse duration.
- AC2: A catalog operation in flight can be superseded or cancelled without the UI thread blocking, and whichever operation commits last leaves the catalog, the profile, the DBC panel, the signal explorer, the selection, and the graphs mutually consistent.
- AC3: Closing the window returns control to the operator within one documented bounded total interval, expressed as a single global budget rather than a sum of per-worker waits, and finalizes or explicitly marks recording evidence.
- AC4: The process never outlives its last window silently: a worker still running at exit is named in the diagnostic log with its identity and last known phase, and the exit path is documented for the case where an external driver never returns.
- AC5: A timed-out acquisition shutdown offers an explicit documented operator action that returns the application to a startable state without restarting the process, and states in the UI what remains uncertain about the driver handle.
- AC6: A slow, absent, or failing adapter connect resolves into a bounded, restartable failure state rather than a phase with no exit, and the Stop request issued during the starting phase is honoured or explained.
- AC7: The application writes a diagnostic log to a documented local path and installs both process-wide and per-thread exception hooks, so no unhandled exception in a Qt slot can leave a lifecycle unsettled without a log entry and a visible operator note.
- AC8: Profile persistence failures - locked file, full disk, permission denied - surface as a visible non-fatal note and reach the log, never as a silently lost setting or a terminated process.
- AC9: Replay backpressure holds for the whole replay: with the UI deliberately slowed below the parse rate, the number of dispatched but unrendered batches never exceeds the documented bound, and the bound is asserted directly rather than inferred from wall time.
- AC10: One UI event-loop turn of ingestion stays inside the documented responsiveness budget for both replay and acquisition, with decode cost bounded per turn rather than per batch, and the existing stage budgets in analysis/profiling.py remain met.
- AC11: Continuous pointer and keyboard input - typing in the trace filter, dragging a cursor, dragging a splitter - performs at most one bounded projection and at most one profile write per documented coalescing window, and performs no disk write per input event, while the operator still sees immediate visual feedback.
- AC12: Export reads a stable snapshot: an export started during a live acquisition produces an internally consistent file, and closing the window during an export neither aborts the process nor leaves a partial file that looks complete.
- AC13: The recording space guard costs a bounded amount per frame written, its interval is documented, and its protective semantics - warn once, stop below the floor, keep the acquisition running - are unchanged.
- AC14: Repeated open-trace, start/stop, and profile-switch cycles leave no growing count of timers, threads, or signal connections, asserted by count rather than by inspection.
- AC15: Every correction above is covered by a focused automated test that fails against the current behaviour, and the audit findings that are platform-dependent are documented in the Windows hardware acceptance procedure.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_011_peaklive_freeze_free_and_self_diagnosing_workstation`
- Architecture decision(s): (none yet)

# References
- docs/trace-performance-audit.md
- src/peaklive/app.py
- peaklive.spec
- src/peaklive/ui/main_window.py
- src/peaklive/ui/catalog_controller.py
- src/peaklive/ui/session_controller.py
- src/peaklive/ui/ingest_controller.py
- src/peaklive/ui/workspace_center.py
- src/peaklive/ui/panels/trace_view.py
- src/peaklive/ui/panels/trace_filters.py
- src/peaklive/ui/panels/graph_stack.py
- src/peaklive/ui/panels/measurement.py
- src/peaklive/ui/dialogs/export.py
- src/peaklive/services/lifecycle.py
- src/peaklive/services/worker.py
- src/peaklive/services/replay_worker.py
- src/peaklive/services/dbc_worker.py
- src/peaklive/services/export_worker.py
- src/peaklive/services/profiles.py
- src/peaklive/recording/asc.py
- src/peaklive/analysis/series.py
- src/peaklive/analysis/profiling.py
- src/peaklive/adapters/pcan.py
- tests/test_ui_lifecycle.py
- tests/test_trace_performance.py
- tests/test_replay_worker.py
- tests/test_export.py
- tests/test_asc_recorder.py
- tests/test_lifecycle.py

# Backlog
- `item_040_give_the_application_a_diagnostic_voice_before_changing_its_behaviour`
- `item_041_remove_the_unbounded_and_serialized_ui_thread_waits`
- `item_042_give_the_acquisition_timeout_an_exit`
- `item_043_make_the_replay_and_ingestion_bounds_hold_in_practice`
- `item_044_coalesce_the_work_driven_by_continuous_pointer_and_keyboard_input`
- `item_045_make_export_and_recording_thread_safe_and_bounded`
