## prod_021_peaklive_self_identifying_graph_lanes_and_durable_frame_sequence - PeakLive self-identifying graph lanes and durable frame sequence
> Date: 2026-09-09
> Status: Proposed
> Related request: `req_022_make_peaklive_graph_lanes_self_identifying_and_received_frames_globally_numbered`
> Related backlog: `item_112_render_concise_coloured_graph_lane_titles_with_subtle_lane_separation`, `item_113_expose_an_acquisition_wide_received_frame_sequence_in_trace`
> Related task: `task_022_deliver_readable_graph_lanes_and_a_global_received_frame_sequence`
> Related architecture: (none yet)
> Reminder: Update status, linked refs, scope, decisions, success signals, and open questions when you edit this doc.

# Overview
A focused operator-readability refinement for the existing diagnostic workspace. It makes each graph lane identifiable without technical noise, separates dense lanes visually, and exposes an acquisition-wide CAN-frame sequence in the bounded Trace table.

# Goals
- Let an operator identify a lane by its coloured horizontal signal title without rotating their reading or relying on a hover popup.
- Preserve technical signal provenance without making hashes and frame identifiers the primary visual identity.
- Let an operator see where a retained frame sits in the complete session even after the visible trace window has rotated.
- Preserve the existing dense non-scrolling graph workspace and bounded-memory behaviour.

# Non-goals
- Change CAN acquisition, transmission, bus configuration, recording format, replay ordering, or decoding outcomes.
- Retain every received frame in UI memory or change the 5,000-record TraceBuffer policy.
- Add manual curve-colour configuration, a new graphing library, or a scrolling graph-card layout.
- Use technical DBC hashes as a default graph title.

# Scope and guardrails
- In: scaffolded request, product, backlog, orchestration task, validation, and handoff context.
- Out: unrelated workflow docs and implementation of generated tasks.

# Key product decisions
- Use structured input as the source of truth for generated docs.
- Keep generated write paths local and repo-bounded.

# Success signals
- Generated docs pass lint and audit without broad manual rewrites.
- Context-pack output can be handed to an implementation agent directly.

# References
- Product back-reference: `req_022_make_peaklive_graph_lanes_self_identifying_and_received_frames_globally_numbered`
- Task back-reference: `task_022_deliver_readable_graph_lanes_and_a_global_received_frame_sequence`
