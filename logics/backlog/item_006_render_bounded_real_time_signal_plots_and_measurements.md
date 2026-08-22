## item_006_render_bounded_real_time_signal_plots_and_measurements - Render bounded real-time signal plots and measurements
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 35%
> Complexity: High
> Theme: Live visualization
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-22 12:10:33

# AI Context
- Summary: Renders selected decoded signals in synchronized, bounded plots with downsampling, live/frozen navigation, and A/B measurements.
- Keywords: render, bounded, real, time, signal, plots, measurements
- Use when: Implementing signal selection, plot buffers, downsampling, zoom/pan, cursors, statistics, or live presentation latency.
- Skip when: Adding dashboards/alarms, changing DBC interpretation, capture contents, hardware control, replay parsing, or packaging.

# Problem
- Signal visualization must stay responsive without retaining or drawing every decoded sample indefinitely.

# Scope
- In:
  - Signal explorer, favorites, stacked synchronized plots, bounded sample buffers, and min/max envelope downsampling.
  - Live/frozen modes, time-window controls, zoom, pan, A/B cursors, values, delta, and range statistics.
  - Persisted signal selection and plot layout.
  - Reference-load latency and responsiveness measurements for at least eight signals.
- Out:
  - Dashboard gauges, alarm rules, scripting, and arbitrary custom widgets.

# Acceptance criteria
- AC1: Users can select decoded signals and render at least eight synchronized live plots under the reference load.
- AC2: Plot memory remains bounded and downsampling preserves visible extrema at each zoom level.
- AC3: Zoom, pan, live/frozen state, and A/B cursor measurements remain usable while recording continues independently.
- AC4: Typical acquisition-to-presentation latency stays below 250 ms on the reference machine or a visible degraded-state metric explains a breach.
- AC5: Plot and signal selections restore locally without decoding unrelated signals eagerly.

# AC Traceability
- request-AC6 -> This backlog slice. Proof: AC1: Users can select decoded signals and render at least eight synchronized live plots under the reference load.
- request-AC8 -> This backlog slice. Proof: AC2: Plot memory remains bounded and downsampling preserves visible extrema at each zoom level.
- request-AC9 -> This backlog slice. Proof: AC3: Zoom, pan, live/frozen state, and A/B cursor measurements remain usable while recording continues independently.
- request-AC12 -> This backlog slice. Proof: AC4: Typical acquisition-to-presentation latency stays below 250 ms on the reference machine or a visible degraded-state metric explains a breach.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_001_peaklive_windows_can_workstation`
- Architecture decision(s): (none yet)
- Request: `req_000_deliver_the_peaklive_windows_can_workstation_mvp`
- Primary task(s): `task_001_orchestrate_the_peaklive_windows_can_workstation_mvp`

# Priority
- Priority: Medium — plots depend on stable acquisition, recording, and decoding foundations.
- Rationale: Set by scaffold input or defaulted for grooming.
