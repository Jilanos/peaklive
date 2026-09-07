## req_018_second_pass_review_findings_integrity_identity_and_recovery_gaps - Second-pass review findings: integrity, identity, and recovery gaps
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Measurement integrity and recoverable desktop workflows
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.

# AI Context
- Summary: Captures independently reproduced gaps left after the September audit remediation: silent frame loss, destructive output paths, incomplete CAN identity, ambiguous signal keys, multi-instance profile loss, and an event-row UI exception.
- Keywords: second, pass, review, findings, integrity, identity, recovery, gaps
- Use when: Scoping follow-up work on acquisition stop integrity, replay backpressure, recording/export collision safety, CAN frame identity, DBC signal identity, profile concurrency, or trace event interactions.
- Skip when: Repeating the original September audit findings, completing the active graph-control task, or treating these candidates as already approved implementation work.

# Needs
- Prevent acquisition Stop from discarding frames that the worker already received or records during finalization, and keep live ingestion memory and UI work explicitly bounded without falsifying session facts.
- Make replay backpressure terminate only as an explicit cancellation or failure; a timeout must never truncate the source and then report full progress and success.
- Make export and recording finalization transactional with respect to pre-existing artifacts, including event sidecars and cancelled exports.
- Preserve complete CAN record identity and semantics across hardware normalization, replay, decode, trace, reporting, and re-recording: direction, remote-frame DLC, and standard-versus-extended identifier space.
- Give decoded signals a catalog-stable identity so equally named messages/signals from different databases or frame IDs cannot merge into one plot, series, favorite, or export column.
- Prevent concurrent application instances from silently overwriting each other's profile changes, keep one acquisition iteration stable across all rotated segments, and make trace event context actions safe.

