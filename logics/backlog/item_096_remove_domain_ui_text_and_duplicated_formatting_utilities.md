## item_096_remove_domain_ui_text_and_duplicated_formatting_utilities - Remove domain UI text and duplicated formatting utilities
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Low
> Theme: P3 code coherence
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: remove, domain, text, duplicated, formatting, utilities
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Domain produces English UI text and several helpers are duplicated.

# Scope
- In:
  - Move labels to presentation resources.
  - Remove unused column labels.
  - Consolidate duplicate default paths, numeric parsing, hex formatting, and bitrate definitions.
- Out:
  - Localization beyond English.

# Acceptance criteria
- Domain modules contain no presentation labels and one canonical helper exists for each consolidated concern.

# AC Traceability
- request-AC9 -> This backlog slice. Proof: Domain modules contain no presentation labels and one canonical helper exists for each consolidated concern.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Low - domain and presentation boundaries are blurred
- Rationale: Set by scaffold input or defaulted for grooming.
