## task_031_deliver_responsive_stop_and_polished_measurement_workspace_controls - Deliver responsive stop and polished measurement workspace controls
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-16 15:24:01
> Owner: maintainer@example.invalid

# AI Context
- Summary: Deliver responsive stop and polished measurement workspace controls.
- Keywords: deliver, responsive, polished, measurement, workspace, controls
- Use when: Implementing or validating the responsive-stop and measurement-workspace follow-up to task_029 and task_030.
- Skip when: Changing unrelated decoding, recording formats, or data retention policies.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

- Operator clarification (2026-09-16): the observed stop can leave the application unresponsive for more than 30 seconds. Feedback within 200 ms is accepted. The operation must either finish in less than 3 seconds or show an explicit saving/finalization popup or progress bar by the 3-second mark, while the GUI remains responsive.
- Evidence handoff: consult the external capture inventory in the linked request before selecting the Wave 1 reproduction fixture.

# Plan
- [x] 1. Wave 1 (High): inspect the external acquisition/sidecar candidates, reproduce and instrument the stop stall, implement the evidence-based repair and saving/finalization feedback, and prove the less-than-3-seconds-or-visible-progress contract with responsive GUI and lifecycle/data integrity.
- [x] 2. Wave 2 (Medium): clean measurement titles with duplicate-identity coverage.
- [x] 3. Wave 3 (Medium): inventory and preserve remaining profile-row actions, remove its visible layout and relocate the single bus indicator.
- [x] 4. Wave 4 (Medium; after Wave 3): apply the header order, reusable icons and sizing contract, then verify primary controls and stable overflow restoration.
- [x] 5. For each meaningful wave, update affected Logics evidence and commit the completed wave under ADR 009. Do not mark this scaffold implemented.
- [x] 6. Run targeted tests then repository CI checks, record before/after latency and visual evidence, validate Logics lint/audit/traceability and close via the CLI only after acceptance criteria are proven.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_139_diagnose_and_repair_acquisition_stop_stalls_with_follow_live`
- `item_140_use_clean_signal_display_titles_in_the_a_b_measurement_table`
- `item_141_remove_the_redundant_profile_row_and_relocate_bus_state_to_the_workspace_header`
- `item_142_unify_graph_header_action_order_and_icon_proportions`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_139_diagnose_and_repair_acquisition_stop_stalls_with_follow_live`. Proof: see this task's request-AC proof below and the slice's own Findings.
- request-AC2 -> `item_139_diagnose_and_repair_acquisition_stop_stalls_with_follow_live`. Proof: see this task's request-AC proof below and the slice's own Findings.
- request-AC3 -> `item_139_diagnose_and_repair_acquisition_stop_stalls_with_follow_live`. Proof: see this task's request-AC proof below and the slice's own Findings.
- request-AC8 -> `item_139_diagnose_and_repair_acquisition_stop_stalls_with_follow_live`. Proof: see this task's request-AC proof below and the slice's own Findings.
- request-AC4 -> `item_140_use_clean_signal_display_titles_in_the_a_b_measurement_table`. Proof: see this task's request-AC proof below and the slice's own Findings.
- request-AC8 -> `item_140_use_clean_signal_display_titles_in_the_a_b_measurement_table`. Proof: see this task's request-AC proof below and the slice's own Findings.
- request-AC5 -> `item_141_remove_the_redundant_profile_row_and_relocate_bus_state_to_the_workspace_header`. Proof: see this task's request-AC proof below and the slice's own Findings.
- request-AC8 -> `item_141_remove_the_redundant_profile_row_and_relocate_bus_state_to_the_workspace_header`. Proof: see this task's request-AC proof below and the slice's own Findings.
- request-AC6 -> `item_142_unify_graph_header_action_order_and_icon_proportions`. Proof: see this task's request-AC proof below and the slice's own Findings.
- request-AC7 -> `item_142_unify_graph_header_action_order_and_icon_proportions`. Proof: see this task's request-AC proof below and the slice's own Findings.
- request-AC8 -> `item_142_unify_graph_header_action_order_and_icon_proportions`. Proof: see this task's request-AC proof below and the slice's own Findings.
- request-AC1 -> This task. Proof: item_139 Findings record the diagnosed cause and a Follow off/full/trailing comparison on the documented synthetic fixture, with stage timings and the remaining reproduction limits.
- request-AC2 -> This task. Proof: tests/test_stop_responsiveness.py; measured maximum GUI heartbeat gap 87 ms (was 2197 ms), click-to-feedback 27 ms (was 133 ms), progress bar visible from 11 ms and a 39.2 s wind-down that stayed responsive throughout.
- request-AC3 -> This task. Proof: tests/test_stop_responsiveness.py covers durable settlement before success, restart gating during the wind-down, a writer that never drains, repeated cycles and an empty acquisition; tests/test_ui_lifecycle.py keeps the timeout and stale-generation contracts.
- request-AC4 -> This task. Proof: tests/test_measurement_titles.py: the Signal cell renders Message.Signal, duplicates keep distinct values and provenance, and A/B/delta/statistics are unchanged.
- request-AC5 -> This task. Proof: tests/test_workspace_setup_row.py: no visible strip and no layout band, every previously unique command still reachable, and one bus indicator beside Play/Stop in all four centre views.
- request-AC6 -> This task. Proof: tests/test_workspace_header_order.py: the documented order holds and survives repeated narrow/wide resizes and centre-view changes, with the three group rules between the four groups.
- request-AC7 -> This task. Proof: tests/test_workspace_header_order.py: the seven commands stay on one line at 1024x768, 1280x720 and 1600x900 with the shared 28px box and 16px canvas, no overlap; icons redraw per size and per state, and item_142 Findings record the visual review and the platform gap.
- request-AC8 -> This task. Proof: Focused suites above plus the full repository suite: 733 passed, ruff clean, Logics lint and audit clean.

# Validation
- (no validation recorded yet)
- ruff check . and QT_QPA_PLATFORM=offscreen pytest passed on 2026-09-16: All checks passed; 733 passed
- Finish workflow executed on 2026-09-16.
- Linked backlog/request close verification passed.

# Report
- Not started.
- Finished on 2026-09-16.
- Linked backlog item(s): `item_139_diagnose_and_repair_acquisition_stop_stalls_with_follow_live`, `item_140_use_clean_signal_display_titles_in_the_a_b_measurement_table`, `item_141_remove_the_redundant_profile_row_and_relocate_bus_state_to_the_workspace_header`, `item_142_unify_graph_header_action_order_and_icon_proportions`
- Related request(s): `req_032_restore_responsive_acquisition_stop_and_polish_the_measurement_workspace`

# Links
- Request: `req_032_restore_responsive_acquisition_stop_and_polish_the_measurement_workspace`
- Product brief(s): `prod_030_peaklive_responsive_stop_and_readable_measurement_controls`
- Architecture decision(s): (none yet)
