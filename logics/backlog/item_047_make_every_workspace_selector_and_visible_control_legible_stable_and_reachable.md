## item_047_make_every_workspace_selector_and_visible_control_legible_stable_and_reachable - Make every workspace selector and visible control legible, stable, and reachable
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Workspace control reachability and geometry
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: workspace, selector, visible, control, legible, stable, reachable
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- workspaceModeSelector is hard-coded to 76 px, which cannot contain its full translated labels, and it disappears when the graph panel is hidden in Trace-only or Report-only modes.
- Selection menus visibly deploy with animation, contrary to the requested direct instrument interaction.
- The compact desktop UI has individual width constraints but lacks a complete, mode-by-mode containment audit for labels and action controls.

# Scope
- In:
  - Move or duplicate the workspace mode control through one authoritative state binding so it remains visible and functional in every workspace mode without divergent state or persistence behavior.
  - Size the selector from translated text and platform font metrics, with no label elision for the mode choices at benchmark viewports.
  - Disable application-configured popup/reveal animations for all application-owned combo/menu selectors, including profile, channel, bitrate, controller mode, export, and workspace mode, while preserving pointer, keyboard, focus, and accessibility behavior.
  - Audit all visible buttons, combo boxes, menu entries, and key control labels in Combo, Graph-only, Trace-only, and Report-only at supported desktop sizes; correct meaningful clipping, overlap, insufficient hit area, or inaccessible compact controls.
  - Add stable offscreen geometry, mode-transition, popup-policy, and accessibility regression coverage, including profile-layout persistence.
- Out:
  - Changing acquisition lifecycle rules, CAN protocol behavior, trace filtering semantics, graph calculations, or report data.
  - A wholesale visual redesign, external-product replication, touch-first layouts, or arbitrary enlargement that removes graph workspace priority.
  - Animating other unrelated operating-system UI beyond PeakLive-owned controls.

# Acceptance criteria
- AC1: Full translated workspace-mode text is contained and readable at all benchmark viewports.
- AC2: Each workspace mode retains a visible, keyboard-operable route to every other mode, including a direct recovery route from Trace-only and Report-only.
- AC3: Application-owned selection popups have no configured deployment animation and retain accessible, predictable interaction.
- AC4: The cross-mode control audit has automated evidence that visible text and controls are contained, operable, and accessible without regressing existing graph, trace, report, acquisition, or profile tests.

# AC Traceability
- request-AC6 -> This backlog slice. Proof: AC1: Full translated workspace-mode text is contained and readable at all benchmark viewports.
- request-AC7 -> This backlog slice. Proof: AC2: Each workspace mode retains a visible, keyboard-operable route to every other mode, including a direct recovery route from Trace-only and Report-only.
- request-AC8 -> This backlog slice. Proof: AC3: Application-owned selection popups have no configured deployment animation and retain accessible, predictable interaction.
- request-AC9 -> This backlog slice. Proof: AC4: The cross-mode control audit has automated evidence that visible text and controls are contained, operable, and accessible without regressing existing graph, trace, report, acquisition, or profile tests.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_012_peaklive_trustworthy_raw_captures_and_universally_reachable_workspace_controls`
- Architecture decision(s): (none yet)
- Request: `req_012_make_peaklive_lossless_capture_export_and_workspace_controls_trustworthy`
- Primary task(s): `task_013_implement_trustworthy_peaklive_capture_exports_and_universally_reachable_controls`

# Priority
- Priority: High - Trace-only currently strands an operator away from mode switching, and clipped controls block core analysis actions.
- Rationale: Set by scaffold input or defaulted for grooming.
