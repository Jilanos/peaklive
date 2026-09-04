## item_068_make_manual_graph_zoom_disable_live_follow - Make manual graph zoom disable live follow
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Low
> Theme: P1 graph navigation
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: manual, graph, zoom, disable, live, follow
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Manual pyqtgraph range changes do not notify live-follow state.

# Scope
- In:
  - Connect manual range changes to live-follow disable.
  - Keep explicit re-follow command.
- Out:
  - New graph navigation modes.

# Acceptance criteria
- Wheel zoom remains visible after the next refresh and re-follow restores live extent.

# AC Traceability
- request-AC7 -> This backlog slice. Proof: Wheel zoom remains visible after the next refresh and re-follow restores live extent.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - mouse zoom is immediately undone
- Rationale: Set by scaffold input or defaulted for grooming.
