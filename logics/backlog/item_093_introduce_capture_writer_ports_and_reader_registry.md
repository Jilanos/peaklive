## item_093_introduce_capture_writer_ports_and_reader_registry - Introduce capture-writer ports and reader registry
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 54%
> Complexity: Medium
> Theme: P3 extensibility
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: introduce, capture, writer, ports, reader, registry
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- ASC recorder embeds TRC branches and readers dispatch on suffix conditionals.

# Scope
- In:
  - Define CaptureWriter port.
  - Register readers by suffix.
  - Migrate ASC and TRC without semantic change.
- Out:
  - Implementing BLF or MDF now.

# Acceptance criteria
- ASC and TRC pass existing fixtures through ports and registry.
- BLF/MDF are recorded as next roadmap consumers.

# AC Traceability
- request-AC8 -> This backlog slice. Proof: ASC and TRC pass existing fixtures through ports and registry.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Low - format branching blocks BLF and MDF evolution
- Rationale: Set by scaffold input or defaulted for grooming.
