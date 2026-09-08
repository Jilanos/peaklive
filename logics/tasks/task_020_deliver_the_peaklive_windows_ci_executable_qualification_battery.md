## task_020_deliver_the_peaklive_windows_ci_executable_qualification_battery - Deliver the PeakLive Windows CI executable qualification battery
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.

# AI Context
- Summary: Delivers the PowerShell-driven qualification kit in four implementation lanes, then records automated and supervised hardware evidence against one hash-verified CI binary.
- Keywords: deliver, peaklive, windows, executable, qualification, battery
- Use when: Coordinating the implementation and validation of the Windows executable qualification battery.
- Skip when: Running an ad hoc bench check without producing reusable harness code and evidence.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Wave 1: implement the binary preflight, isolated sandbox, result schema, evidence manifest, and PowerShell orchestration contract; validate its path and metadata unit cases.
- [ ] 2. Wave 2: add the non-hardware packaged-executable smoke, identity, UI, viewport, keyboard, and profile-recovery lane using a documented Windows UI automation mechanism.
- [ ] 3. Wave 3: curate copied fixtures and add the replay, DBC, trace, graph, measurement, report, CSV, Parquet, and cancellation-output lane.
- [ ] 4. Wave 4: add the PCAN hardware preflight, guided safety prompts, live/recovery/endurance checklist, evidence capture, and Not-run/waiver workflow.
- [ ] 5. Wave 5: run the automated lanes against the supplied PeakLive CI executable, fix harness defects, rerun the full automated gate, then execute available hardware cases under operator supervision.
- [ ] 6. Close only after Logics validation passes and the report separates passed mandatory automated cases from failed, blocked, not-run, and waived hardware cases. Keep commits under operator control.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_105_create_an_isolated_powershell_qualification_harness_for_a_ci_built_peaklive_executable`
- `item_106_automate_packaged_windows_smoke_identity_ui_and_persisted_workspace_checks`
- `item_107_qualify_replay_dbc_analysis_graph_report_and_export_flows_in_the_packaged_executable`
- `item_108_run_safety_conscious_pcan_live_acquisition_recovery_and_endurance_acceptance`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_105_create_an_isolated_powershell_qualification_harness_for_a_ci_built_peaklive_executable`. Proof deferred to slice closeout.
- request-AC2 -> `item_105_create_an_isolated_powershell_qualification_harness_for_a_ci_built_peaklive_executable`. Proof deferred to slice closeout.
- request-AC6 -> `item_105_create_an_isolated_powershell_qualification_harness_for_a_ci_built_peaklive_executable`. Proof deferred to slice closeout.
- request-AC7 -> `item_105_create_an_isolated_powershell_qualification_harness_for_a_ci_built_peaklive_executable`. Proof deferred to slice closeout.
- request-AC2 -> `item_106_automate_packaged_windows_smoke_identity_ui_and_persisted_workspace_checks`. Proof deferred to slice closeout.
- request-AC3 -> `item_106_automate_packaged_windows_smoke_identity_ui_and_persisted_workspace_checks`. Proof deferred to slice closeout.
- request-AC6 -> `item_106_automate_packaged_windows_smoke_identity_ui_and_persisted_workspace_checks`. Proof deferred to slice closeout.
- request-AC7 -> `item_106_automate_packaged_windows_smoke_identity_ui_and_persisted_workspace_checks`. Proof deferred to slice closeout.
- request-AC4 -> `item_107_qualify_replay_dbc_analysis_graph_report_and_export_flows_in_the_packaged_executable`. Proof deferred to slice closeout.
- request-AC6 -> `item_107_qualify_replay_dbc_analysis_graph_report_and_export_flows_in_the_packaged_executable`. Proof deferred to slice closeout.
- request-AC7 -> `item_107_qualify_replay_dbc_analysis_graph_report_and_export_flows_in_the_packaged_executable`. Proof deferred to slice closeout.
- request-AC5 -> `item_108_run_safety_conscious_pcan_live_acquisition_recovery_and_endurance_acceptance`. Proof deferred to slice closeout.
- request-AC6 -> `item_108_run_safety_conscious_pcan_live_acquisition_recovery_and_endurance_acceptance`. Proof deferred to slice closeout.
- request-AC8 -> `item_108_run_safety_conscious_pcan_live_acquisition_recovery_and_endurance_acceptance`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_020_qualify_the_peaklive_ci_windows_executable_with_a_reproducible_functional_test_battery`
- Product brief(s): `prod_019_peaklive_windows_executable_qualification_kit`
- Architecture decision(s): (none yet)
