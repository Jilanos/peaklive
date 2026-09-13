## req_028_incremental_review_findings_trace_loading_and_historical_storage - Incremental review findings: trace loading and historical storage
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Trace loading integrity and performance
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-13 23:32:17

# AI Context
- Summary: Evidence-backed incremental audit after the second-pass review, focused on trace loading, ordered events, history write failure and missing performance attribution.
- Keywords: incremental, review, findings, trace, loading, historical, storage
- Use when: Reviewing the evidence and ownership map before implementing the associated corrective corpus.
- Skip when: Claiming these findings are implemented or duplicating already-open navigation and Windows layout work.

# Needs
- F1 (High): Remove synchronous historical sample/summary/event construction from the GUI loading critical path while retaining complete measurement evidence.
- F2 (High): Bound valid replay events together with frames and preserve their source order.
- F3 (High): Contain history write failures without leaking acknowledgements, leaving unexplained partial facts or misreporting completion.
- F4 (Medium): Measure and enforce the complete current loading path, including history construction and first/final useful display.

# Context
- Baseline: a4a4bbf, the independent second-pass review on 2026-09-07. Reviewed head: cc75668, 93 later commits. See docs/audit-2026-09-13-trace-loading.md for evidence, limitations, existing debt, commands and results.
- F1 evidence: src/peaklive/ui/ingest_controller.py:323 calls HistoricalSignalStore.append_many on the GUI path; src/peaklive/analysis/history.py:114-279 builds seven summary levels and commits per batch. At 200000 synthetic frames and sixteen selected signals, history cost is 12.565 seconds within a 21.981-second load; initial offscreen event passes reached 487 ms. These diagnostic runs overlapped the test suite and are not a Windows SLA.
- F2 evidence: src/peaklive/services/replay_worker.py:127-159 emits valid bus events outside the semaphore and before buffered frames. Reproduced event(0.001), frame(0.000), frame(0.002) delivery and 10000 events emitted without acknowledgements.
- F3 evidence: src/peaklive/ui/session_controller.py:201-212 acknowledges only after ingestion. A SQLite query_only failure escapes the drain with one trace/cache frame already mutated and zero acknowledgements. No actual disk-full scenario was claimed.
- F4 evidence: src/peaklive/analysis/profiling.py has no history stage; scripts/audit_trace_performance.py returns zero after budget overruns and does not enforce replay success/deadline/frame-count or final historical-display readiness. The responsiveness test uses no DBC; existing Windows tolerances are not production budgets.
- The supplied local capture calibrates the workload without publishing its filename, identifiers or payloads. The operator explicitly accepts longer loading for equally dense captures up to 50 minutes; retain responsive, cancellable, truthful preparation instead of inventing an absolute completion SLA.
- Existing historical-navigation and reconstruction obligations stay with backlog item 123 (see the audit ownership table). Rare-event overflow indication and Windows layout qualification remain with their existing active tasks. The audit records their evidence without creating duplicate fixes.
- Full baseline verification: QT_QPA_PLATFORM=offscreen uv run --python 3.13 python -m pytest -ra -> 626 passed in 197.18s. Ruff passed. Baseline Logics health/lint passed; audit had zero blockers and existing warnings.
- This request captures the review only. The user separately authorized a ready-to-develop corrective corpus; no application changes are implemented by this audit.

# Acceptance criteria
- AC1: Selected-signal loading has attributable history costs and bounded GUI work without discarding raw or rare-event history.
- AC2: Mixed frame/event and event-only replay is source-ordered and bounded through terminal acknowledgement.
- AC3: Storage failures produce explicit recoverable terminal outcomes without silent partial success or stuck permits.
- AC4: Performance evidence covers representative signal counts, long-duration density, first-data and ready states; harness failure returns a nonzero verdict.
- AC5: New corrections and already-owned historical/Windows debts are distinguished, with workload decisions, qualification blockers and remaining questions documented.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)

# References
- docs/audit-2026-09-13-trace-loading.md
- logics/analysis/trace_load_followup_probe.py
- src/peaklive/ui/ingest_controller.py
- src/peaklive/ui/session_controller.py
- src/peaklive/services/replay_worker.py
- src/peaklive/analysis/history.py
- src/peaklive/analysis/profiling.py
- scripts/audit_trace_performance.py
- tests/test_trace_performance.py

# Backlog
- none
