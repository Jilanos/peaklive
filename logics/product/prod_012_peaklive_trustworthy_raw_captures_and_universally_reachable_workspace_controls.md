## prod_012_peaklive_trustworthy_raw_captures_and_universally_reachable_workspace_controls - PeakLive trustworthy raw captures and universally reachable workspace controls
> Date: 2026-09-02
> Status: Proposed
> Related request: `req_012_make_peaklive_lossless_capture_export_and_workspace_controls_trustworthy`
> Related backlog: `item_046_deliver_explicit_lossless_asc_and_trc_acquisition_capture_export`, `item_047_make_every_workspace_selector_and_visible_control_legible_stable_and_reachable`
> Related task: `task_013_implement_trustworthy_peaklive_capture_exports_and_universally_reachable_controls`
> Related architecture: (none yet)
> Reminder: Update status, linked refs, scope, decisions, success signals, and open questions when you edit this doc.

# Overview
PeakLive provides an honest split between decoded analysis exports and lossless raw CAN captures, while its selection and workspace controls remain stable, legible, non-animated, and reachable in every analysis mode.

# Goals
- Export every acquisition frame in ASC or PCAN-View text TRC through a durable, explicit capture contract.
- Prevent bounded decoded buffers from being mistaken for complete raw captures.
- Make mode switching and selection controls fully legible and reachable across the desktop workspace.
- Remove distracting menu deployment animation without compromising keyboard accessibility.

# Non-goals
- Reconstruct a lossless raw capture after an acquisition that was not recorded from its beginning.
- Add binary or proprietary trace formats, CAN transmission, cloud storage, or new decoding semantics.
- Change signal values, graph mathematics, trace filtering rules, or report content beyond control accessibility and export labelling.
- Copy another product's visual identity or interaction implementation.

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
- Product back-reference: `req_012_make_peaklive_lossless_capture_export_and_workspace_controls_trustworthy`
- Task back-reference: `task_013_implement_trustworthy_peaklive_capture_exports_and_universally_reachable_controls`
