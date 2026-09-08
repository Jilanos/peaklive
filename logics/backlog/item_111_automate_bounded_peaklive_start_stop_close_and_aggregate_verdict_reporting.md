## item_111_automate_bounded_peaklive_start_stop_close_and_aggregate_verdict_reporting - Automate bounded PeakLive start-stop-close and aggregate verdict reporting
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Windows UI automation and evidence verdict
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: Replaces manual status entry with safe automation of PeakLive's passive lifecycle and a metric-derived terminal verdict.
- Keywords: automate, bounded, peaklive, start, close, aggregate, verdict, reporting
- Use when: Selecting stable accessible controls or diagnostics-safe hooks for passive Start, Stop, Close, and evidence aggregation.
- Skip when: Automating risky vehicle actions, UI styling review, replay semantics, or user-facing CAN analysis.

# Problem
- The current interactive script requires an operator to navigate the application and type a status, which makes duration and outcome subjective.
- PeakLive must be commanded through stable accessible controls or a dedicated diagnostics-safe test surface to prove Start, Stop, and Close under actual load.

# Scope
- In:
  - Choose a maintained Windows UI Automation approach and use stable accessible names or test-safe app diagnostics to select passive mode, Start, Stop, and Close.
  - Fail safely when the intended passive configuration or required controls cannot be proven, never falling back to an unsafe mode.
  - Run a six-minute loaded observation and bounded Stop/close within the overall ten-minute deadline.
  - Aggregate process, UI, PCAN, and artifact observations into documented Pass/Fail/Blocked/NotRun thresholds.
  - Capture failure screenshots/UI tree diagnostics only when they cannot include trace content; otherwise record a redacted control-state snapshot.
- Out:
  - Visual pixel-perfect regression, DBC navigation, graph assessment, replay content validation, or export semantics.
  - Auto-answering Windows security, driver, or vehicle safety prompts.
  - Treating UI automation success as a statement about vehicle correctness.

# Acceptance criteria
- AC1: The MVP starts PeakLive only after identity, passive-mode, adapter, and bitrate preconditions are proven.
- AC2: It requests Start, observes loaded acquisition, requests Stop, and closes PeakLive without a human status entry.
- AC3: The final verdict is produced from recorded thresholds and contains a precise terminal reason.
- AC4: A supervised bench run completes within 600 seconds and reports only app-load evidence, not CAN semantics.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: The MVP starts PeakLive only after identity, passive-mode, adapter, and bitrate preconditions are proven.
- request-AC3 -> This backlog slice. Proof: AC2: It requests Start, observes loaded acquisition, requests Stop, and closes PeakLive without a human status entry.
- request-AC4 -> This backlog slice. Proof: AC3: The final verdict is produced from recorded thresholds and contains a precise terminal reason.
- request-AC5 -> This backlog slice. Proof: AC4: A supervised bench run completes within 600 seconds and reports only app-load evidence, not CAN semantics.
- request-AC6 -> This backlog slice. Proof: AC4: A supervised bench run completes within 600 seconds and reports only app-load evidence, not CAN semantics.
- request-AC7 -> This backlog slice. Proof: AC4: A supervised bench run completes within 600 seconds and reports only app-load evidence, not CAN semantics.
- request-AC8 -> This backlog slice. Proof: AC4: A supervised bench run completes within 600 seconds and reports only app-load evidence, not CAN semantics.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_020_peaklive_ten_minute_black_box_vehicle_load_qualification`
- Architecture decision(s): (none yet)
- Request: `req_021_automate_a_ten_minute_black_box_peaklive_vehicle_load_qualification`
- Primary task(s): `task_021_deliver_the_ten_minute_automated_black_box_peaklive_vehicle_load_mvp`

# Priority
- Priority: High - application behaviour, not operator interaction, must control the test's lifecycle and produce a release decision.
- Rationale: Set by scaffold input or defaulted for grooming.
