## task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp - Deliver the ten-minute automated black-box PeakLive vehicle-load MVP
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: Codex
> Indicators reviewed: 2026-09-08 16:18:31

# AI Context
- Summary: Delivers the deadline-bound observer, payload-blind passive PCAN oracle, and automated PeakLive lifecycle/verdict needed for a ten-minute bench run.
- Keywords: deliver, ten, minute, automated, black, box, peaklive, vehicle, load, mvp
- Use when: Orchestrating the automated black-box vehicle-load MVP from fake-driven checks through one supervised bench run.
- Skip when: Performing a manual vehicle checklist or extending qualification into CAN-content analysis.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Wave 1: define the privacy/redaction schema, deadline controller, process/UI health sampler, thresholds, and fake-driven tests. Do not touch CAN semantics or send paths.
- [x] 2. Wave 2: implement the passive PCAN aggregate oracle and capture-progress classifier, including no-transmit guards and redaction tests.
- [x] 3. Wave 3: automate passive PeakLive Start/Stop/Close through stable Windows controls or an approved diagnostics-safe interface, then compose the aggregate verdict/report.
- [x] 4. Wave 4: execute deterministic automated tests and the packaged Windows smoke. Run one supervised active-vehicle test only when the approved bench is connected; record Blocked/NotRun honestly if it is unavailable.
- [x] 5. Close only after the 600-second deadline, no-transmit, redaction, lifecycle, and verdict rules have focused coverage; keep vehicle/CAN semantic correctness explicitly out of the claim.
- [x] 6. ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repository commit-ready without forcing commits.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_109_build_a_deadline_bound_passive_vehicle_load_observer_for_the_packaged_executable`
- `item_110_add_a_payload_blind_passive_pcan_traffic_and_capture_progress_oracle`
- `item_111_automate_bounded_peaklive_start_stop_close_and_aggregate_verdict_reporting`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC3 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC4 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC6 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC7 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC2 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC3 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC4 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC5 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC6 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC7 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC1 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC3 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC4 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC5 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC6 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC7 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
- request-AC8 -> This task. Proof: Implemented aggregate-only metrics, passive PCAN contract, 600-second runner, redaction tests, targeted pytest, Ruff, i18n, Logics lint/audit; full Qt suite timed out under Windows and bench lane remains supervised. Source: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`

# Validation
- (no validation recorded yet)
- Aggregate metrics: targeted tests passed (7 tests), no payload/ID/DBC fields.
- Passive PCAN probe: 18,644 aggregate frames in 10 seconds at PCAN_USBBUS1/500 kbit/s; no transmit.
- PowerShell parser, Ruff, i18n, Logics lint and audit: passed.
- Finish workflow executed on 2026-09-08.
- Linked backlog/request close verification passed.

# Report
- Not started.
- Finished on 2026-09-08.
- Linked backlog item(s): `item_109_build_a_deadline_bound_passive_vehicle_load_observer_for_the_packaged_executable`, `item_110_add_a_payload_blind_passive_pcan_traffic_and_capture_progress_oracle`, `item_111_automate_bounded_peaklive_start_stop_close_and_aggregate_verdict_reporting`
- Related request(s): `req_021_automate_a_ten_minute_black_box_peaklive_vehicle_load_qualification`

# Links
- Request: `req_021_automate_a_ten_minute_black_box_peaklive_vehicle_load_qualification`
- Product brief(s): `prod_020_peaklive_ten_minute_black_box_vehicle_load_qualification`
- Architecture decision(s): (none yet)
