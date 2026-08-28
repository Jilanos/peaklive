## req_008_diagnose_and_make_peaklive_asc_trc_trace_loading_reliable_and_responsive - Diagnose and make PeakLive ASC/TRC trace loading reliable and responsive
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Reliable and responsive trace replay
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-08-28 11:00:54

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: diagnose, peaklive, asc, trc, trace, loading, reliable, responsive
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Needs
- An operator must be able to open supported ASC and PCAN-View text TRC captures and obtain a correct, responsive replay regardless of capture size.
- When a capture contains unsupported or malformed records, the application must explain the outcome without flooding the UI or making the trace unusable.
- Trace loading must preserve the existing bounded-memory workspace and must be safely cancellable or replaceable by another trace selection.

# Context
- ReplayWorker incrementally iterates a selected ASC or TRC file, but emits every 512-frame batch and every event through queued Qt signals directly to UI rendering. Unlike live acquisition, replay has no presentation coalescing or generation guard.
- The UI path renders each replay batch into the bounded trace, graph, report, and decoded-series projections. A large number of queued batches or status/anomaly events can therefore defer user input and make even small captures appear to hang.
- Representative local captures include PCAN-View text TRC and Vector-style ASC variants using both `base hex` and `base dec`, with status and ErrorFrame records. Parsing a 10,000-record slice of one decimal ASC yielded 9,842 replay anomalies, 157 status events, and one error event, with no parsed data frames; this indicates that decimal payload interpretation is not currently supported correctly.
- The supported PCAN-View TRC sample parses predominantly as frames, so the investigation must distinguish parser-format defects from replay dispatch and UI-projection responsiveness defects.
- The current trace table is bounded, but replay correctness and responsiveness must be validated using sanitized, repository-owned fixtures rather than the externally supplied captures.

# Acceptance criteria
- AC1: A documented diagnosis identifies, with focused automated evidence, whether each supported ASC/TRC variant fails during parsing, worker dispatch, UI projection, cancellation, or more than one stage; the final user-visible outcome is deterministic.
- AC2: Supported Vector-style ASC captures in both declared hexadecimal and decimal bases, including Rx/Tx data frames, ErrorFrame records, and status records, normalize to correct CAN frames/events without silently treating decimal bytes or identifiers as hexadecimal.
- AC3: Supported PCAN-View text TRC captures normalize frame timestamps, identifiers, payloads, directions, and malformed-record diagnostics correctly, without regressing existing classic CAN or extended-ID support.
- AC4: Opening a supported trace keeps the Qt event loop responsive, gives visible loading progress, and does not allow accumulated frame or anomaly notifications to starve Cancel, Open Trace, window-close, or ordinary UI interaction.
- AC5: Replay memory and UI work remain bounded for captures larger than the trace-table capacity; a full replay does not require loading the file or all decoded records into memory, and display projection is coalesced or otherwise rate-limited without corrupting the retained session facts contract.
- AC6: Replacing or cancelling an active replay is generation-safe: stale frames/events cannot alter the newly selected trace, controls settle predictably, and no worker is destroyed while still running.
- AC7: Unsupported lines remain observable through a bounded, actionable diagnostic summary that includes count and representative location/reason, rather than generating an unbounded row/event stream or concealing data loss.
- AC8: Automated parser, worker, and offscreen UI tests use compact sanitized ASC/TRC fixtures plus synthetic high-volume streams to cover base selection, malformed records, progress, cancellation/replacement, event-loop responsiveness, bounded memory, and regression of existing replay behavior.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_008_peaklive_reliable_trace_replay`
- Architecture decision(s): (none yet)

# References
- src/peaklive/analysis/replay.py
- src/peaklive/services/replay_worker.py
- src/peaklive/ui/session_controller.py
- src/peaklive/ui/panels/trace_view.py
- src/peaklive/analysis/trace.py
- tests/test_replay.py
- tests/test_replay_worker.py
- tests/test_ui_analyst.py
- tests/test_ui_lifecycle.py

# Backlog
- `item_035_diagnose_and_correct_asc_trc_normalization_and_responsive_replay_dispatch`
