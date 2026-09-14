## item_134_qualify_typical_and_fifty_minute_trace_loading_with_existing_historical_work - Qualify typical and fifty minute trace loading with existing historical work
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 60%
> Complexity: High
> Theme: Integrated long capture qualification
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-14 10:03:23

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
- request-AC1 -> This backlog slice. Proof: item_130's harness, exercised directly by the 400k/800k-frame qualification probes recorded in Validation.
- request-AC2 -> This backlog slice. Not qualified at typical density in this wave; see Report. Mechanism-level proof only: item_131's `tests/test_replay_ordered_transport.py`.
- request-AC3 -> This backlog slice. Not qualified at scale in this wave; see Report. Mechanism-level proof only: item_132's `tests/test_history_write_failures.py`.
- request-AC4 -> This backlog slice. Measured and NOT met at 400k/800k frames (317ms/281ms > 250ms budget) - see Report; an open finding, not closed out.
- request-AC5 -> This backlog slice. Partial: RAM peak recorded in Validation; temp-disk peak and admission-limit-under-pressure not instrumented this wave - see Report.
- request-AC6 -> This backlog slice. Proof: exact accepted-frame-count match at both probe scales (Validation); full suite (650 tests) green.
- request-AC7 -> This backlog slice. NOT satisfied: no native Windows evidence exists from this session, and the full 1.756M/5.575M-frame workloads were not run (tmpfs `/tmp` capacity, see Report) - this explicitly blocks final qualification, exactly as AC7 anticipates.

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

# Validation
- Reduced-scale qualification probes (2026-09-14), run directly through the item_130 harness's `measure()` at the operator's measured density (`OPERATOR_FRAME_INTERVAL_S`, ~1858.35 fps) rather than through `--qualify` (which targets the full `TYPICAL`/1,755,746-frame and `LONG`/5,575,042-frame profiles - not attempted, see Report):
  - 400,000 frames, 16 signals: succeeded, all frames accepted (400000/400000), wall clock 38.46s, `history_write` dominant at 53.3% of measured time, `queue_wait` 24.0%. Slowest event-loop tick **317ms**, exceeding the 250ms responsiveness budget.
  - 800,000 frames, 8 signals: succeeded, all frames accepted (800000/800000), wall clock 51.43s, `history_write` dominant at 53.7%. Slowest event-loop tick **281ms**, exceeding the 250ms responsiveness budget.
  - Process memory stayed bounded during both runs (peaked at ~2.5GiB used of 7.6GiB system RAM, observed via `free -h` polling every 20s during the 800k run); no memory exhaustion.
  - Full test suite (650 tests, all prior waves) passes; Ruff clean.

# Report
- **AC4 is not met at this measured scale**: the existing 250ms interaction/responsiveness objective is exceeded (317ms and 281ms slowest ticks) at 400k and 800k frames respectively, on this Linux/offscreen environment. This is reported as measured, per the literal criterion, not reinterpreted or softened - it is a genuine, currently open performance gap that this task's waves (items 130-133) did not fully close, surfaced only once qualification actually exercised meaningful density. It is not yet triaged to a specific cause (candidates include the still-uncoordinated `SourceSignalDecodeWorker` writer, the count-only queue bound without a byte budget, or `HISTORY_DRAIN_POLL_MS`/GUI-thread polling overhead during `_finish_historical_readiness`) and is not fixed in this session; it should be treated as a new, explicit finding for the operator/next task, not closed out here.
- **The full 1.756M/5.575M-frame qualification workloads (`TYPICAL`/`LONG`) were not run in this session.** Two independent blockers exist, not one: (1) no native Windows reference machine or packaged build capability is available from this session - AC7 explicitly requires native Windows evidence and its absence explicitly blocks final qualification, exactly as AC7 anticipates. (2) Independently of Windows, this Linux sandbox's `/tmp` is a `tmpfs` (RAM-backed) filesystem with only ~3.1GiB available (`df -h /tmp`); the original audit measured historical-storage growth at roughly 39x source bytes for a dense multi-signal capture, so a full-scale `TYPICAL` or `LONG` run's temporary SQLite store would very plausibly exceed that space (and compound with process RAM) before completing. Attempting it risked crashing this session's own environment for a result that, per (1), could not have qualified the target platform anyway; the two smaller probes above were chosen instead as a bounded, safe way to still exercise the harness and the real writer/backpressure pipeline under load and obtain genuine evidence (including the responsiveness finding above) rather than none at all.
- AC1 (harness) - satisfied by item_130's own wave; these probes used it directly. AC2 (event-heavy/EOF/cancel/replacement at typical density) - not separately qualified in this wave; item_131's own unit-level tests cover the mechanism, not at this frame count. AC3 (storage/worker fault qualification at scale) - not run; item_132's tests cover the mechanism at small scale only. AC5 (temp-disk/queue peaks, admission limits) - partially observed (RAM peak recorded above; no dedicated temp-disk-usage instrumentation was added, and the two probes did not exercise the `MIN_FREE_DISK_BYTES` admission limit under real pressure). AC6 (source-oracle/regression traceability) - the exact accepted-frame-count match at both probe scales is consistent with a source oracle; the full suite remaining green is the broader regression signal.
- Existing historical/workspace obligations (task_026's late-selection reconstruction, DPI/layout quarantine) are unchanged and not claimed resolved by this qualification work, per scope.
