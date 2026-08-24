## item_009_analyze_the_cantracediag_to_peaklive_ux_delta - Analyze the CanTraceDiag to PeakLive UX delta
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 95%
> Confidence: 90%
> Progress: 100%
> Complexity: Medium
> Theme: UX delta analysis
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-24 14:43:19

# AI Context
- Summary: Produces the Qt-specific delta map between CanTraceDiag's reference diagnostic workspace and PeakLive's current desktop UI before implementation begins.
- Keywords: analyze, cantracediag, peaklive, delta
- Use when: Auditing CanTraceDiag reference behavior, documenting PeakLive UI gaps, or defining the implementation/test map for UX parity.
- Skip when: Directly implementing DBC library, acquisition controls, plots, styling, or validation after the delta map is already accepted.

# Problem
- The desired UX is described by a working sibling product and operator expectations, but PeakLive needs a concrete Qt-specific delta map before implementation begins.
- Without a checked-in map, later UI changes may copy superficial styling while missing workflow parity and validation limits.

# Scope
- In:
  - Inspect CanTraceDiag's signal explorer, plot, trace, inspector, fullscreen/layout, and visual style behavior from the supplied sibling checkout.
  - Inspect PeakLive's current PySide6 UI, profile model, DBC catalog, acquisition worker, and tests.
  - Create a repo-local delta analysis document that maps reference behaviors to PeakLive gaps, target modules, acceptance evidence, and explicit non-goals.
  - Record the validation strategy, including fake/replay-first coverage and a strict 2-minute cap for any optional live CAN smoke test.
  - Identify any UX decisions that need product confirmation before coding.
- Out:
  - Implementing the UI changes in the analysis slice.
  - Creating screenshots or mockups that embed real vehicle, company, supplier, or client data.
  - Changing the previously closed MVP request or reopening its task.

# Acceptance criteria
- AC1: The delta document lists each relevant CanTraceDiag UX pattern and the corresponding current PeakLive gap.
- AC2: The document names the PeakLive modules or tests expected to change for each gap.
- AC3: The document separates required parity, deliberate desktop-specific adaptation, and out-of-scope browser-only behavior.
- AC4: The test plan states that live CAN validation is optional, capped at 2 minutes, and never the only evidence for a backlog item.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: The delta document lists each relevant CanTraceDiag UX pattern and the corresponding current PeakLive gap.
- request-AC7 -> This backlog slice. Proof: AC2: The document names the PeakLive modules or tests expected to change for each gap.
- request-AC8 -> This backlog slice. Proof: AC3: The document separates required parity, deliberate desktop-specific adaptation, and out-of-scope browser-only behavior.
- request-AC9 -> This backlog slice. Proof: AC4: The test plan states that live CAN validation is optional, capped at 2 minutes, and never the only evidence for a backlog item.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_002_peaklive_cantracediag_grade_diagnostic_workspace`
- Architecture decision(s): (none yet)
- Request: `req_001_bring_peaklive_ux_to_cantracediag_parity`
- Primary task(s): `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta`

# Priority
- Priority: High - this is the control document for the UI parity implementation.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta`

# Notes
- Task `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta` was finished via `logics-manager flow finish task` on 2026-08-24.
