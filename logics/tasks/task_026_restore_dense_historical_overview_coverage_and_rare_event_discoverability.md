## task_026_restore_dense_historical_overview_coverage_and_rare_event_discoverability - Restore dense historical overview coverage and rare event discoverability
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-09-12 16:30:42

# AI Context
- Summary: Sequence summary correctness, single-pass rendering, event fidelity and packaged qualification.
- Keywords: restore, dense, historical, overview, coverage, rare, event, discoverability
- Use when: Implementing the complete corrective chain from the supplied diagnosis and source/render probes.
- Skip when: Closing with queued CI, unresolved artifact qualification or option-only rendering evidence.

# Context
- Start with logics/analysis/dense_overview_diagnosis.md and its reproducible source/render probe. This task implements the correction; creating this corpus did not change application behavior.
- Summary/render correctness and the pulse/dip fidelity cases are ready to implement. Operator-specific build/DBC evidence gates packaged qualification; generic semantic anomaly classification is excluded.

# Plan
- [ ] 1. Read the diagnosis and existing historical-navigation brief; record the operator's confirmed before-load three-signal setup and the unverified build string. Reproduce the synthetic source/render failures before implementation.
- [ ] 2. Deliver High-priority summary completeness and reset correctness first; establish the fallback/index-ready contract and raw evidence oracle.
- [ ] 3. Integrate a single historical render reduction and transition/event anchors, including non-extreme two-frame events, a four-frame assertion after 50,000 quiet frames and a 250 A to 180 A dip lasting 100 ms. Preserve exact entry/extremum/recovery timecodes without requiring an amplitude threshold.
- [ ] 4. Complete the bounded request scheduler, revision/cache identity and nonmodal state/measurement guardrails; measure both returned data and actual display output.
- [ ] 5. Implement the small independent copyable-build label item after the High-priority correctness design, in time for final artifact qualification.
- [ ] 6. Run synthetic scaling and rare-event tests, Linux/Windows CI and packaging; reproduce the private trace's exact wheel-zoom sequence in the identified Windows executable and record every AC's evidence before closeout.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_121_make_historical_summary_coverage_complete_and_independent_of_ingest_batches`
- `item_122_render_dense_envelopes_and_rare_event_anchors_without_a_second_lossy_reduction`
- `item_123_bound_viewport_scheduling_and_expose_truthful_loading_and_measurement_states`
- `item_124_qualify_long_view_rare_event_fidelity_on_the_packaged_windows_application`
- `item_125_make_the_application_build_identifier_selectable_and_copyable`

# Definition of Done (DoD)
- [ ] All request acceptance criteria have behavioral evidence; every planned correction is implemented and reviewed.
- [ ] Synthetic source, render, rare-event, lifecycle and scaling regressions pass without loosening the declared budgets.
- [ ] Linux/Windows CI and Windows packaging pass for the delivered commit.
- [ ] The copied build identity and artifact hash accompany the operator's three-signal private wheel-zoom qualification.
- [ ] Open questions affecting claimed fidelity are resolved or explicit limitations are approved; no private signal identities or payloads enter versioned proof.
- [ ] Logics validation, lint/audit and the refreshed handoff are complete.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_121_make_historical_summary_coverage_complete_and_independent_of_ingest_batches`. Proof deferred to slice closeout.
- request-AC2 -> `item_121_make_historical_summary_coverage_complete_and_independent_of_ingest_batches`. Proof deferred to slice closeout.
- request-AC3 -> `item_121_make_historical_summary_coverage_complete_and_independent_of_ingest_batches`. Proof deferred to slice closeout.
- request-AC5 -> `item_121_make_historical_summary_coverage_complete_and_independent_of_ingest_batches`. Proof deferred to slice closeout.
- request-AC8 -> `item_121_make_historical_summary_coverage_complete_and_independent_of_ingest_batches`. Proof deferred to slice closeout.
- request-AC1 -> `item_122_render_dense_envelopes_and_rare_event_anchors_without_a_second_lossy_reduction`. Proof deferred to slice closeout.
- request-AC3 -> `item_122_render_dense_envelopes_and_rare_event_anchors_without_a_second_lossy_reduction`. Proof deferred to slice closeout.
- request-AC4 -> `item_122_render_dense_envelopes_and_rare_event_anchors_without_a_second_lossy_reduction`. Proof deferred to slice closeout.
- request-AC6 -> `item_122_render_dense_envelopes_and_rare_event_anchors_without_a_second_lossy_reduction`. Proof deferred to slice closeout.
- request-AC8 -> `item_122_render_dense_envelopes_and_rare_event_anchors_without_a_second_lossy_reduction`. Proof deferred to slice closeout.
- request-AC1 -> `item_123_bound_viewport_scheduling_and_expose_truthful_loading_and_measurement_states`. Proof deferred to slice closeout.
- request-AC5 -> `item_123_bound_viewport_scheduling_and_expose_truthful_loading_and_measurement_states`. Proof deferred to slice closeout.
- request-AC6 -> `item_123_bound_viewport_scheduling_and_expose_truthful_loading_and_measurement_states`. Proof deferred to slice closeout.
- request-AC8 -> `item_123_bound_viewport_scheduling_and_expose_truthful_loading_and_measurement_states`. Proof deferred to slice closeout.
- request-AC1 -> `item_124_qualify_long_view_rare_event_fidelity_on_the_packaged_windows_application`. Proof deferred to slice closeout.
- request-AC2 -> `item_124_qualify_long_view_rare_event_fidelity_on_the_packaged_windows_application`. Proof deferred to slice closeout.
- request-AC3 -> `item_124_qualify_long_view_rare_event_fidelity_on_the_packaged_windows_application`. Proof deferred to slice closeout.
- request-AC4 -> `item_124_qualify_long_view_rare_event_fidelity_on_the_packaged_windows_application`. Proof deferred to slice closeout.
- request-AC5 -> `item_124_qualify_long_view_rare_event_fidelity_on_the_packaged_windows_application`. Proof deferred to slice closeout.
- request-AC6 -> `item_124_qualify_long_view_rare_event_fidelity_on_the_packaged_windows_application`. Proof deferred to slice closeout.
- request-AC7 -> `item_124_qualify_long_view_rare_event_fidelity_on_the_packaged_windows_application`. Proof deferred to slice closeout.
- request-AC8 -> `item_124_qualify_long_view_rare_event_fidelity_on_the_packaged_windows_application`. Proof deferred to slice closeout.
- request-AC7 -> `item_125_make_the_application_build_identifier_selectable_and_copyable`. Proof deferred to slice closeout.
- request-AC8 -> `item_125_make_the_application_build_identifier_selectable_and_copyable`. Proof deferred to slice closeout.

# Validation
- Corpus preparation only (2026-09-12): request flow validation has zero findings; Ruff and Logics lint pass; repository audit has zero blockers and one pre-existing prod_021 missing-diagram warning. The synthetic probe reproduces partial summary coverage, zero rendered points after automatic reduction, stale overview after clear, and loss of a non-extreme 100 ms analog dip. Implementation and packaged acceptance remain outstanding; task progress stays 0%.

# Report
- Additional operator screenshot: selection after loading stays blank with 1705746 dropped frames, matching the capture census minus the 50000-frame cache. Tail-only decoding updates SeriesStore but not HistoricalSignalStore. See the diagnosis for this second failure path. Full-file background reconstruction is recommended; its preparation-latency scope choice awaits operator response and is not yet an implementation commitment.

# Links
- Request: `req_026_restore_dense_historical_curves_and_preserve_rare_diagnostic_signal_events`
- Product brief(s): `prod_025_discoverable_rare_diagnostic_events_in_dense_historical_views`
- Architecture decision(s): (none yet)
