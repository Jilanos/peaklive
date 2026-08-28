## item_035_diagnose_and_correct_asc_trc_normalization_and_responsive_replay_dispatch - Diagnose and correct ASC/TRC normalization and responsive replay dispatch
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: High
> Theme: Trace parser and replay reliability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-28 11:00:55

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: diagnose, correct, asc, trc, normalization, responsive, replay, dispatch
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- The line parser assumes hexadecimal identifiers and bytes even when ASC metadata declares decimal base, producing replay anomalies instead of frames for representative decimal captures.
- The replay worker delivers high-frequency frame batches and anomaly/status events directly across Qt queued connections. UI rendering can therefore be overwhelmed even though file reading itself is incremental.
- The active replay replacement path waits synchronously for a worker and does not protect a newly opened trace from stale callbacks.

# Scope
- In:
  - Characterize representative ASC and TRC grammar variants with sanitized fixtures and an explicit support matrix.
  - Parse declared ASC base and normalize valid identifiers/payload bytes with correct decimal or hexadecimal semantics, while retaining valid status, error, direction, remote-frame, and extended-ID behavior.
  - Introduce bounded replay progress, presentation dispatch, anomaly aggregation, cancellation, and generation-safe replacement appropriate to the existing PySide6 architecture.
  - Preserve bounded trace/series/session projections and make user-visible loading, cancellation, completion, and partial/unsupported outcomes explicit.
  - Add parser, worker, and offscreen UI regression coverage including high-volume synthetic replay and event-loop responsiveness assertions.
- Out:
  - Binary capture formats, CAN FD, J1939 semantic decoding changes, trace editing, or hardware acquisition changes.
  - Loading all replay records into memory solely to calculate progress or diagnostics.
  - Suppressing malformed-record evidence merely to improve apparent performance.

# Acceptance criteria
- AC1: Tests demonstrate correct frame values for sanitized decimal-base and hexadecimal-base ASC fixtures, plus PCAN-View text TRC fixtures, including event and malformed-line handling.
- AC2: The replay worker exposes bounded, monotonic loading/progress and diagnostic information without a queued callback per source anomaly or an unbounded number of unrendered frame batches.
- AC3: During a synthetic sustained replay, a scheduled UI action executes within a documented bound and can cancel or replace replay; stale callbacks cannot mutate the replacement session.
- AC4: A replay larger than trace-table capacity remains bounded in retained records and UI work while preserving the documented session/report semantics and a truthful unsupported-record summary.
- AC5: Existing ASC/TRC unit tests, normal trace-open UI behavior, filters, graphs, reports, and cancellation/close lifecycle tests continue to pass on Linux and Windows CI.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: Tests demonstrate correct frame values for sanitized decimal-base and hexadecimal-base ASC fixtures, plus PCAN-View text TRC fixtures, including event and malformed-line handling.
- request-AC2 -> This backlog slice. Proof: AC2: The replay worker exposes bounded, monotonic loading/progress and diagnostic information without a queued callback per source anomaly or an unbounded number of unrendered frame batches.
- request-AC3 -> This backlog slice. Proof: AC3: During a synthetic sustained replay, a scheduled UI action executes within a documented bound and can cancel or replace replay; stale callbacks cannot mutate the replacement session.
- request-AC4 -> This backlog slice. Proof: AC4: A replay larger than trace-table capacity remains bounded in retained records and UI work while preserving the documented session/report semantics and a truthful unsupported-record summary.
- request-AC5 -> This backlog slice. Proof: AC5: Existing ASC/TRC unit tests, normal trace-open UI behavior, filters, graphs, reports, and cancellation/close lifecycle tests continue to pass on Linux and Windows CI.
- request-AC6 -> This backlog slice. Proof: AC5: Existing ASC/TRC unit tests, normal trace-open UI behavior, filters, graphs, reports, and cancellation/close lifecycle tests continue to pass on Linux and Windows CI.
- request-AC7 -> This backlog slice. Proof: AC5: Existing ASC/TRC unit tests, normal trace-open UI behavior, filters, graphs, reports, and cancellation/close lifecycle tests continue to pass on Linux and Windows CI.
- request-AC8 -> This backlog slice. Proof: AC5: Existing ASC/TRC unit tests, normal trace-open UI behavior, filters, graphs, reports, and cancellation/close lifecycle tests continue to pass on Linux and Windows CI.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_008_peaklive_reliable_trace_replay`
- Architecture decision(s): (none yet)
- Request: `req_008_diagnose_and_make_peaklive_asc_trc_trace_loading_reliable_and_responsive`
- Primary task(s): `task_009_deliver_reliable_bounded_and_responsive_peaklive_asc_trc_trace_loading`

# Priority
- Priority: High - trace opening is a core analysis workflow and currently fails to provide reliable results or responsive interaction for representative captures.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_009_deliver_reliable_bounded_and_responsive_peaklive_asc_trc_trace_loading`

# Notes
- Task `task_009_deliver_reliable_bounded_and_responsive_peaklive_asc_trc_trace_loading` was finished via `logics-manager flow finish task` on 2026-08-28.
