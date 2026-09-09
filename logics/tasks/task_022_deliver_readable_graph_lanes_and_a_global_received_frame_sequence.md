## task_022_deliver_readable_graph_lanes_and_a_global_received_frame_sequence - Deliver readable graph lanes and a global received-frame sequence
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
- Summary: (unfilled: replace before this doc is used)
- Keywords: deliver, readable, graph, lanes, global, received, frame, sequence
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Implement the lane-header and separator presentation, replacing the rotated Y-axis technical label while preserving all existing plot navigation and provenance access.
- [ ] 2. Implement the frame-only session sequence and Trace column without changing the bounded buffer, recording, replay, or event-selection contracts.
- [ ] 3. Do not run product tests during either implementation wave. Once every code and i18n change is complete, add or finalize regression coverage and run the complete relevant test suite, lint, i18n validation, and local CI gate together.
- [ ] 4. Only after the local CI gate passes, commit and push the implementation. Monitor remote CI to its terminal result, record the run URL and verdict in closeout evidence, and do not mark the task complete if remote CI fails or is cancelled.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_112_render_concise_coloured_graph_lane_titles_with_subtle_lane_separation`
- `item_113_expose_an_acquisition_wide_received_frame_sequence_in_trace`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

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
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_022_make_peaklive_graph_lanes_self_identifying_and_received_frames_globally_numbered`
- Product brief(s): `prod_021_peaklive_self_identifying_graph_lanes_and_durable_frame_sequence`
- Architecture decision(s): (none yet)
