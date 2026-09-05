## item_080_set_fusion_and_an_application_wide_dark_palette - Set Fusion and an application-wide dark palette
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 41%
> Complexity: Medium
> Theme: P2 visual system
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: set, fusion, application, wide, dark, palette
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- No fixed Qt style or full palette and stylesheet is window-only.

# Scope
- In:
  - Set Fusion.
  - Apply named dark palette and application stylesheet.
  - Style alternate rows and table corner.
- Out:
  - Platform-native theme support.

# Acceptance criteria
- Dialogs, tooltips, alternate rows, and table corner use the same dark palette.

# AC Traceability
- request-AC6 -> This backlog slice. Proof: Dialogs, tooltips, alternate rows, and table corner use the same dark palette.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - native fragments break dark UI consistency
- Rationale: Set by scaffold input or defaulted for grooming.
