## item_091_clarify_graph_cursors_and_trace_graph_linkage - Clarify graph cursors and trace graph linkage
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 59%
> Complexity: Medium
> Theme: P3 graph workflow
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: clarify, graph, cursors, trace, linkage
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Cursors lack labels and trace-to-graph navigation is absent.

# Scope
- In:
  - Label and style A/B.
  - Use live view change signal.
  - Add markers and bidirectional trace graph navigation.
- Out:
  - New measurement types.

# Acceptance criteria
- Selecting a trace and a graph point moves the linked context deterministically.

# AC Traceability
- request-AC6 -> This backlog slice. Proof: Selecting a trace and a graph point moves the linked context deterministically.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Low - cursor identity and navigation linkage are weak
- Rationale: Set by scaffold input or defaulted for grooming.
