## item_019_deliver_display_only_trace_filtering_with_active_filter_chips - Deliver display-only trace filtering with active filter chips
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 95%
> Complexity: High
> Theme: Trace view
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-25 11:43:05

# AI Context
- Summary: Implements the display-only trace filtering the product scope already promises but the UI never had: ID, message, signal, direction, event kind, decode status and time range, frames/events toggles, removable active-filter chips, and persistence in the measurement profile.
- Keywords: trace filters, filter chips, display only, progressive disclosure, profile persistence
- Use when: Adding or changing any trace filter dimension, the filter chip row, the filtered-to-empty state, or how trace_filters is persisted and restored.
- Skip when: Hardware or driver-level acceptance filtering, regular-expression filter syntax, shared named presets, or anything that would filter the recorded ASC stream instead of the display.

# Problem
- The trace view has no filter control of any kind, although display-only filtering is a stated MVP capability.
- Without filtering, a dense multi-DBC bus makes the trace view unusable for targeted inspection.

# Scope
- In:
  - Add filter inputs for arbitration ID, message name, signal name, direction, event kind, decode status, and a time range.
  - Add frames-only and events-only toggles.
  - Show each active filter as an individually removable chip with a clear-all action.
  - Progressively disclose secondary filters so the default trace header stays compact.
  - Apply filtering to display only, never to the recorded ASC stream or the retained buffer used by graphs and export.
  - Persist the filter set in the measurement profile and restore it on reload.
  - Show an explicit filtered-to-empty state distinct from the no-data state.
- Out:
  - Hardware or driver-level acceptance filtering.
  - Saved named filter presets shared between profiles.
  - Regular-expression filter syntax.

# Acceptance criteria
- AC1: Each filter field narrows the displayed rows and leaves the retained buffer, graphs, and recording untouched.
- AC2: Combining several filters intersects them, and each active filter appears as a removable chip.
- AC3: Clear-all removes every filter and restores the full displayed trace.
- AC4: Frames-only and events-only toggles behave independently of the field filters.
- AC5: The filter set persists across an application restart on the same profile.
- AC6: A filter matching nothing shows a filtered-to-empty state distinct from the empty-trace state.
- AC7: Headless offscreen tests cover each filter dimension, chip removal, persistence, and the empty states.

# AC Traceability
- request-AC4 -> This backlog slice. Proof: AC1: Each filter field narrows the displayed rows and leaves the retained buffer, graphs, and recording untouched.
- request-AC12 -> This backlog slice. Proof: AC2: Combining several filters intersects them, and each active filter appears as a removable chip.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_003_peaklive_analyst_measurement_and_reporting_workspace`
- Architecture decision(s): (none yet)
- Request: `req_002_complete_the_peaklive_analyst_workspace_to_cantracediag_parity`
- Primary task(s): `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Priority
- Priority: High - the product scope already promises display-only trace filtering that does not exist.
- Rationale: Set by scaffold input or defaulted for grooming.
