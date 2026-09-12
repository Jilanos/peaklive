## item_125_make_the_application_build_identifier_selectable_and_copyable - Make the application build identifier selectable and copyable
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 48%
> Complexity: Low
> Theme: Operator build identity usability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-12 17:10:01

# AI Context
- Summary: Allow exact read-only build identity selection and copying in normal app chrome.
- Keywords: application, build, identifier, selectable, copyable
- Use when: Preventing operator build transcription errors with existing Qt text interaction.
- Skip when: Changing version numbering or replacing the About dialog.

# Problem
- The operator has to transcribe the displayed build string manually, leaving an ambiguous artifact identity in the report.

# Scope
- In:
  - Make the existing build label read-only selectable by mouse/keyboard and support ordinary copy behavior using the canonical build_info().identifier.
  - Preserve existing normal-workspace visibility, compact layout, tooltip and accessible name. Use existing Qt text interaction rather than inventing another version source.
  - Verify selection and clipboard behavior offscreen where reliable, plus copy/paste in the Windows artifact.
- Out:
  - Version format changes, editable build values and a broad About-dialog redesign.

# Acceptance criteria
- AC7: The exact displayed canonical identifier can be selected/copied without editing or obstructing the workspace and matches the artifact identity.
- AC8: The packaged qualification records the copied identifier rather than manually interpreting a typed timestamp.

# AC Traceability
- request-AC7 -> This backlog slice. Proof: AC7: The exact displayed canonical identifier can be selected/copied without editing or obstructing the workspace and matches the artifact identity.
- request-AC8 -> This backlog slice. Proof: AC8: The packaged qualification records the copied identifier rather than manually interpreting a typed timestamp.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_025_discoverable_rare_diagnostic_events_in_dense_historical_views`
- Architecture decision(s): (none yet)
- Request: `req_026_restore_dense_historical_curves_and_preserve_rare_diagnostic_signal_events`
- Primary task(s): `task_026_restore_dense_historical_overview_coverage_and_rare_event_discoverability`

# Priority
- Priority: Low - small independent usability correction that prevents qualification transcription errors.
- Rationale: Set by scaffold input or defaulted for grooming.
