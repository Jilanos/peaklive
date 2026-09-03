## task_014_implement_configurable_collision_safe_peaklive_recording_names - Implement configurable, collision-safe PeakLive recording names
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-03 10:37:16

# AI Context
- Summary: Coordinates the service-first naming change with the profile-scoped Qt editor while preserving raw capture evidence semantics.
- Keywords: implement, configurable, collision, safe, peaklive, recording, names
- Use when: Delivering either recording naming reservation or its settings/preview UI as one integrated task.
- Skip when: Working on unrelated trace, graph, adapter, or export changes.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Characterize current RecordingSettings, recorder lifecycle, profile persistence, and ASC/TRC tests; introduce a clock-injectable naming/reservation contract with focused failure and concurrency fixtures.
- [ ] 2. Wire reservation and next-iteration persistence into acquisition startup and recorder finalization without changing raw capture ordering, formats, rotations, or incomplete-capture evidence.
- [ ] 3. Add the localized Recording settings action/editor with folder browse, validation, profile binding, reset, and immediate non-mutating preview.
- [ ] 4. Run targeted unit/service/profile/offscreen UI tests, the full test suite and Logics validation; refresh the Logics index and leave unrelated worktree changes untouched.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_048_deliver_a_deterministic_recording_naming_and_reservation_service`
- `item_049_expose_profile_recording_settings_with_live_filename_preview`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC3 -> `item_048_deliver_a_deterministic_recording_naming_and_reservation_service`. Proof deferred to slice closeout.
- request-AC5 -> `item_048_deliver_a_deterministic_recording_naming_and_reservation_service`. Proof deferred to slice closeout.
- request-AC6 -> `item_048_deliver_a_deterministic_recording_naming_and_reservation_service`. Proof deferred to slice closeout.
- request-AC7 -> `item_048_deliver_a_deterministic_recording_naming_and_reservation_service`. Proof deferred to slice closeout.
- request-AC8 -> `item_048_deliver_a_deterministic_recording_naming_and_reservation_service`. Proof deferred to slice closeout.
- request-AC1 -> `item_049_expose_profile_recording_settings_with_live_filename_preview`. Proof deferred to slice closeout.
- request-AC2 -> `item_049_expose_profile_recording_settings_with_live_filename_preview`. Proof deferred to slice closeout.
- request-AC4 -> `item_049_expose_profile_recording_settings_with_live_filename_preview`. Proof deferred to slice closeout.
- request-AC6 -> `item_049_expose_profile_recording_settings_with_live_filename_preview`. Proof deferred to slice closeout.
- request-AC8 -> `item_049_expose_profile_recording_settings_with_live_filename_preview`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_013_add_canalyzer_style_recording_configuration_and_collision_safe_acquisition_naming_to_peaklive`
- Product brief(s): `prod_013_peaklive_configurable_and_collision_safe_acquisition_recording`
- Architecture decision(s): (none yet)
