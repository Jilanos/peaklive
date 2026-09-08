## item_109_build_a_deadline_bound_passive_vehicle_load_observer_for_the_packaged_executable - Build a deadline-bound passive vehicle-load observer for the packaged executable
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Black-box Windows process and UI observability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: Builds the clock, process, resource, and responsiveness observer that makes the ten-minute application-health verdict deterministic.
- Keywords: build, deadline, bound, passive, vehicle, load, observer, packaged, executable
- Use when: Implementing deadline handling, app process sampling, UI liveness probes, or verdict threshold tests.
- Skip when: Reading CAN content, operating a vehicle, or relying on an operator to decide whether the UI is fluid.

# Problem
- The existing runner can launch PeakLive and ask human questions, but it does not enforce phase timing or produce a verdict from liveness and responsiveness samples.
- A loaded UI can appear responsive between occasional manual interactions while its event loop is already stalling or its resource usage is growing unsafely.

# Scope
- In:
  - Implement a monotonic 600-second runner with bounded phase budgets and guaranteed bounded process cleanup.
  - Sample PeakLive process liveness, CPU, working set, handle count where Windows exposes it, and a bounded UI/window responsiveness probe at a documented cadence.
  - Acquire app-visible acquisition state and capture progress through stable diagnostics or UI automation, without reading CAN content.
  - Write timestamped aggregate samples and a threshold-based verdict to JSON and Markdown.
  - Provide deterministic fake-process and fake-clock tests for timeout, stall, exit, and resource-growth rules.
- Out:
  - Using screenshot pixels as the sole health signal.
  - Adding cloud telemetry, collecting raw trace rows, or modifying vehicle traffic.
  - Extending the test beyond ten minutes.

# Acceptance criteria
- AC1: The observer kills or cleanly closes its owned PeakLive process by the 600-second deadline and records the terminal reason.
- AC2: Samples are bounded in memory and contain only aggregate application/process facts.
- AC3: Defined UI stall, process-exit, deadline, and sustained-resource-growth fixtures produce deterministic Fail verdicts.
- AC4: A missing adapter, unavailable active traffic, or denied UI automation produces Blocked/NotRun rather than Pass.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: The observer kills or cleanly closes its owned PeakLive process by the 600-second deadline and records the terminal reason.
- request-AC3 -> This backlog slice. Proof: AC2: Samples are bounded in memory and contain only aggregate application/process facts.
- request-AC4 -> This backlog slice. Proof: AC3: Defined UI stall, process-exit, deadline, and sustained-resource-growth fixtures produce deterministic Fail verdicts.
- request-AC6 -> This backlog slice. Proof: AC4: A missing adapter, unavailable active traffic, or denied UI automation produces Blocked/NotRun rather than Pass.
- request-AC7 -> This backlog slice. Proof: AC4: A missing adapter, unavailable active traffic, or denied UI automation produces Blocked/NotRun rather than Pass.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_020_peaklive_ten_minute_black_box_vehicle_load_qualification`
- Architecture decision(s): (none yet)
- Request: `req_021_automate_a_ten_minute_black_box_peaklive_vehicle_load_qualification`
- Primary task(s): `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`

# Priority
- Priority: High - without a bounded observer, a short vehicle test cannot distinguish a frozen application from an operator delay or an unbounded test process.
- Rationale: Set by scaffold input or defaulted for grooming.
