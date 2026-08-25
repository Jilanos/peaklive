## item_018_deliver_the_range_measurement_table - Deliver the range measurement table
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 95%
> Complexity: Medium
> Theme: Graph measurement
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-25 11:43:05

# AI Context
- Summary: Adds the analysis primitives PeakLive lacks entirely - nearest-sample cursor lookup, bounded range statistics (count, min, max, mean, standard deviation, RMS), and enum value distributions - and renders them as a measurement table under the graph stack.
- Keywords: range statistics, count, min, max, mean, std, rms, enum distribution, cursor values
- Use when: Implementing or changing statistics over the retained signal buffers, the per-signal cursor value lookup, or the measurement table rendered below the plots.
- Skip when: Statistics over the recorded ASC file rather than the retained buffer, frequency-domain analysis, curve fitting, or cross-signal correlation.

# Problem
- The cursor readout reports timestamps and a time delta only, with no signal value at either cursor.
- No count, min, max, mean, standard deviation, RMS, or enum distribution is computed anywhere in the application, so the operator must export data to answer basic questions.

# Scope
- In:
  - Add a range statistics function in the analysis layer computing sample count, min, max, mean, standard deviation, and RMS over a bounded time range for one signal.
  - Add a value distribution computation for enumerated or textual signals over the same range.
  - Add a nearest-sample cursor value lookup per shown signal for cursors A and B.
  - Render a measurement table under the graph stack combining, per shown signal, the value at A, the value at B, the delta, and the range statistics.
  - State explicitly when both cursors are not yet placed and when a signal has no sample in the range.
  - Keep the computation bounded so it stays responsive with the full retained buffer.
- Out:
  - Statistics over the recorded ASC file rather than the retained in-memory buffer.
  - Frequency-domain analysis, histograms as charts, or curve fitting.
  - Cross-signal correlation.

# Acceptance criteria
- AC1: For a numeric signal with known samples, the table reports the correct count, min, max, mean, standard deviation, and RMS between the two cursors.
- AC2: The table reports the value at cursor A, the value at cursor B, and their delta per shown signal.
- AC3: An enumerated or textual signal shows a value distribution instead of numeric statistics.
- AC4: With one or zero cursors placed, the table states that a range measurement needs both cursors.
- AC5: A signal with no sample inside the range is reported as such rather than as zero.
- AC6: Unit tests verify the statistics against fixture series, and headless offscreen tests verify the rendered table.

# AC Traceability
- request-AC3 -> This backlog slice. Proof: AC1: For a numeric signal with known samples, the table reports the correct count, min, max, mean, standard deviation, and RMS between the two cursors.
- request-AC12 -> This backlog slice. Proof: AC2: The table reports the value at cursor A, the value at cursor B, and their delta per shown signal.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_003_peaklive_analyst_measurement_and_reporting_workspace`
- Architecture decision(s): (none yet)
- Request: `req_002_complete_the_peaklive_analyst_workspace_to_cantracediag_parity`
- Primary task(s): `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Priority
- Priority: High - range statistics are the primary reason an analyst places two cursors.
- Rationale: Set by scaffold input or defaulted for grooming.
