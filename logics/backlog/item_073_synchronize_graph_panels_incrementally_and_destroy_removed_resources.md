## item_073_synchronize_graph_panels_incrementally_and_destroy_removed_resources - Synchronize graph panels incrementally and destroy removed resources
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 34%
> Complexity: Medium
> Theme: P1 graph lifetime
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: synchronize, graph, panels, incrementally, destroy, removed, resources
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Graph sync recreates plots without deterministic teardown.

# Scope
- In:
  - Reuse unchanged graph lanes.
  - Disconnect and delete removed lanes.
  - Test repeated deferred decode changes.
- Out:
  - New graph layouts.

# Acceptance criteria
- Repeated sync leaves stable widget and connection counts.
- Existing plots preserve their intended state.

# AC Traceability
- request-AC7 -> This backlog slice. Proof: Repeated sync leaves stable widget and connection counts.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - graph rebuilds leak widgets and connections
- Rationale: Set by scaffold input or defaulted for grooming.
