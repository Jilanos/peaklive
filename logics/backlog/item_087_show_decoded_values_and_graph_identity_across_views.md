## item_087_show_decoded_values_and_graph_identity_across_views - Show decoded values and graph identity across views
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 63%
> Complexity: Low
> Theme: P2 diagnostic legibility
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: show, decoded, values, graph, identity, across, views
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Trace lacks decoded values and measurement rows are not tied to plot color.

# Scope
- In:
  - Add decoded-value trace presentation.
  - Color measurement signal identity with graph palette.
  - Make bus state visible beyond a 12-pixel LED.
- Out:
  - Changing decode rules.

# Acceptance criteria
- Fixture decode values appear in trace and graph-linked measurement rows are unambiguous.

# AC Traceability
- request-AC6 -> This backlog slice. Proof: Fixture decode values appear in trace and graph-linked measurement rows are unambiguous.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - decoded data exists but is hidden and curves lack correspondence
- Rationale: Set by scaffold input or defaulted for grooming.
