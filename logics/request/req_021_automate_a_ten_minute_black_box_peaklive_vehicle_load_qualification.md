## req_021_automate_a_ten_minute_black_box_peaklive_vehicle_load_qualification - Automate a ten-minute black-box PeakLive vehicle-load qualification
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Objective packaged-application qualification under live CAN load
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-08 16:18:30

# AI Context
- Summary: Defines an objective, privacy-preserving 600-second qualification of the packaged PeakLive application under opaque live vehicle traffic.
- Keywords: automate, ten, minute, black, box, peaklive, vehicle, load, qualification
- Use when: Designing, implementing, or reviewing automated PeakLive health and capture-lifecycle qualification on an approved active vehicle bench.
- Skip when: Validating vehicle functions, CAN/DBC semantics, decoded signals, or any workflow that sends traffic to the vehicle.

# Needs
- Qualify PeakLive itself under an active vehicle CAN bus without decoding, classifying, storing, or judging CAN payloads, identifiers, signals, or vehicle behaviour.
- Replace operator-entered Pass/Fail judgements with one automated 600-second Windows run that measures application liveness, UI responsiveness, resource use, capture progress, controlled stop, and output finalization.
- Use the vehicle bus only as an opaque, passive receive-only traffic source. The harness and application must never transmit, mutate vehicle state, or include raw frame content in evidence.
- Produce one hash-keyed evidence bundle and deterministic verdict that clearly separates application failures, missing bench prerequisites, safety aborts, and traffic-not-present outcomes.

# Context
- The current PCAN passive probe on PCAN_USBBUS1 at 500 kbit/s received 18,644 frames in ten seconds. This confirms an available high-rate traffic source but does not prove PeakLive stays responsive or records correctly under the same load.
- The existing ten-minute runner is a useful safety checklist, but it asks the operator to judge every phase. It cannot objectively prove fluidity or distinguish a UI stall from an attentive operator delay.
- PeakLive is a receive-only product. Any test that calls a CAN send operation, enables a transmit control, or needs decoded vehicle semantics is outside scope and must fail closed.
- The test must run against the packaged CI executable with a hash-matching build metadata file and an isolated PEAKLIVE_DATA_DIR. Evidence may contain aggregate counts, rates, durations, process metrics, application state, hashes, and file metadata, but no payload bytes, arbitration IDs, decoded values, or DBC-derived content.
- A 600-second budget includes preflight, launch, passive connection, loaded observation, controlled Stop, artifact inspection, close, and report writing. A deadline breach is a failed run and triggers bounded cleanup.

# Acceptance criteria
- AC1: One command runs a packaged-executable qualification with a hard 600-second monotonic deadline, explicit cleanup, and a hash/identifier preflight before PeakLive starts.
- AC2: The harness opens only a passive receive-only PCAN channel and enforces a no-transmit policy. Its evidence and logs contain only aggregate traffic statistics, never CAN payloads, arbitration identifiers, signal names, decoded values, or DBC content.
- AC3: During a configurable loaded-observation window, the harness samples PeakLive process liveness, CPU, working set, handle count where available, window/UI responsiveness, application acquisition state, capture-file growth, and aggregate ingress/capture counters at bounded intervals.
- AC4: The verdict uses documented thresholds for unexpected process exit, UI response timeout, missing/non-growing capture, excessive sustained resource growth, driver errors, traffic absence, and deadline breach. It distinguishes Fail, Blocked, NotRun, and Pass without operator-entered case status.
- AC5: The harness performs and verifies one controlled Stop and close, then checks that only final or explicitly recoverable partial capture artifacts exist, without opening, parsing, or exposing CAN frame contents.
- AC6: Each run emits a machine-readable aggregate report, readable summary, build hash, Windows/driver/adapter facts, sampled metrics, screenshots or UI diagnostics on failure, and redacts forbidden CAN content by construction.
- AC7: The MVP has deterministic automated tests for deadline enforcement, no-transmit guard, redaction, verdict thresholds, artifact-state classification, and missing-hardware behaviour; no active vehicle is required for those tests.
- AC8: The final Windows bench run against the supplied CI binary records an objective verdict for the 10-minute scenario. It does not claim vehicle or CAN-protocol correctness.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_020_peaklive_ten_minute_black_box_vehicle_load_qualification`
- Architecture decision(s): (none yet)

# References
- docs/windows-ci-build-under-test.md
- docs/windows-qualification.md
- docs/vehicle-test-10m.md
- docs/windows-hardware-acceptance.md
- scripts/qualify-windows.ps1
- scripts/vehicle-test-10m.ps1
- src/peaklive/diagnostics.py
- src/peaklive/services/acquisition.py
- src/peaklive/ui/main_window.py
- src/peaklive/ui/session_controller.py
- src/peaklive/recording/asc.py
- artifacts/hardware-acceptance

# Backlog
- `item_109_build_a_deadline_bound_passive_vehicle_load_observer_for_the_packaged_executable`
- `item_110_add_a_payload_blind_passive_pcan_traffic_and_capture_progress_oracle`
- `item_111_automate_bounded_peaklive_start_stop_close_and_aggregate_verdict_reporting`
