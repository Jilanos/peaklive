## item_022_deliver_the_session_diagnostic_report - Deliver the session diagnostic report
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Reporting
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-25 11:36:53

# AI Context
- Summary: Adds the session synthesis PeakLive has none of: time range, frame and event volumes, frames per second, per-arbitration-ID counts, loaded DBCs with signal counts and applied conflict resolutions, decode coverage, and anomalies grouped by type, refreshable and exportable to a local file.
- Keywords: session report, volumes, decode coverage, anomalies by type, report export
- Use when: Collecting session facts during acquisition or replay, adding anomaly categories, or rendering and exporting the report view.
- Skip when: Report branding or customer-facing templates, statistical anomaly detection, automated fault diagnosis, and comparison between two sessions.

# Problem
- PeakLive has no session synthesis at all, so an operator finishing an acquisition cannot state what was captured, which DBCs applied, or what went wrong.
- Anomalies such as unknown arbitration IDs, DBC conflicts, malformed replay records, bus errors, and recording warnings are currently either transient or invisible.

# Scope
- In:
  - Collect session facts during acquisition and replay: time range, frame and event volumes, frames per second, and per-arbitration-ID counts.
  - Collect the loaded DBCs with signal counts, enabled state, and conflict resolutions applied.
  - Collect decode coverage, that is the share of frames resolved to a DBC message.
  - Collect anomalies grouped by type: unknown arbitration IDs, DBC conflicts, malformed replay records, bus errors, and recording warnings.
  - Add a report view in the workspace view selector with a refresh action.
  - Export the report to a local file.
  - Keep the collection bounded so it does not grow without limit during a long session.
- Out:
  - Report templates, branding, or customer-facing layouts.
  - Statistical anomaly detection or automated fault diagnosis.
  - Comparison of two sessions.

# Acceptance criteria
- AC1: The report shows the session time range, frame and event volumes, frames per second, and per-arbitration-ID counts.
- AC2: The report lists each loaded DBC with signal count, enabled state, and applied conflict resolutions.
- AC3: The report states decode coverage and groups anomalies by type with counts.
- AC4: The report is reachable from the workspace view selector and can be refreshed.
- AC5: The report exports to a local file whose content matches the displayed report.
- AC6: Report collection stays bounded during a sustained fixture session.
- AC7: Headless offscreen tests cover the report contents against fixture sessions, including an anomaly-bearing replay fixture.

# AC Traceability
- request-AC7 -> This backlog slice. Proof: AC1: The report shows the session time range, frame and event volumes, frames per second, and per-arbitration-ID counts.
- request-AC12 -> This backlog slice. Proof: AC2: The report lists each loaded DBC with signal count, enabled state, and applied conflict resolutions.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_003_peaklive_analyst_measurement_and_reporting_workspace`
- Architecture decision(s): (none yet)
- Request: `req_002_complete_the_peaklive_analyst_workspace_to_cantracediag_parity`
- Primary task(s): `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Priority
- Priority: Medium - the report turns a session into shareable evidence and closes the reference parity gap.
- Rationale: Set by scaffold input or defaulted for grooming.
