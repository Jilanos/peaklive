## item_015_validate_the_ux_parity_delivery_with_bounded_hardware_evidence - Validate the UX parity delivery with bounded hardware evidence
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 95%
> Confidence: 90%
> Progress: 100%
> Complexity: Medium
> Theme: Validation
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-24 14:43:19

# AI Context
- Summary: Defines the fake/replay-first validation matrix for UX parity and caps optional live CAN evidence at 2 minutes.
- Keywords: validate, parity, delivery, bounded, hardware, evidence
- Use when: Planning or recording validation evidence for the UX parity request, especially the no-long-CAN-test constraint and closeout matrix.
- Skip when: Implementing UI behavior before validation planning is needed, or running unrelated hardware acceptance outside this UX parity request.

# Problem
- The UX parity request touches many UI states, but the operator cannot support long live CAN runs for this phase.
- Validation must distinguish broad fake/replay coverage from optional short hardware smoke evidence.

# Scope
- In:
  - Define and run a validation matrix covering DBC workflows, acquisition options, signal explorer, graphs, cursors, panel configurations, inspector, and visual smoke states.
  - Use fake adapters, replay traces, DBC fixtures, and Qt tests for mandatory evidence.
  - Keep any live PCAN smoke test optional and capped at 2 minutes, with no broader acceptance dependency on live hardware.
  - Record command outputs, fixture names, screenshots if generated, and hardware-smoke duration in closeout evidence.
  - Keep Logics closeout honest if the optional hardware smoke is skipped.
- Out:
  - Running a 60-minute acceptance test.
  - Making release publication or installer signing part of this UX parity request.
  - Collecting or committing private vehicle captures or DBC contents.

# Acceptance criteria
- AC1: The validation matrix maps each request acceptance criterion to at least one automated or bounded manual evidence source.
- AC2: Mandatory validation runs without a connected CAN bus.
- AC3: Optional live bus validation, when run, lasts no more than 2 minutes and is documented as smoke evidence only.
- AC4: Closeout includes Logics lint/audit and the project's normal tests.

# AC Traceability
- request-AC8 -> This backlog slice. Proof: AC1: The validation matrix maps each request acceptance criterion to at least one automated or bounded manual evidence source.
- request-AC9 -> This backlog slice. Proof: AC2: Mandatory validation runs without a connected CAN bus.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_002_peaklive_cantracediag_grade_diagnostic_workspace`
- Architecture decision(s): (none yet)
- Request: `req_001_bring_peaklive_ux_to_cantracediag_parity`
- Primary task(s): `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta`

# Priority
- Priority: Medium - validation must be complete without requiring long bus availability.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta`

# Notes
- Task `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta` was finished via `logics-manager flow finish task` on 2026-08-24.
