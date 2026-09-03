## task_017_implement_compact_graph_controls_and_unmistakable_signal_states - Implement compact graph controls and unmistakable signal states
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-04 00:32:09

# AI Context
- Summary: Deliver the compact graph command row and the unmistakable combo/eye/star signal-state slices while preserving navigation, cursor, and persistence behavior.
- Keywords: implement, compact, graph, controls, unmistakable, signal, states
- Use when: Implementing the linked graph-command-row and selector/signal-state backlog slices as one coordinated delivery.
- Skip when: Only a standalone decoding, acquisition, or export change is required.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Capture current rendered baselines for graph-header geometry, combo triggers, and eye/star states at the supported viewports.
- [x] 2. Remove the specified graph controls and window readout, enlarge fit glyphs, place Follow live inline, and make complete A/B cursor times durable at supported sizes.
- [x] 3. Replace the ambiguous combo trigger across the shared dark theme and strengthen shown/favorite rendering, keeping the inactive favorite star unchanged and selected favorite bright yellow.
- [x] 4. Add focused offscreen/rendered tests for every requested visual and behavioral contract, then run targeted UI, i18n, and full regression suites.
- [x] 5. Validate the request chain, audit and lint Logics docs, record closeout evidence, and leave the repository commit-ready.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_055_simplify_and_make_the_peaklive_graph_command_row_legible`
- `item_056_make_peaklive_selector_triggers_and_signal_eye_star_states_unmistakable`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC2 -> This task. Proof: Verified by ruff check . and the full offscreen pytest suite, including new tests/test_ui_compact_graph_and_signal_states.py plus updated tests/test_ui_workspace_refinement.py and tests/test_ui_signal_affordances.py. Source: `pytest -q (full suite, QT_QPA_PLATFORM=offscreen) and ruff check .`
- request-AC3 -> This task. Proof: Verified by ruff check . and the full offscreen pytest suite, including new tests/test_ui_compact_graph_and_signal_states.py plus updated tests/test_ui_workspace_refinement.py and tests/test_ui_signal_affordances.py. Source: `pytest -q (full suite, QT_QPA_PLATFORM=offscreen) and ruff check .`
- request-AC4 -> This task. Proof: Verified by ruff check . and the full offscreen pytest suite, including new tests/test_ui_compact_graph_and_signal_states.py plus updated tests/test_ui_workspace_refinement.py and tests/test_ui_signal_affordances.py. Source: `pytest -q (full suite, QT_QPA_PLATFORM=offscreen) and ruff check .`
- request-AC7 -> This task. Proof: Verified by ruff check . and the full offscreen pytest suite, including new tests/test_ui_compact_graph_and_signal_states.py plus updated tests/test_ui_workspace_refinement.py and tests/test_ui_signal_affordances.py. Source: `pytest -q (full suite, QT_QPA_PLATFORM=offscreen) and ruff check .`
- request-AC1 -> This task. Proof: Verified by ruff check . and the full offscreen pytest suite, including new tests/test_ui_compact_graph_and_signal_states.py plus updated tests/test_ui_workspace_refinement.py and tests/test_ui_signal_affordances.py. Source: `pytest -q (full suite, QT_QPA_PLATFORM=offscreen) and ruff check .`
- request-AC5 -> This task. Proof: Verified by ruff check . and the full offscreen pytest suite, including new tests/test_ui_compact_graph_and_signal_states.py plus updated tests/test_ui_workspace_refinement.py and tests/test_ui_signal_affordances.py. Source: `pytest -q (full suite, QT_QPA_PLATFORM=offscreen) and ruff check .`
- request-AC6 -> This task. Proof: Verified by ruff check . and the full offscreen pytest suite, including new tests/test_ui_compact_graph_and_signal_states.py plus updated tests/test_ui_workspace_refinement.py and tests/test_ui_signal_affordances.py. Source: `pytest -q (full suite, QT_QPA_PLATFORM=offscreen) and ruff check .`
- request-AC7 -> This task. Proof: Verified by ruff check . and the full offscreen pytest suite, including new tests/test_ui_compact_graph_and_signal_states.py plus updated tests/test_ui_workspace_refinement.py and tests/test_ui_signal_affordances.py. Source: `pytest -q (full suite, QT_QPA_PLATFORM=offscreen) and ruff check .`

# Validation
- (no validation recorded yet)
- ruff check . passed; pytest -q (full suite, QT_QPA_PLATFORM=offscreen) passed, including new tests/test_ui_compact_graph_and_signal_states.py
- Finish workflow executed on 2026-09-04.
- Linked backlog/request close verification passed.

# Report
- Not started.
- Finished on 2026-09-04.
- Linked backlog item(s): `item_055_simplify_and_make_the_peaklive_graph_command_row_legible`, `item_056_make_peaklive_selector_triggers_and_signal_eye_star_states_unmistakable`
- Related request(s): `req_016_compact_peaklive_graph_controls_and_unmistakable_signal_states`

# Links
- Request: `req_016_compact_peaklive_graph_controls_and_unmistakable_signal_states`
- Product brief(s): `prod_016_peaklive_compact_graph_controls_and_unmistakable_signal_states`
- Architecture decision(s): (none yet)
