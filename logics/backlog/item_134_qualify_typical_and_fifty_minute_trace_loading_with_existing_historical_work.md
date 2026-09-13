## item_134_qualify_typical_and_fifty_minute_trace_loading_with_existing_historical_work - Qualify typical and fifty minute trace loading with existing historical work
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Integrated long capture qualification
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-13 23:32:48

# AI Context
- Summary: Exercise 1.756M and 5.575M frames at operator density and keep missing Windows proof explicit.
- Keywords: qualify, typical, fifty, minute, trace, loading, existing, historical, work
- Use when: Qualifying the integrated preparation pipeline after correctness and performance slices.
- Skip when: Using small offscreen tests or historical artifact records as current native Windows acceptance.

# Problem
- Small offscreen tests and historic Windows evidence cannot qualify the current selected-signal pipeline at operator density.

# Scope
- In:
  - Priority rationale: qualification follows High-priority correctness and loading fixes and gates final claims.
  - Run the new matrix at 20k/200k frames in routine validation and approximately 1.756M/5.575M frames at measured density in an explicit resource-budgeted qualification job.
  - Qualify 1/8/16 signals, mixed bus events, late selection, repeated open/cancel, resource failure and one representative source-derived raw oracle; private evidence stays local.
  - Integrate existing historical scheduler/reconstruction and rare-event obligations through their current owner; list unmet prerequisites rather than rewriting their statuses.
  - Record identifiable native Windows build, hardware/storage, memory/disk peaks, first-data/ready times and heartbeat/cancel latency; retain explicit unavailable status if platform access is missing.
  - Run focused tests plus full Linux/Windows suites, Ruff, i18n validation when copy changes, and required Logics validation before closeout.
  - Track existing workspace quarantine and native DPI acceptance separately; do not claim those resolved by a loading benchmark.
- Out:
  - Closing unrelated tasks or waiving their remaining criteria.
  - Requiring an operator-private fixture to start development.

# Acceptance criteria
- AC1: The complete lifecycle harness records each preparation stage and first-data/ready milestones; timeout, partial load and enabled budget failures have nonzero verdicts.
- AC2: Typical-density and event-heavy qualification preserves ordered frame/event counts with bounded queues through EOF, cancel and replacement.
- AC3: Storage and worker fault qualification demonstrates one explicit incomplete outcome, exact ownership retirement and successful reopen without source mutation.
- AC4: Identified reference-machine evidence demonstrates the existing 250ms interaction target during loading, finalization and cancellation without relaxing product bounds.
- AC5: Temporary-disk, memory and queue peaks plus configured admission limits are recorded; reset, late-selection and shutdown preserve session/revision isolation.
- AC6: Source-oracle, live/export and historical regression evidence remains traceable; existing navigation/rare-event/workspace obligations are not duplicated or silently waived.
- AC7: Approximately 1.756M/5.575M-frame workloads at 1858 frames/s and 1/8/16 signals have identifiable native Windows evidence; unrun configurations explicitly block final qualification.

# AC Traceability
- request-AC1 -> This backlog slice. Proof deferred to implementation. Planned evidence: The complete lifecycle harness records each preparation stage and first-data/ready milestones; timeout, partial load and enabled budget failures have nonzero verdicts.
- request-AC2 -> This backlog slice. Proof deferred to implementation. Planned evidence: Typical-density and event-heavy qualification preserves ordered frame/event counts with bounded queues through EOF, cancel and replacement.
- request-AC3 -> This backlog slice. Proof deferred to implementation. Planned evidence: Storage and worker fault qualification demonstrates one explicit incomplete outcome, exact ownership retirement and successful reopen without source mutation.
- request-AC4 -> This backlog slice. Proof deferred to implementation. Planned evidence: Identified reference-machine evidence demonstrates the existing 250ms interaction target during loading, finalization and cancellation without relaxing product bounds.
- request-AC5 -> This backlog slice. Proof deferred to implementation. Planned evidence: Temporary-disk, memory and queue peaks plus configured admission limits are recorded; reset, late-selection and shutdown preserve session/revision isolation.
- request-AC6 -> This backlog slice. Proof deferred to implementation. Planned evidence: Source-oracle, live/export and historical regression evidence remains traceable; existing navigation/rare-event/workspace obligations are not duplicated or silently waived.
- request-AC7 -> This backlog slice. Proof deferred to implementation. Planned evidence: Approximately 1.756M/5.575M-frame workloads at 1858 frames/s and 1/8/16 signals have identifiable native Windows evidence; unrun configurations explicitly block final qualification.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_027_peaklive_responsive_and_trustworthy_long_trace_preparation`
- Architecture decision(s): (none yet)
- Request: `req_029_make_long_trace_loading_responsive_ordered_and_failure_explicit`
- Primary task(s): `task_028_deliver_responsive_ordered_and_measurable_long_trace_loading`

# Priority
- Priority: Medium
- Rationale: Qualification follows the High-priority fixes and gates final completion.
