## prod_020_peaklive_ten_minute_black_box_vehicle_load_qualification - PeakLive ten-minute black-box vehicle-load qualification
> Date: 2026-09-08
> Status: Settled
> Related request: `req_021_automate_a_ten_minute_black_box_peaklive_vehicle_load_qualification`
> Related backlog: `item_109_build_a_deadline_bound_passive_vehicle_load_observer_for_the_packaged_executable`
> Related task: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
> Related architecture: (none yet)
> Reminder: Update status, linked refs, scope, decisions, success signals, and open questions when you edit this doc.
> Indicators reviewed: 2026-09-08 16:18:31

# Overview
PeakLive can be objectively qualified under real active-vehicle traffic in ten minutes, treating the CAN bus as an opaque passive load source and judging only the packaged application's health, responsiveness, recording lifecycle, and recoverable local output.

```mermaid
flowchart LR
  B[Hash verified binary] --> P[Passive opaque load]
  P --> O[Bounded app observer]
  O --> S[Controlled stop]
  S --> V[Aggregate verdict]
```

# Goals
- Make the qualification verdict derived from measured application facts rather than operator judgement of high-rate traffic.
- Keep vehicle interaction passive, receive-only, and payload-blind.
- Bound every run and its cleanup to ten minutes.
- Create portable, privacy-conscious evidence for the exact CI executable.

# Non-goals
- Validate CAN message semantics, identifiers, payloads, DBC decoding, signals, vehicle subsystems, or bus-protocol compliance.
- Transmit frames, acknowledge a safety-critical bus, change vehicle configuration, or test while driving.
- Replace long-duration endurance qualification; this is a short release-smoke/load gate.
- Collect raw vehicle traffic in the harness report or upload evidence to a cloud service.

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
- Product back-reference: `item_109_build_a_deadline_bound_passive_vehicle_load_observer_for_the_packaged_executable`
- Task back-reference: `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`
