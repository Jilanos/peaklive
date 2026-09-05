## item_076_enforce_class_surface_architecture_budgets - Enforce class-surface architecture budgets
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 39%
> Complexity: Medium
> Theme: P1 maintainability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: enforce, class, surface, architecture, budgets
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Multiple inheritance distributes one implicit window state across files.

# Scope
- In:
  - Add AST-tested class surface budgets.
  - Forbid defensive getattr on owned state.
  - Extract two autonomous mixins into collaborators.
- Out:
  - A wholesale UI rewrite.

# Acceptance criteria
- Structural tests fail when declared class-surface budgets are exceeded.
- The selected collaborators have explicit interfaces and no owned-state getattr workaround.

# AC Traceability
- request-AC9 -> This backlog slice. Proof: Structural tests fail when declared class-surface budgets are exceeded.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - file-length rules hide a 143-method mixin monolith
- Rationale: Set by scaffold input or defaulted for grooming.
