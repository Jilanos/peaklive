## item_104_make_trace_context_actions_safe_for_frame_and_event_records - Make trace context actions safe for frame and event records
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 75%
> Complexity: Low
> Theme: Record-aware trace interaction
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-07 12:36:49

# AI Context
- Summary: Make trace context actions record-aware so both events and frames can be copied safely while identifier filtering is offered only for valid frame identifiers.
- Keywords: trace-view, context-menu, event-row, frame-row, copy, identifier-filter, qt-slot
- Use when: Changing trace row lookup, context-menu construction, event copying, or identifier-dependent trace actions.
- Skip when: Redesigning trace styling, graph commands, multi-row selection, or data retention without changing context actions.

# Problem
- The trace menu builds an identifier-filter action for every record, including events whose arbitration identifier is absent.
- Formatting the missing identifier raises before the menu opens, so Copy is also unavailable for diagnostic events.
- The context action surface does not distinguish frame-only commands from commands valid for every record.

# Scope
- In:
  - Build common context actions for every trace record and add identifier-dependent actions only for frames with a valid identifier.
  - Keep copy output useful for both frame and event rows and preserve retained-record lookup safety.
  - Prepare offscreen event/frame menu coverage, with execution deferred to final verification.
- Out:
  - A general context-menu redesign, new graph commands, multi-row copy, or unrelated trace styling.
  - Running UI tests during this implementation slice.

# Acceptance criteria
- AC1: Right-clicking frame and event rows opens a usable menu without an exception.
- AC2: Copy is available for both record types, while identifier filtering appears only when a valid identifier exists.
- AC3: Existing frame context behavior and retained-record safety remain unchanged.
- AC4: Offscreen context-menu tests execute only during the final verification phase.

# AC Traceability
- request-AC12 -> This backlog slice. Proof: AC1: Right-clicking frame and event rows opens a usable menu without an exception.
- request-AC13 -> This backlog slice. Proof: AC4: Offscreen context-menu tests execute only during the final verification phase.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_018_peaklive_trustworthy_measurement_identity_and_recoverable_local_evidence`
- Architecture decision(s): (none yet)
- Request: `req_019_eliminate_peaklive_second_pass_integrity_identity_and_recovery_gaps`
- Primary task(s): `task_019_implement_every_second_pass_peaklive_integrity_and_recovery_correction`

# Priority
- Priority: Medium - every event-row context click currently raises and hides the safe copy workflow needed for diagnostics.
- Rationale: Set by scaffold input or defaulted for grooming.