# Context
- This is a deliberately independent second pass. `docs/audit-2026-09.md` and completed requests `req_009_audit_peaklive_performance_and_make_trace_signal_exploration_and_time_navigation_complete`, `req_011_eliminate_the_remaining_peaklive_freezes_dead_ends_and_silent_failures_found_by_the_ui_thread_audit`, `req_012_make_peaklive_lossless_capture_export_and_workspace_controls_trustworthy`, `req_013_add_canalyzer_style_recording_configuration_and_collision_safe_acquisition_naming_to_peaklive`, and `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap` were read first and used as an exclusion list. The active graph-control work in `task_016_implement_legible_peaklive_graph_comparison_and_signal_controls`/`req_015_make_peaklive_graph_comparison_and_signal_controls_unmistakably_legible` was also excluded. None of the findings below repeats the original audit's eight critical defects, its performance table, visual findings, or known mixin/port debt; several are regressions or unverified edge cases in the later remediation.
- **Critical — Stop silently discards already-received live frames.** `WorkspaceSession._stop_acquisition()` invalidates presentation at `src/peaklive/ui/session_controller.py:103-111` before requesting worker stop. `WorkspaceIngest._invalidate_presentation_generation()` clears `_pending_presentation_frames` at `src/peaklive/ui/ingest_controller.py:269-277`; the worker's final `_flush()` then calls a sink whose generation is rejected at `:279-291`. The discarded frames never reach `TraceBuffer`, `SeriesStore`, `FrameCache`, or `SessionFacts`, although they can already be present in the recording. Reproduction against `MainWindow`: queueing 64 frames and following the Stop invalidation changed the pending count from 64 to 0.
- **Critical — Replay backpressure converts a slow UI into a successful truncated replay.** In `ReplayWorker.run()` at `src/peaklive/services/replay_worker.py:135-147`, a false `_dispatch()` result breaks parsing; the same full batch is retried once at `:141-142` with its result ignored, then total progress and `_succeeded = True` are emitted unconditionally. With the existing four-permit bound, 2,000 generated frames and no acknowledgements dispatched exactly 1,024 frames, retained four pending batches, and still returned `succeeded=True`. The UI completion path at `src/peaklive/ui/session_controller.py:277-299` does not consult `succeeded` and announces completion.
- **Critical — cancelling or failing an export can delete a pre-existing destination.** Both writers open the selected final path directly (`src/peaklive/analysis/export.py:27-38`, `:41-73`). `ExportWorker._discard_partial()` then unlinks that same path on cancellation or handled failure (`src/peaklive/services/export_worker.py:51-83`). Reproduction: create `existing.csv`, request cancellation before `execute()`, and the call returns `-1` with `exists=False`. There is no distinct temporary output despite the method name and comment referring to a partial file.
- **Critical — recording reservation ignores sidecars and clean finalization overwrites them.** `RecordingNaming.reserve()` checks only the capture final, capture partial, and marker at `src/peaklive/recording/naming.py:201-218`; an existing `.peaklive-events.jsonl` or its partial does not make a candidate occupied. `AscRecorder._open_next_segment()` opens the sidecar partial with `"w"` and `_close_segment()` replaces the final sidecar (`src/peaklive/recording/asc.py:193-202`, `:219-230`). Reproduction: pre-create the event sidecar after reserving an otherwise free capture; a start/stop replaces its contents with an empty file.
- **Critical — valid remote frames can abort one UI ingestion turn and are not represented losslessly.** `CanFrame.dlc` is derived only from `len(data)` (`src/peaklive/domain/models.py:20-33`), while hardware and replay normalization discard the separately declared DLC (`src/peaklive/adapters/pcan.py:96-103`, `src/peaklive/analysis/replay.py:133-155`). A remote request with DLC 8 therefore becomes DLC 0. If its identifier has a DBC definition, `DbcCatalog.decode()` passes the empty payload to the normal decoder without considering `is_remote_frame` (`src/peaklive/analysis/dbc.py:285-305`); reproduction raised `DecodeError: Wrong data size: 0 instead of 8 bytes`. `_decode()` catches only `AmbiguousMessageError` (`src/peaklive/ui/ingest_controller.py:367-384`), so the timer/queued slot exits before recording the frame in UI facts and buffers.
- **High — the live handoff introduced an unbounded memory and event-loop workload.** The post-audit implementation changed the lossy replacement into `_pending_presentation_frames.extend(frames)` (`src/peaklive/ui/ingest_controller.py:252-291`), but gives this cross-thread list no capacity or producer backpressure. Every 16 ms `_drain_presentation_frames()` hands the entire accumulated list to per-frame decoding on the UI thread (`:293-350`). If input exceeds decode throughput, both backlog memory and the duration of one UI turn grow without a bound; Stop then triggers the critical discard above. Existing bounded `TraceBuffer`, series, and frame cache do not bound this upstream list.
- **High — standard and extended frames with the same numeric identifier share one DBC cache entry and decode route.** `DbcCatalog._decode_cache`, resolutions, conflicts, and `_resolve_candidate()` are all keyed only by `arbitration_id` (`src/peaklive/analysis/dbc.py:98-110`, `:256-320`); `CanFrame.is_extended_id` is never consulted. Reproduction loaded a standard 0x123 DBC message and decoded an extended 0x123 frame as that standard message, returning value 5. Session aggregates are likewise keyed only by the integer at `src/peaklive/analysis/session.py:84-114`, merging two distinct CAN identifier spaces.
- **High — different DBC signals collapse onto the same mutable series identity.** `DbcSignalReference.display_name` is only `message.signal` (`src/peaklive/analysis/dbc.py:46-57`); `signal_names()` deduplicates that text (`:119-127`), the explorer persists it (`src/peaklive/ui/panels/signal_explorer.py:103-185`), and ingestion uses it as the `SeriesStore` key (`src/peaklive/ui/ingest_controller.py:330-339`). Reproduction with two enabled databases defining `SharedMessage.SharedSignal` on IDs 0x123 and 0x124 produced two references but one selectable name; decoding produced values 3 A and 6 B under the same key. Graphs, measurements, deferred decode, favorites, and export can therefore combine unrelated units and signals.
- **High — profile persistence is atomic per write but still loses concurrent edits.** `ProfileStore.save()` uses a unique temporary and `replace()` (`src/peaklive/services/profiles.py:134-163`) but has no lock, revision check, or merge. Two store instances loaded the same state; instance A saved bitrate 125000, then instance B saved a channel edit from its stale copy. The final profile had the channel change but bitrate 500000. This contradicts the method's “safely alongside another instance” claim and can silently erase setup changes.
- **Medium — replay discards Tx direction.** Both parsers validate/read `Rx` or `Tx` but `_frame()` has no direction argument (`src/peaklive/analysis/replay.py:76-109`, `:112-156`); `CanFrame` has no direction field and `TraceBuffer.add_frame()` hard-codes `"RX"` (`src/peaklive/analysis/trace.py:96-115`). Reproduction with two Tx ASC records displayed directions `['RX', 'RX']`. Direction filtering and any later re-recording therefore state the opposite bus direction.
- **Medium — recording iteration changes inside one rotated acquisition.** `AcquisitionSession.start()` mutates the same `RecordingSettings.iteration` immediately after starting the recorder (`src/peaklive/services/acquisition.py:30-51`). `AscRecorder` retains that object and reads its now-incremented iteration for subsequent segments (`src/peaklive/recording/asc.py:180-200`). With a `{iteration}_{segment}` template and forced rotation, one acquisition produced `capture_001_001.asc`, then `capture_002_002.asc`, `capture_002_003.asc`, and later segments while the next suggested acquisition iteration remained 2. The iteration no longer identifies one acquisition consistently and collides conceptually with the next reservation search.
- **Medium — the trace context menu raises on every event row.** `TraceViewPanel._context_menu()` accepts any retained record, then formats `record.arbitration_id` with `:X` (`src/peaklive/ui/panels/trace_view.py:251-273`). Event records return `None`. An offscreen reproduction right-clicking a `driver_error` row raised `TypeError: unsupported format string passed to NoneType.__format__`, so even the safe Copy action is unavailable on event evidence and the exception reaches the Qt slot boundary.
- **Medium — pending frames and bus events are recorded out of source order.** `AcquisitionWorker.run()` accumulates frames in `batch`, but a following `BusEvent` goes directly to `_handle_event()` without first flushing that batch (`src/peaklive/services/worker.py:91-108`, `:181-206`). `session.record_event()` writes the later event immediately while earlier received frames remain memory-only until the next batch/timeout/finalization. The durable ASC/TRC and sidecar ordering therefore disagrees with adapter delivery order around every event or reconnect boundary.
- Validation evidence: `uv run ruff check .` passed. `QT_QPA_PLATFORM=offscreen uv run --python 3.13 python -m pytest` passed all 520 tests, demonstrating that these scenarios are coverage gaps rather than currently failing regressions. The first unqualified `uv run pytest -q` selected a local Python 3.14 executable without project dependencies and failed collection; it was not treated as product evidence.
- Scope is capture only: no fixes, backlog items, tasks, product brief, or architecture decisions are created by this review. Hardware behavior and Windows rendering remain unverified; all stated reproductions used the repository's Python 3.13 environment on Linux/offscreen Qt.

