## item_108_run_safety_conscious_pcan_live_acquisition_recovery_and_endurance_acceptance - Run safety-conscious PCAN live acquisition, recovery, and endurance acceptance
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Bench hardware acceptance
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: Defines operator-supervised PCAN evidence for the live behaviours that cannot be simulated faithfully by the packaged offline lanes.
- Keywords: run, safety, conscious, pcan, live, acquisition, recovery, endurance, acceptance
- Use when: Preparing or executing passive live-bus, recovery, degraded-shutdown, or endurance acceptance on an approved bench.
- Skip when: No active, approved CAN bench is available, or when a source-run mock test is sufficient.

# Problem
- Prior PCAN proof was limited and the documented 60-minute acceptance remains deferred.
- Driver, bitrate, active traffic, USB disconnect, and disk constraints make hardware tests unsafe to infer from automation alone.
- A simple pass/fail checklist cannot distinguish unavailable hardware from a functional regression.

# Scope
- In:
  - Implement a hardware-lane preflight and guided checklist with passive listen-only as default; require an explicit operator acknowledgment before normal receive mode or USB disruption.
  - Capture Windows, PCAN driver, adapter, channel, bitrate, disk space, fixture/build identity, and bus-traffic facts into the evidence manifest.
  - Exercise connect, stop, repeated Start/Stop, unplug/replug, degraded shutdown, final/partial capture pairs, replay of captured output, and 60-minute high-load recording when the bench is available.
  - Define observable limits and evidence: UI interactivity, state text, frame/event counters, recorder high-water mark, driver errors, capture paths, and output integrity.
  - Mark unavailable prerequisites Not run and record the reason; enable an explicit operator waiver for deferred endurance only.
- Out:
  - Transmission, fuzzing a vehicle bus, simulated driver faults that require unsupported tools, or unsupervised USB manipulation.
  - Treating no-traffic reception as a successful high-load test.
  - Automatically deleting captured bench evidence.

# Acceptance criteria
- AC1: Passive PCAN acquisition at the declared known bitrate demonstrates live incoming frames and a clean Stop with recorded state/counter evidence.
- AC2: Repeated Start/Stop and unplug/replug follow the documented recoverable or degraded state model without a frozen window or unsafe re-enable of Start.
- AC3: A 60-minute active-bus run, when available, records load/counters, capture rotation/sidecars, driver errors, disk outcome, and replayability of resulting output.
- AC4: Every skipped/blocked hardware case names the missing prerequisite and cannot be aggregated as a release pass without a recorded waiver.

# AC Traceability
- request-AC5 -> This backlog slice. Proof: AC1: Passive PCAN acquisition at the declared known bitrate demonstrates live incoming frames and a clean Stop with recorded state/counter evidence.
- request-AC6 -> This backlog slice. Proof: AC2: Repeated Start/Stop and unplug/replug follow the documented recoverable or degraded state model without a frozen window or unsafe re-enable of Start.
- request-AC8 -> This backlog slice. Proof: AC3: A 60-minute active-bus run, when available, records load/counters, capture rotation/sidecars, driver errors, disk outcome, and replayability of resulting output.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_019_peaklive_windows_executable_qualification_kit`
- Architecture decision(s): (none yet)
- Request: `req_020_qualify_the_peaklive_ci_windows_executable_with_a_reproducible_functional_test_battery`
- Primary task(s): `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`

# Priority
- Priority: High - only a real Windows driver and active bus can validate connection, bounded shutdown, unplug/replug behaviour, recording order, and sustained capture.
- Rationale: Set by scaffold input or defaulted for grooming.
