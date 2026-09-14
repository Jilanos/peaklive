## item_130_measure_and_gate_the_complete_trace_preparation_lifecycle - Measure and gate the complete trace preparation lifecycle
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 60%
> Complexity: Medium
> Theme: Trace loading evidence
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-14 09:59:11

# AI Context
- Summary: Expose SQLite preparation and truthful ready milestones missing from the old seven-stage benchmark.
- Keywords: measure, gate, complete, trace, preparation, lifecycle
- Use when: Building trustworthy before/after evidence and fail-closed benchmark verdicts.
- Skip when: Changing transport or writer ownership before their dedicated slices.

# Problem
- The profiler excludes the new dominant history write cost and the script can report success after timeout or budget overruns.
- The old one-signal small fixture does not qualify the operator's long dense captures.

# Scope
- In:
  - Priority rationale: establish valid failure and performance evidence before changing the loading architecture.
  - Instrument history append, summary/event maintenance, transaction commit, queue wait, GUI projection, first-data and final-ready separately. State overlapping-thread timing semantics and measure bounded overhead with profiling disabled.
  - Make the command fail for timeout, unsuccessful/partial replay, count mismatch and enabled budget violations; keep strict product thresholds distinct from environment-specific diagnostics.
  - Add configurable synthetic density/duration and ASC/TRC/event-heavy fixtures; ordinary CI uses bounded small cases and a scheduled/manual qualification tier uses typical and fifty-minute profiles.
  - Capture machine/build/configuration and raw structured metrics; do not commit generated captures or private source details.
- Out:
  - Changing runtime ingestion ownership in this measurement slice.
  - Treating Linux offscreen or widened CI tolerance as Windows qualification.

# Acceptance criteria
- AC1: Harness regressions prove nonzero exit for timeout, cancellation/failure, frame/event mismatch and forced stage or readiness overrun.
- AC2: Structured results distinguish history preparation from GUI work and first-data from final-ready; 0/1/8/16 signals actually exercise their expected historical sample counts.
- AC3: Synthetic density is configurable to the measured 1858 frames/s and the report identifies whether 1.756M/5.575M qualification cases were run or deferred.

# AC Traceability
- request-AC1 -> This backlog slice. Proof (partial - see Report for cancellation/event-mismatch gaps): `tests/test_lifecycle_harness.py::test_main_exits_nonzero_on_a_forced_timeout`, `::test_main_exits_nonzero_on_a_frame_count_mismatch`, `::test_main_exits_nonzero_when_history_persistence_fails`, `::test_enforce_budgets_fails_only_when_asked`.
- request-AC7 -> This backlog slice. Proof: `tests/test_lifecycle_harness.py::test_a_successful_small_case_measures_the_history_write_stage` (history_write stage now measured, separate from GUI stages, with first-data/ready milestones distinguished).

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_027_peaklive_responsive_and_trustworthy_long_trace_preparation`
- Architecture decision(s): (none yet)
- Request: `req_029_make_long_trace_loading_responsive_ordered_and_failure_explicit`
- Primary task(s): `task_028_deliver_responsive_ordered_and_measurable_long_trace_loading`

# Priority
- Priority: High
- Rationale: Establish valid failure and performance evidence before changing the loading architecture.

# Validation
- Wave 4 (2026-09-14): `analysis/profiling.py` gains two stages - `history_write` (the background writer's actual SQLite append/summary/commit, previously excluded from every stage entirely, per the audit's F4 finding) and `queue_wait` (the GUI-thread cost of `HistoryWriter.submit()` blocking for queue room). `StageProfiler` is now thread-safe (a lock around `add`/`count_frames`/`reset`/`profile`), since the writer thread and the GUI thread both report into the same shared `PROFILER`.
- `scripts/audit_trace_performance.py` was rewritten from a script whose `main()` unconditionally `return 0`'d (even while printing "OVER BUDGET" lines) into a harness whose exit code is a verdict: nonzero for a timeout, a source-accepted-frame-count mismatch, or a contained historical-persistence failure (item_132/item_133's `_history_failed`), always; nonzero for a stage budget overrun only with `--enforce-budgets` (off by default, keeping product budgets distinct from this harness's own diagnostics, per scope). It also now separates "first data" (first trace row observed) from "ready" (`_historical_view_ready`, i.e. the background writer has actually drained) as two distinct, separately-reported milestones instead of one "replay done" moment.
- `analysis/benchmark.py` gains `CaptureProfile.frame_interval_s` (configurable density; previously hardcoded to 1kHz) and `QUALIFICATION_PROFILES = (TYPICAL, LONG)`, generated at the operator's measured density (`OPERATOR_FRAMES_PER_SECOND = 1755746/944.788905 ≈ 1858.35 fps`): `TYPICAL` is 1,755,746 frames (~944.8s, the operator's typical capture) and `LONG` is 5,575,042 frames (~50 minutes at the same density) - the exact two workloads req_029/item_134 ask for. These are deliberately kept separate from `CAPTURE_PROFILES` (small/medium/large, 1kHz) so routine CI never accidentally generates and replays millions of frames; `--qualify` opts into them explicitly.
- Local proof: `tests/test_lifecycle_harness.py` (new, 7 cases, loading the script via `importlib` since `scripts/` is not a package): a real small-capture run measures `history_write` and reports first-data <= ready; `main()` exits 0 for a normal small run and nonzero for a forced near-zero-deadline timeout, a monkeypatched frame-count shortfall, and a monkeypatched `_history_failed` result; `--enforce-budgets` is proven to change the verdict for an otherwise-identical inflated-budget result; `QUALIFICATION_PROFILES` are proven to carry the exact operator-measured frame counts and density. Full suite `uv run pytest -ra` -> 650 passed; Ruff clean (including `scripts/`).

# Report
- Not yet covered, explicitly: AC1 also asks for "cancellation/failure" and "frame/**event**" mismatch coverage specifically; this wave's regressions cover timeout, historical-persistence failure, and frame-count mismatch, but not a harness-level test that forces a mid-replay Stop or asserts on an accepted bus-event count separately from frames (item_131 already covers event-count fidelity at the transport-unit level in `tests/test_replay_ordered_transport.py`, but the *harness* itself does not yet assert it end-to-end). AC3's "the report identifies whether 1.756M/5.575M qualification cases were run or deferred" is satisfied structurally (`--qualify` vs default, and every run prints its own frame count) but no qualification run has actually been executed and recorded yet in this wave - that is item_134's job, next.
