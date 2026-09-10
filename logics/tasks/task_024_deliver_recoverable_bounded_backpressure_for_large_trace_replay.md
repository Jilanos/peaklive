## task_024_deliver_recoverable_bounded_backpressure_for_large_trace_replay - Deliver recoverable bounded backpressure for large trace replay
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-10 17:58:36
> Owner: Codex

# AI Context
- Summary: Implement and validate recoverable bounded replay handoff for large traces.
- Keywords: deliver, recoverable, bounded, backpressure, large, trace, replay
- Use when: Developing the replay backpressure correction described by request 024 and backlog item 116.
- Skip when: Investigating live adapter transport, parser format support, or unrelated UI performance work.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Reproduce the 36.7-second failure with a deterministic large capture and a controlled slow presentation path; record queue depth, acknowledgement latency, parsed frame count, and the lifecycle message.
- [x] 2. Map the replay state machine and choose a bounded handoff policy that tolerates legitimate progress while retaining an explicit cancellation and shutdown escape hatch.
- [x] 3. Implement exact permit ownership and generation-safe acknowledgement handling, then keep parsing, decoding, historical persistence, and presentation projections lossless.
- [x] 4. Make progress and completion ordering truthful and preserve distinct diagnostics for parser failure, cancellation, and exhausted backpressure.
- [x] 5. Add focused regression coverage for slow presentation, selected-signal historical writes, cancellation, stale generations, frame-count integrity, and the no-ack safety case.
- [x] 6. Run Ruff, the full headless test suite, the trace performance checks, and the Windows packaging validation; record evidence and close the task only after all acceptance criteria pass.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_116_make_bounded_replay_backpressure_recoverable_and_truthful`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> This task. Proof: Implemented in commits eb7931a, 2d6f915, 938b475, 3e9b42d, e192a5e, and 4b6b67f; validated with ruff check ., QT_QPA_PLATFORM=offscreen .venv/Scripts/python.exe -m pytest -q, i18n validation, Logics lint/flow validation, and final PyInstaller packaging. Source: `4b6b67f`
- request-AC2 -> This task. Proof: Implemented in commits eb7931a, 2d6f915, 938b475, 3e9b42d, e192a5e, and 4b6b67f; validated with ruff check ., QT_QPA_PLATFORM=offscreen .venv/Scripts/python.exe -m pytest -q, i18n validation, Logics lint/flow validation, and final PyInstaller packaging. Source: `4b6b67f`
- request-AC3 -> This task. Proof: Implemented in commits eb7931a, 2d6f915, 938b475, 3e9b42d, e192a5e, and 4b6b67f; validated with ruff check ., QT_QPA_PLATFORM=offscreen .venv/Scripts/python.exe -m pytest -q, i18n validation, Logics lint/flow validation, and final PyInstaller packaging. Source: `4b6b67f`
- request-AC4 -> This task. Proof: Implemented in commits eb7931a, 2d6f915, 938b475, 3e9b42d, e192a5e, and 4b6b67f; validated with ruff check ., QT_QPA_PLATFORM=offscreen .venv/Scripts/python.exe -m pytest -q, i18n validation, Logics lint/flow validation, and final PyInstaller packaging. Source: `4b6b67f`
- request-AC5 -> This task. Proof: Implemented in commits eb7931a, 2d6f915, 938b475, 3e9b42d, e192a5e, and 4b6b67f; validated with ruff check ., QT_QPA_PLATFORM=offscreen .venv/Scripts/python.exe -m pytest -q, i18n validation, Logics lint/flow validation, and final PyInstaller packaging. Source: `4b6b67f`
- request-AC6 -> This task. Proof: Implemented in commits eb7931a, 2d6f915, 938b475, 3e9b42d, e192a5e, and 4b6b67f; validated with ruff check ., QT_QPA_PLATFORM=offscreen .venv/Scripts/python.exe -m pytest -q, i18n validation, Logics lint/flow validation, and final PyInstaller packaging. Source: `4b6b67f`
- request-AC7 -> This task. Proof: Implemented in commits eb7931a, 2d6f915, 938b475, 3e9b42d, e192a5e, and 4b6b67f; validated with ruff check ., QT_QPA_PLATFORM=offscreen .venv/Scripts/python.exe -m pytest -q, i18n validation, Logics lint/flow validation, and final PyInstaller packaging. Source: `4b6b67f`

# Validation
- (no validation recorded yet)
- command: `ruff check .; QT_QPA_PLATFORM=offscreen .venv/Scripts/python.exe -m pytest -q; logics-manager i18n validate; logics-manager lint; logics-manager flow validate req_024_prevent_long_trace_replay_from_aborting_on_false_backpressure_timeouts; uv run python -m PyInstaller --noconfirm --clean peaklive.spec` | result: passed | date: 2026-09-10
- Finish workflow executed on 2026-09-10.
- Linked backlog/request close verification passed.

# Report
- Not started.
- Finished on 2026-09-10.
- Linked backlog item(s): `item_116_make_bounded_replay_backpressure_recoverable_and_truthful`
- Related request(s): `req_024_prevent_long_trace_replay_from_aborting_on_false_backpressure_timeouts`

# Links
- Request: `req_024_prevent_long_trace_replay_from_aborting_on_false_backpressure_timeouts`
- Product brief(s): `prod_023_reliable_large_trace_replay_and_presentation_backpressure`
- Architecture decision(s): (none yet)
