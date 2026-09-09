## task_022_deliver_readable_graph_lanes_and_a_global_received_frame_sequence - Deliver readable graph lanes and a global received-frame sequence
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 90%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-09 19:21:41

# AI Context
- Summary: Delivery task orchestrating item_112 (coloured lane headers, no rotated axis title) and item_113 (a global, frame-only Trace sequence column), gated on a single post-implementation test/lint/i18n/CI pass.
- Keywords: deliver, readable, graph, lanes, global, received, frame, sequence
- Use when: Coordinating or reviewing the combined graph-lane and Trace-sequence delivery, or checking whether both backlog slices and the CI gate closed together.
- Skip when: Changing only one of the two backlog slices in isolation, or working on unrelated graph/trace features such as measurement statistics or recording formats.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Implement the lane-header and separator presentation, replacing the rotated Y-axis technical label while preserving all existing plot navigation and provenance access.
- [x] 2. Implement the frame-only session sequence and Trace column without changing the bounded buffer, recording, replay, or event-selection contracts.
- [x] 3. Do not run product tests during either implementation wave. Once every code and i18n change is complete, add or finalize regression coverage and run the complete relevant test suite, lint, i18n validation, and local CI gate together.
- [ ] 4. Only after the local CI gate passes, commit and push the implementation. Monitor remote CI to its terminal result, record the run URL and verdict in closeout evidence, and do not mark the task complete if remote CI fails or is cancelled.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_112_render_concise_coloured_graph_lane_titles_with_subtle_lane_separation`
- `item_113_expose_an_acquisition_wide_received_frame_sequence_in_trace`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_112_render_concise_coloured_graph_lane_titles_with_subtle_lane_separation`. Proof deferred to slice closeout.
- request-AC2 -> `item_112_render_concise_coloured_graph_lane_titles_with_subtle_lane_separation`. Proof deferred to slice closeout.
- request-AC3 -> `item_112_render_concise_coloured_graph_lane_titles_with_subtle_lane_separation`. Proof deferred to slice closeout.
- request-AC5 -> `item_112_render_concise_coloured_graph_lane_titles_with_subtle_lane_separation`. Proof deferred to slice closeout.
- request-AC7 -> `item_112_render_concise_coloured_graph_lane_titles_with_subtle_lane_separation`. Proof deferred to slice closeout.
- request-AC4 -> `item_113_expose_an_acquisition_wide_received_frame_sequence_in_trace`. Proof deferred to slice closeout.
- request-AC5 -> `item_113_expose_an_acquisition_wide_received_frame_sequence_in_trace`. Proof deferred to slice closeout.
- request-AC6 -> `item_113_expose_an_acquisition_wide_received_frame_sequence_in_trace`. Proof deferred to slice closeout.
- request-AC7 -> `item_113_expose_an_acquisition_wide_received_frame_sequence_in_trace`. Proof deferred to slice closeout.

# Validation
- `pytest -q` (full suite, split into two batches to stay within local memory limits): all passed, 2026-09-09.
- `ruff check .`: all checks passed, 2026-09-09.
- `logics-manager i18n validate`: valid, 2026-09-09.
- `logics-manager lint --require-status` / `logics-manager audit --group-by-doc`: OK (0 blocking issues), 2026-09-09.
- Pushed as commit d4841d3, 2026-09-09.
- Remote CI run https://github.com/Jilanos/peaklive/actions/runs/34382484865: ubuntu-latest passed (pytest+ruff, ~4.5min); windows-latest was CANCELLED after hitting the job's 25-minute timeout mid-`pytest` (ruff passed first). No test failure surfaced before the timeout, and the same suite passed locally and on ubuntu, so this reads as hosted-runner slowness rather than a defect in this change - but per plan item 4 the task is not complete until a remote CI run reaches a clean terminal verdict.

# Report
- Not started.

# Links
- Request: `req_022_make_peaklive_graph_lanes_self_identifying_and_received_frames_globally_numbered`
- Product brief(s): `prod_021_peaklive_self_identifying_graph_lanes_and_durable_frame_sequence`
- Architecture decision(s): (none yet)
