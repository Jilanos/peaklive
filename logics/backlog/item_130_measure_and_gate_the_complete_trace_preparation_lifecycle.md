## item_130_measure_and_gate_the_complete_trace_preparation_lifecycle - Measure and gate the complete trace preparation lifecycle
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Trace loading evidence
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-13 23:32:48

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
- request-AC1 -> This backlog slice. Proof: AC1: Harness regressions prove nonzero exit for timeout, cancellation/failure, frame/event mismatch and forced stage or readiness overrun.
- request-AC7 -> This backlog slice. Proof: AC2: Structured results distinguish history preparation from GUI work and first-data from final-ready; 0/1/8/16 signals actually exercise their expected historical sample counts.

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
