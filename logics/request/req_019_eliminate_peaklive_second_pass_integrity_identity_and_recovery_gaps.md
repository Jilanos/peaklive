## req_019_eliminate_peaklive_second_pass_integrity_identity_and_recovery_gaps - Eliminate PeakLive second-pass integrity, identity, and recovery gaps
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: End-to-end measurement integrity and recoverable workflows
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-07 15:06:52

# AI Context
- Summary: Delivery corpus for the thirteen independently reproduced integrity, identity, recovery, concurrency, ordering, and UI safety gaps recorded in req_018, organized into six implementation waves followed by one deferred verification phase.
- Keywords: frame-drain, replay-backpressure, atomic-export, recording-collision, can-identity, signal-provenance, profile-concurrency, trace-events, deferred-testing
- Use when: Implementing or reviewing the second-pass corrections that make accepted measurements complete, local evidence recoverable, CAN and signal identities lossless, concurrent settings durable, and trace actions safe.
- Skip when: Investigating unrelated features, applying the earlier general audit without one of these reproduced scenarios, or running incremental tests before all implementation waves are complete.

# Needs
- Make every frame already accepted by an acquisition or replay reach its authoritative session state exactly once, including final batches, without allowing an unbounded live handoff or a false successful replay.
- Make export and recording artifacts transactional and collision-safe so cancellation, failure, rotation, concurrent operation, or a pre-existing sidecar cannot destroy prior evidence or mislabel incomplete output as complete.
- Preserve complete CAN record semantics across normalization, replay, decoding, trace, reports, plots, exports, and re-recording, including direction, declared remote-frame DLC, and distinct standard and extended identifier spaces.
- Give every decoded signal a stable provenance-qualified identity so equally named definitions from different databases or identifiers never merge values, units, selections, favorites, plots, measurements, or exports.
- Prevent stale concurrent profile saves from erasing another instance's completed change, keep recording iteration stable throughout one segmented acquisition, preserve frame/event source order, and make trace event context actions safe.
- Use a deferred validation workflow for this delivery: do not execute tests during individual implementation steps. Complete all development first, then create or update the regression coverage and run targeted and full validation only in the final verification phase.

# Context
- The independent second-pass review in req_018 reproduced thirteen findings that were absent from the original September audit or appeared in its remediation. Five can silently lose frames or existing files, four can corrupt identity or grow work without a bound, and four break direction, segment naming, event interaction, or durable ordering.
- Stopping acquisition currently clears the pending live frame handoff before asking the worker to stop. The worker can then flush a final batch into a generation the UI has already invalidated, leaving the durable capture and in-memory session facts inconsistent.
- Replay backpressure currently treats failure to acquire a presentation permit as an end-of-input condition, retries one batch without checking the result, emits total progress, and marks the replay successful. A 2,000-frame reproduction delivered 1,024 frames and still reported success.
- CSV and columnar export write directly to the selected destination, while cancellation cleanup unlinks that same path. Recording reservation does not include event sidecars in its collision domain, and clean finalization replaces a pre-existing sidecar.
- The normalized frame model derives DLC from payload length and has no direction field. This loses non-zero remote-frame DLC and Tx direction. Remote frames matching a DBC message enter ordinary payload decoding and can raise before session facts are updated.
- DBC decode lookup and session aggregates key only on the numeric identifier, ignoring standard-versus-extended identity. Signal selection and SeriesStore key only on message.signal, ignoring database and frame provenance, so unrelated values and units can merge.
- Profile saves use unique temporary files but remain whole-file, last-writer-wins updates with no lock, revision, or merge. Recording rotation observes the already-incremented next-acquisition iteration. The trace context menu formats a missing arbitration identifier for event rows, raising at the Qt slot boundary.
- The existing 520-test Linux/offscreen suite and lint pass, so each reproduced scenario requires new focused coverage. Windows and live hardware remain separate acceptance evidence rather than prerequisites for local implementation.
- Development sequencing is operator-mandated: implementation waves must not run unit, UI, integration, performance, or full-suite tests. Test authoring and all test execution begin only after every implementation slice is complete; failures found then are handled inside the final verification phase.

# Acceptance criteria
- AC1: A normal Stop drains every frame accepted by the active live generation into session facts, frame cache, trace, and selected series exactly once before retirement, including the worker's final partial batch; degraded timeout recovery remains generation-safe.
- AC2: The live worker-to-session handoff has a documented bounded-memory and bounded-UI-work policy under sustained overload, without dropping authoritative facts or allowing one event-loop turn to grow without a deterministic limit.
- AC3: Replay reaches success and 100 percent progress only after every parsed frame batch has been accepted and acknowledged. Backpressure timeout, cancellation, replacement, parser failure, and genuine completion have distinct, explicit outcomes.
- AC4: CSV and columnar export use uniquely owned temporary artifacts and atomically publish only after success. Cancellation or failure preserves any pre-existing destination and removes only output owned by the current export.
- AC5: Capture reservation and rotated segment allocation treat capture final, capture partial, reservation marker, event sidecar, and event-sidecar partial as one collision domain; allocation is bounded, concurrent-safe, and never overwrites existing evidence.
- AC6: One acquisition retains its reserved iteration across every rotated segment, the persisted next iteration is used only by the next acquisition, and frame/event records remain in adapter delivery order across batch, error, reconnect, and finalization boundaries.
- AC7: The frame model preserves direction and declared DLC independently of payload. Live and replay paths round-trip Rx, Tx, data, remote, standard, and extended frames through every applicable projection and output.
- AC8: Remote frames bypass payload decoding, while short or otherwise undecodable data frames receive an explicit bounded decode result without escaping a UI slot or preventing their facts and raw identity from being retained.
- AC9: DBC lookup, cache, conflict resolution, filtering, reporting, and identifier aggregation distinguish standard and extended frames that share the same numeric identifier.
- AC10: Signal identity includes stable database and frame provenance. Same-named signals from different enabled definitions remain independently selectable, persisted, decoded, graphed, measured, and exported with their correct units.
- AC11: Concurrent profile writers serialize, merge, or reject stale state explicitly; a stale whole-file save cannot silently erase a completed change made by another application instance.
- AC12: Trace context menus operate on both frames and events, always offer safe record-appropriate actions, and never format or filter on a missing identifier.
- AC13: No tests are executed during implementation waves. After all code changes are complete, focused regression coverage for every reproduced scenario is created or updated, then targeted tests, the full suite, lint, internationalization checks, and Logics validation run in the final verification phase.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_018_peaklive_trustworthy_measurement_identity_and_recoverable_local_evidence`
- Architecture decision(s): (none yet)

# References
- logics/request/req_018_second_pass_review_findings_integrity_identity_and_recovery_gaps.md
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
- `item_098_drain_live_acquisition_completely_through_a_bounded_authoritative_handoff`
- `item_099_make_replay_completion_truthful_under_backpressure_and_cancellation`
- `item_100_publish_exports_and_recording_artifacts_transactionally_without_collision`
- `item_101_preserve_complete_can_frame_identity_and_make_decoding_total`
- `item_102_qualify_decoded_signal_identity_across_databases_and_identifiers`
- `item_103_prevent_stale_concurrent_profile_writers_from_erasing_setup_changes`
- `item_104_make_trace_context_actions_safe_for_frame_and_event_records`
