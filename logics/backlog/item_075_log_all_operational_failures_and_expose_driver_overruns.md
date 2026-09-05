## item_075_log_all_operational_failures_and_expose_driver_overruns - Log all operational failures and expose driver overruns
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 41%
> Complexity: Low
> Theme: P1 observability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: log, all, operational, failures, expose, driver, overruns
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Acquisition, replay, DBC, export, and adapter overruns are volatile or ignored.

# Scope
- In:
  - Log each error boundary.
  - Include normalized driver events in session anomalies and bus state.
- Out:
  - Remote diagnostics.

# Acceptance criteria
- Each named failure has structured local log evidence.
- Driver overrun and bus warnings are visible in diagnostics and report fixtures.

# AC Traceability
- request-AC4 -> This backlog slice. Proof: Each named failure has structured local log evidence.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Medium - diagnostics infrastructure has little operational coverage
- Rationale: Set by scaffold input or defaulted for grooming.
