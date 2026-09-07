## prod_018_peaklive_trustworthy_measurement_identity_and_recoverable_local_evidence - PeakLive trustworthy measurement identity and recoverable local evidence
> Date: 2026-09-07
> Status: Proposed
> Related request: `req_019_eliminate_peaklive_second_pass_integrity_identity_and_recovery_gaps`
> Related backlog: `item_098_drain_live_acquisition_completely_through_a_bounded_authoritative_handoff`, `item_099_make_replay_completion_truthful_under_backpressure_and_cancellation`, `item_100_publish_exports_and_recording_artifacts_transactionally_without_collision`, `item_101_preserve_complete_can_frame_identity_and_make_decoding_total`, `item_102_qualify_decoded_signal_identity_across_databases_and_identifiers`, `item_103_prevent_stale_concurrent_profile_writers_from_erasing_setup_changes`, `item_104_make_trace_context_actions_safe_for_frame_and_event_records`
> Related task: `task_019_implement_every_second_pass_peaklive_integrity_and_recovery_correction`
> Related architecture: (none yet)
> Reminder: Update status, linked refs, scope, decisions, success signals, and open questions when you edit this doc.

# Overview
PeakLive preserves every accepted measurement record and its identity across live acquisition, replay, decoding, visualization, persistence, and local output, while failures remain explicit and prior evidence remains recoverable.

```mermaid
flowchart LR
    Sources[Live adapters and replay files] --> Handoff[Bounded acknowledged handoff]
    Handoff --> Identity[Lossless frame and signal identity]
    Identity --> Session[Authoritative session state]
    Identity --> Evidence[Transactional capture and export evidence]
    Session --> UI[Safe trace graphs and measurements]
    Profiles[Concurrency-safe profiles] --> UI
    Waves[Six code-only implementation waves] --> Verify[One deferred final verification phase]
    Verify --> Trust[Complete and recoverable operator evidence]
    Evidence --> Trust
    UI --> Trust
```

# Goals
- Keep durable capture, replay results, session facts, retained frames, decoded series, and operator-visible status mutually consistent.
- Prevent cancellation, collision, rotation, or concurrent application instances from silently deleting or overwriting local evidence and configuration.
- Represent CAN direction, remote DLC, identifier format, and decoded-signal provenance without ambiguity.
- Bound live and replay handoffs without converting overload into silent loss or false success.
- Deliver one end-of-development verification phase covering all integrity scenarios after implementation is complete.

# Non-goals
- Add new capture formats, new hardware adapters, frame transmission, cloud storage, or remote collaboration.
- Change series, frame-cache, or trace retention capacities except where an upstream handoff requires an explicit bound.
- Redesign unrelated graph controls, visual styling, workspace layout, or the active graph-legibility work.
- Claim Windows or live-hardware certification from Linux/offscreen automated evidence.
- Run tests repeatedly after each implementation slice; validation is intentionally deferred until all development slices are complete.

# Scope and guardrails
- In: scaffolded request, product, backlog, orchestration task, validation, and handoff context.
- Out: unrelated workflow docs and implementation of generated tasks.

# Key product decisions
- Authoritative ingestion and bounded presentation are separate responsibilities; accepted records cannot disappear merely to protect UI responsiveness.
- Completion is asserted only after acknowledged delivery, and every cancellation, replacement, overload, parser, decode, or publication failure remains explicit.
- Final local output is published transactionally from operation-owned temporary artifacts, and all related capture/sidecar names share one collision domain.
- CAN frame and decoded-signal keys carry machine-stable provenance independently of concise operator labels.
- Profile concurrency produces a deterministic merge or visible stale-write rejection, never silent last-writer data loss.
- Tests are neither authored nor executed incrementally during the six implementation waves; regression authoring and all automated gates occur together after development is complete.

# Success signals
- A stopped live session and a successful replay contain every accepted source frame exactly once while overload remains bounded.
- Cancellation, rotation, collision, concurrent instances, remote frames, and identity collisions preserve prior evidence and expose truthful outcomes.
- Operators can distinguish same-number CAN identities and same-name decoded signals throughout UI, persistence, analysis, and output.
- The final deferred regression matrix, full Linux/offscreen suite, lint, internationalization checks, and Logics validation pass after all implementation waves complete.

# References
- Product back-reference: `req_019_eliminate_peaklive_second_pass_integrity_identity_and_recovery_gaps`
- Task back-reference: `task_019_implement_every_second_pass_peaklive_integrity_and_recovery_correction`
