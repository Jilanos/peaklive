## task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery - Deliver the PeakLive Windows CI executable qualification battery
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
> Indicators reviewed: 2026-09-08 14:14:11

# AI Context
- Summary: Delivers the PowerShell-driven qualification kit in four implementation lanes, then records automated and supervised hardware evidence against one hash-verified CI binary.
- Keywords: deliver, peaklive, windows, executable, qualification, battery
- Use when: Coordinating the implementation and validation of the Windows executable qualification battery.
- Skip when: Running an ad hoc bench check without producing reusable harness code and evidence.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Wave 1: implement the binary preflight, isolated sandbox, result schema, evidence manifest, and PowerShell orchestration contract; validate its path and metadata unit cases.
- [x] 2. Wave 2: add the non-hardware packaged-executable smoke, identity, UI, viewport, keyboard, and profile-recovery lane using a documented Windows UI automation mechanism.
- [x] 3. Wave 3: curate copied fixtures and add the replay, DBC, trace, graph, measurement, report, CSV, Parquet, and cancellation-output lane.
- [x] 4. Wave 4: add the PCAN hardware preflight, guided safety prompts, live/recovery/endurance checklist, evidence capture, and Not-run/waiver workflow.
- [x] 5. Wave 5: run the automated lanes against the supplied PeakLive CI executable, fix harness defects, rerun the full automated gate, then execute available hardware cases under operator supervision.
- [x] 6. Close only after Logics validation passes and the report separates passed mandatory automated cases from failed, blocked, not-run, and waived hardware cases. Keep commits under operator control.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_105_create_an_isolated_powershell_qualification_harness_for_a_ci_built_peaklive_executable`
- `item_106_automate_packaged_windows_smoke_identity_ui_and_persisted_workspace_checks`
- `item_107_qualify_replay_dbc_analysis_graph_report_and_export_flows_in_the_packaged_executable`
- `item_108_run_safety_conscious_pcan_live_acquisition_recovery_and_endurance_acceptance`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> This task. Proof: PowerShell parser, packaged smoke, targeted pytest, ruff, i18n, lint and audit results recorded in task_020 Validation. Source: `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`
- request-AC2 -> This task. Proof: PowerShell parser, packaged smoke, targeted pytest, ruff, i18n, lint and audit results recorded in task_020 Validation. Source: `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`
- request-AC6 -> This task. Proof: PowerShell parser, packaged smoke, targeted pytest, ruff, i18n, lint and audit results recorded in task_020 Validation. Source: `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`
- request-AC7 -> This task. Proof: PowerShell parser, packaged smoke, targeted pytest, ruff, i18n, lint and audit results recorded in task_020 Validation. Source: `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`
- request-AC2 -> This task. Proof: PowerShell parser, packaged smoke, targeted pytest, ruff, i18n, lint and audit results recorded in task_020 Validation. Source: `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`
- request-AC3 -> This task. Proof: PowerShell parser, packaged smoke, targeted pytest, ruff, i18n, lint and audit results recorded in task_020 Validation. Source: `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`
- request-AC6 -> This task. Proof: PowerShell parser, packaged smoke, targeted pytest, ruff, i18n, lint and audit results recorded in task_020 Validation. Source: `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`
- request-AC7 -> This task. Proof: PowerShell parser, packaged smoke, targeted pytest, ruff, i18n, lint and audit results recorded in task_020 Validation. Source: `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`
- request-AC4 -> This task. Proof: PowerShell parser, packaged smoke, targeted pytest, ruff, i18n, lint and audit results recorded in task_020 Validation. Source: `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`
- request-AC6 -> This task. Proof: PowerShell parser, packaged smoke, targeted pytest, ruff, i18n, lint and audit results recorded in task_020 Validation. Source: `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`
- request-AC7 -> This task. Proof: PowerShell parser, packaged smoke, targeted pytest, ruff, i18n, lint and audit results recorded in task_020 Validation. Source: `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`
- request-AC5 -> This task. Proof: PowerShell parser, packaged smoke, targeted pytest, ruff, i18n, lint and audit results recorded in task_020 Validation. Source: `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`
- request-AC6 -> This task. Proof: PowerShell parser, packaged smoke, targeted pytest, ruff, i18n, lint and audit results recorded in task_020 Validation. Source: `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`
- request-AC8 -> This task. Proof: PowerShell parser, packaged smoke, targeted pytest, ruff, i18n, lint and audit results recorded in task_020 Validation. Source: `task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery`

# Validation
- (no validation recorded yet)
- PowerShell parser: passed
- Packaged smoke: passed; artifacts/windows-qualification/20260908-140636-208/summary.json; 4/4 mandatory cases passed
- Targeted pytest: 19 passed
- ruff: passed; i18n: valid; lint: passed; audit: 0 blocking and 0 warnings
- Finish workflow executed on 2026-09-08.
- Linked backlog/request close verification passed.

# Report
- Not started.
- Finished on 2026-09-08.
- Linked backlog item(s): `item_105_create_an_isolated_powershell_qualification_harness_for_a_ci_built_peaklive_executable`, `item_106_automate_packaged_windows_smoke_identity_ui_and_persisted_workspace_checks`, `item_107_qualify_replay_dbc_analysis_graph_report_and_export_flows_in_the_packaged_executable`, `item_108_run_safety_conscious_pcan_live_acquisition_recovery_and_endurance_acceptance`
- Related request(s): `req_020_qualify_the_peaklive_ci_windows_executable_with_a_reproducible_functional_test_battery`

# Links
- Request: `req_020_qualify_the_peaklive_ci_windows_executable_with_a_reproducible_functional_test_battery`
- Product brief(s): `prod_019_peaklive_windows_executable_qualification_kit`
- Architecture decision(s): (none yet)
