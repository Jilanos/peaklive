## item_084_tokenize_spacing_geometry_and_stable_focus - Tokenize spacing geometry and stable focus
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 59%
> Complexity: Medium
> Theme: P2 layout consistency
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: tokenize, spacing, geometry, stable, focus
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Fourteen spacing values, competing heights, and focus borders shift layout.

# Scope
- In:
  - Define spacing, height, radius, and focus tokens.
  - Apply them across workspace and dialogs.
- Out:
  - Full layout redesign.

# Acceptance criteria
- Controls on a shared row use one height and focus never shifts content.

# AC Traceability
- request-AC6 -> This backlog slice. Proof: Controls on a shared row use one height and focus never shifts content.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - inconsistent geometry accumulates visual friction
- Rationale: Set by scaffold input or defaulted for grooming.