# Acceptance criteria
- AC1: Stopping live acquisition drains every frame accepted by the active generation into facts, retained buffers, and selected series exactly once before retiring it; the handoff has an explicit bounded-memory/backpressure policy and remains responsive under sustained overload.
- AC2: Replay cannot reach its success path unless every parsed batch has been accepted and acknowledged; backpressure timeout, explicit cancellation, parser failure, and replacement each have distinct tested outcomes and never emit false 100% progress.
- AC3: CSV/Parquet export writes to a unique temporary artifact and atomically replaces the selected destination only after success; cancellation or failure preserves any pre-existing destination and removes only artifacts owned by that export.
- AC4: Capture reservation and every rotated-segment allocation treat capture, partial, marker, event sidecar, and sidecar partial as one collision domain. Existing evidence is never replaced, and segment allocation is bounded and atomic across concurrent instances.
- AC5: The normalized frame model preserves direction and declared DLC independently of payload, including remote frames; replay and live normalization round-trip them through trace, report, recording, and export where applicable.
- AC6: Remote frames never enter payload decoding, and short/malformed payload decode failures become an explicit per-frame decode status or bounded diagnostic rather than escaping the UI ingestion slot or dropping session facts.
- AC7: DBC lookup, conflict resolution, decode caching, reporting, and filtering distinguish standard and extended identifier spaces, with regression fixtures for equal numeric IDs in both spaces.
- AC8: Signal selection and series identity include enough stable provenance to distinguish same-named messages/signals across enabled databases and frame IDs; display labels may remain concise, but values and units cannot merge.
- AC9: Concurrent profile writers either serialize, detect stale state, or merge deterministically; a stale whole-file save cannot silently erase another running instance's completed change.
- AC10: One recording keeps its reserved iteration across every rotated segment, while the persisted next-iteration value remains reserved for the next acquisition.
- AC11: Context menus work for both frame and event rows, exposing only actions valid for that record kind; no `None` identifier is formatted or passed to an ID filter.
- AC12: Before recording a bus event or reconnect transition, the worker flushes all frames received earlier, and deterministic mixed frame/event fixtures prove durable source order.
- AC13: Focused regression tests cover every reproduced scenario above in addition to the full lint and test suite; Windows/hardware claims require separate platform evidence.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)

# References
- docs/audit-2026-09.md
- src/peaklive/domain/models.py
- src/peaklive/analysis/dbc.py
- src/peaklive/analysis/export.py
- src/peaklive/analysis/replay.py
- src/peaklive/analysis/session.py
- src/peaklive/analysis/trace.py
- src/peaklive/recording/asc.py
- src/peaklive/recording/naming.py
- src/peaklive/services/acquisition.py
- src/peaklive/services/export_worker.py
- src/peaklive/services/profiles.py
- src/peaklive/services/replay_worker.py
- src/peaklive/services/worker.py
- src/peaklive/ui/ingest_controller.py
- src/peaklive/ui/session_controller.py
- src/peaklive/ui/panels/signal_explorer.py
- src/peaklive/ui/panels/trace_view.py
- tests

# Backlog
- none
