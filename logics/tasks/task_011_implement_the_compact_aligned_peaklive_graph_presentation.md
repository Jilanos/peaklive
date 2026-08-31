## task_011_implement_the_compact_aligned_peaklive_graph_presentation - Implement the compact aligned PeakLive graph presentation
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 90%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-08-31 16:02:46
> Owner: Codex

# AI Context
- Summary: Coordinate the presentation-only graph refinement from geometry tests through a compact toolbar, aligned plot lanes, and complete UI validation.
- Keywords: implement, compact, aligned, peaklive, graph, presentation
- Use when: A developer needs the ordered delivery plan and evidence expectations for the graph-header, axis-alignment, and non-scrolling-canvas work.
- Skip when: Starting unrelated replay, acquisition, decode, export, Trace filter, or visual-brand work.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Capture the current graph-header, PlotWidget, ViewBox, axis, and scrollbar geometry in focused offscreen regression tests at the benchmark resolutions.
- [ ] 2. Implement the single-row compact header, preserving direct access, keyboard operation, labels, tooltips, and dynamic readouts.
- [ ] 3. Implement a shared axis-gutter and deterministic lane-layout policy, then verify visual alignment and non-scrolling behaviour with multiple signals and stress labels.
- [ ] 4. Run targeted and full UI validation, i18n validation for changed copy, and Logics validation; record implementation evidence and close out only after the delivery is complete.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_039_deliver_a_compact_aligned_non_scrolling_peaklive_graph_surface`

# Definition of Done (DoD)
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_039_deliver_a_compact_aligned_non_scrolling_peaklive_graph_surface`. Proof deferred to slice closeout.
- request-AC2 -> `item_039_deliver_a_compact_aligned_non_scrolling_peaklive_graph_surface`. Proof deferred to slice closeout.
- request-AC3 -> `item_039_deliver_a_compact_aligned_non_scrolling_peaklive_graph_surface`. Proof deferred to slice closeout.
- request-AC4 -> `item_039_deliver_a_compact_aligned_non_scrolling_peaklive_graph_surface`. Proof deferred to slice closeout.
- request-AC5 -> `item_039_deliver_a_compact_aligned_non_scrolling_peaklive_graph_surface`. Proof deferred to slice closeout.
- request-AC6 -> `item_039_deliver_a_compact_aligned_non_scrolling_peaklive_graph_surface`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_010_refine_the_peaklive_graph_header_axis_alignment_and_scrolling_behaviour`
- Product brief(s): `prod_010_peaklive_compact_aligned_measurement_graphs`
- Architecture decision(s): (none yet)
