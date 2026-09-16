## item_140_use_clean_signal_display_titles_in_the_a_b_measurement_table - Use clean signal display titles in the A B measurement table
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Low
> Theme: Measurement presentation
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-16 15:24:02

# AI Context
- Summary: Use clean signal display titles in the A B measurement table.
- Keywords: clean, signal, display, titles, measurement, table
- Use when: Implementing or validating the responsive-stop and measurement-workspace follow-up to task_029 and task_030.
- Skip when: Changing unrelated decoding, recording formats, or data retention policies.

# Problem
- MeasurementPanel uses signal_label, exposing hash and frame ID beside Signal/A/B/delta values although a clean formatter already exists.

# Scope
- In:
  - Render Signal cells with the shared signal_display_title helper; preserve canonical signal keys for data lookups and distinct rows.
  - Keep technical provenance in an explicit tooltip/details affordance, including enough information to distinguish two identical Message.Signal titles.
  - Cover qualified names, legacy/plain names, duplicate display names, missing values and numeric/textual measurements.
- Out:
  - Renaming stored keys, changing exports or changing A/B/statistics calculations.
  - Globally stripping provenance from diagnostics.

# Acceptance criteria
- AC1: A qualified sample renders PowerStatus.Voltage, with no bracketed hash or frame ID in the visible Signal cell.
- AC2: Two sources with the same display title retain separate correct values and inspectable source identity.
- AC3: A/B, delta, units and existing statistics remain unchanged in focused tests.

# AC Traceability
- request-AC4 -> This backlog slice. Proof: AC1: A qualified sample renders PowerStatus.Voltage, with no bracketed hash or frame ID in the visible Signal cell.
- request-AC8 -> This backlog slice. Proof: AC2: Two sources with the same display title retain separate correct values and inspectable source identity.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_030_peaklive_responsive_stop_and_readable_measurement_controls`
- Architecture decision(s): (none yet)
- Request: `req_032_restore_responsive_acquisition_stop_and_polish_the_measurement_workspace`
- Primary task(s): `task_031_deliver_responsive_stop_and_polished_measurement_workspace_controls`

# Priority
- Priority: Medium - technical identifiers obscure the values analysts need to read.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_031_deliver_responsive_stop_and_polished_measurement_workspace_controls`

# Notes
- Task `task_031_deliver_responsive_stop_and_polished_measurement_workspace_controls` was finished via `logics-manager flow finish task` on 2026-09-16.
