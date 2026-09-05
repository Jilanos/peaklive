## item_094_extend_adapter_capability_ports_and_roadmap_discovery - Extend adapter capability ports and roadmap discovery
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 56%
> Complexity: Medium
> Theme: P3 adapter extensibility
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: extend, adapter, capability, ports, roadmap, discovery
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Adapter capabilities exist partially but are not consumed; discovery and bitrate scan are absent.

# Scope
- In:
  - Add channels and supported-bitrates to adapter port.
  - Drive controls from capabilities.
  - Document bitrate scan and interface discovery roadmap phases.
- Out:
  - Physical adapter discovery implementation.

# Acceptance criteria
- UI uses adapter-provided capabilities with deterministic fake-adapter tests.
- Roadmap defines hardware acceptance for scan and discovery.

# AC Traceability
- request-AC8 -> This backlog slice. Proof: UI uses adapter-provided capabilities with deterministic fake-adapter tests.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Low - channel and bitrate facts are hard-coded in the UI
- Rationale: Set by scaffold input or defaulted for grooming.
