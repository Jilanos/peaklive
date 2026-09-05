## item_086_create_an_acquisition_command_surface_with_gated_actions - Create an acquisition command surface with gated actions
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 61%
> Complexity: Low
> Theme: P2 lifecycle UX
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: create, acquisition, command, surface, gated, actions
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Start and Stop appear under View and actions are not retained for gating.

# Scope
- In:
  - Add Acquisition menu.
  - Retain actions and update enabled state by lifecycle phase.
- Out:
  - New lifecycle phases.

# Acceptance criteria
- Menu, buttons, and shortcuts present identical enabled state and invalid actions explain why.

# AC Traceability
- request-AC6 -> This backlog slice. Proof: Menu, buttons, and shortcuts present identical enabled state and invalid actions explain why.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - lifecycle commands are misplaced and shortcuts can silently no-op
- Rationale: Set by scaffold input or defaulted for grooming.
