## prod_002_peaklive_cantracediag_grade_diagnostic_workspace - PeakLive CanTraceDiag-grade diagnostic workspace
> Date: 2026-08-24
> Status: Proposed
> Related request: `req_001_bring_peaklive_ux_to_cantracediag_parity`
> Related backlog: `item_009_analyze_the_cantracediag_to_peaklive_ux_delta`, `item_010_deliver_multi_dbc_library_and_conflict_management`, `item_011_upgrade_acquisition_setup_controls`, `item_012_bring_the_signal_explorer_to_cantracediag_parity`, `item_013_deliver_multi_graph_measurements_and_configurable_workspace_panels`, `item_014_apply_the_cantracediag_instrument_visual_system_to_peaklive`, `item_015_validate_the_ux_parity_delivery_with_bounded_hardware_evidence`
> Related task: `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta`
> Related architecture: (none yet)
> Reminder: Update status, linked refs, scope, decisions, success signals, and open questions when you edit this doc.

# Overview
A refined PeakLive desktop workspace that brings the proven CanTraceDiag multi-DBC, signal, plotting, trace, inspector, and instrument-style UX into the live Windows CAN acquisition application.

```mermaid
flowchart LR
    Ref[CanTraceDiag reference UX] --> Delta[PeakLive UX delta map]
    Delta --> DBC[Multi DBC library]
    Delta --> Acquire[Acquisition setup]
    DBC --> Signals[Grouped signal explorer]
    Signals --> Graphs[Multi graph cursors]
    Acquire --> Trace[Live trace inspector]
    Graphs --> Layout[Collapsible workspace]
    Trace --> Layout
    Layout --> Style[Instrument visual system]
    Style --> Validate[Bounded validation]
```

# Goals
- Make DBC and signal workflows efficient enough for real multi-DBC engineering sessions.
- Translate CanTraceDiag's dense instrument UX into a native Qt desktop application while preserving PeakLive's live acquisition and recording boundaries.
- Let operators configure acquisition modes safely and understand the distinction between application receive-only, passive listen-only, and controller acknowledgement.
- Support several synchronized graphs and measurement cursors without hiding raw trace or inspector context.
- Keep validation fast, repeatable, and mostly hardware-independent, with any live CAN smoke run capped at 2 minutes.

# Non-goals
- Copy CanTraceDiag's browser implementation directly or turn PeakLive into a PWA.
- Add frame transmission, cyclic transmit, dashboards, alarms, diagnostic protocols, CAN FD, LIN, or multi-channel acquisition.
- Require a 60-minute or otherwise long live CAN bus validation for this UX request.
- Persist private DBC contents into the repository or upload any vehicle data.
- Replace the existing PeakLive domain boundaries or recorder integrity model.

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
- Product back-reference: `req_001_bring_peaklive_ux_to_cantracediag_parity`
- Task back-reference: `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta`
