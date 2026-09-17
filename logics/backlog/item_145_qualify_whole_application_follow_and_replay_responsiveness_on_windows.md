## item_145_qualify_whole_application_follow_and_replay_responsiveness_on_windows - Qualify whole-application follow and replay responsiveness on Windows
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Performance and integrity qualification
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-17 13:22:02

# AI Context
- Summary: Prove sustained live-follow latency, replay integrity and Windows performance against the reported workload.
- Keywords: qualify, whole, application, follow, replay, responsiveness, windows
- Use when: Delivering or qualifying the consolidated replay and live-follow responsiveness correction.
- Skip when: Changing unrelated workspace cosmetics, adapters or recording formats.

# Problem
- A local headless pass cannot establish interactive behavior on the packaged Windows workstation, and average timings can hide 30-second boundary stalls.

# Scope
- In:
  - Create deterministic synthetic traffic/DBC fixtures with one, six and nine lanes, mixed events, slow-progressing and stuck persistence; prioritize six-lane full-extent live acquisition on Windows 11 with recording active, measuring first-click latency before 15 seconds of acquisition as well as sustained operation, retain an off/full/trailing comparator and no-lane control.
  - Use a fake clock for exact boundary semantics and a real event-loop run of at least five minutes for performance; record input feedback, heartbeat max/p95, point age, CPU, queue peaks, worker counts and range-update rate.
  - Exercise menus, view switches, visible/hidden measurements, recording, manual navigation, enable/disable, Stop, repeated starts and replay completion; compare exact retained records and final bounds.
  - Run the reduced/removed queue_wait tolerance on hosted Windows and qualify the packaged executable with build and fixture metadata; record any missing hardware/user evidence as an open gate.
  - Update affected Logics proof and the handoff pack, reconcile any delivered overlapping item_123 work via the CLI, and close only when every applicable acceptance gate is proven.
- Out:
  - Claiming Windows/operator success from synthetic Linux tests.
  - Committing raw external captures or changing unrelated historical workflow statuses.

# Acceptance criteria
- AC1: Baseline and delivered measurements use identical documented fixtures and include boundary maxima and build/platform identifiers.
- AC2: Functional regressions expose original defects, supported-load latency/freshness budgets hold, and exact data/recording integrity passes across lifecycle transitions.
- AC3: Ruff, relevant tests, full CI checks and the revised hosted-Windows audit pass; packaged/operator evidence is present or qualification remains explicitly incomplete.
- AC4: Each request AC has concrete proof at closeout; root-cause limits, selected axis policy and outstanding operator questions are documented without invented results.

# AC Traceability
- request-AC1 -> This backlog slice. Proof deferred to slice closeout: matched before/after follow-mode and first-click measurements.
- request-AC2 -> This backlog slice. Proof deferred to slice closeout: nonblocking replay heartbeat and exact ordered consumption.
- request-AC3 -> This backlog slice. Proof deferred to slice closeout: bounded stalled-writer containment and generation-safe cancellation.
- request-AC4 -> This backlog slice. Proof deferred to slice closeout: sustained input latency, heartbeat and incoming-point freshness.
- request-AC5 -> This backlog slice. Proof deferred to slice closeout: measured continuous-versus-stepped policy decision.
- request-AC6 -> This backlog slice. Proof deferred to slice closeout: axis padding, short-window and manual-navigation semantics.
- request-AC7 -> This backlog slice. Proof deferred to slice closeout: retained data, recording and finalization integrity.
- request-AC8 -> This backlog slice. Proof deferred to slice closeout: regression results and hosted/packaged Windows evidence.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_031_responsive_live_graph_following_and_lossless_replay_presentation`
- Architecture decision(s): (none yet)
- Request: `req_034_restore_application_responsiveness_with_follow_live_and_nonblocking_replay_history`
- Primary task(s): `task_032_deliver_responsive_follow_live_and_complete_the_deferred_replay_handoff`

# Priority
- Priority: High
- Rationale: Prior short stop tests did not establish sustained responsiveness on the operator platform.
