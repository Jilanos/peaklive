## req_032_restore_responsive_acquisition_stop_and_polish_the_measurement_workspace - Restore responsive acquisition stop and polish the measurement workspace
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Acquisition responsiveness and measurement workspace clarity
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-16 13:45:23

# AI Context
- Summary: Restore responsive acquisition stop and polish the measurement workspace.
- Keywords: restore, responsive, acquisition, polish, measurement, workspace
- Use when: Implementing or validating the responsive-stop and measurement-workspace follow-up to task_029 and task_030.
- Skip when: Changing unrelated decoding, recording formats, or data retention policies.

# Needs
- Diagnose and fix application unresponsiveness when stopping acquisition; the operator suspects Follow live makes it more likely, which remains a hypothesis to test.
- Remove technical provenance suffixes from signal titles in the A/B/delta/statistics table.
- Remove the redundant visible row beginning with Measurement profile now that configuration belongs in the top menus; move the bus status into the shared Graphs/Trace/Report header.
- Reorganize Play, Stop, Follow live, cursors A/B and both Fit actions on one line, with coherent icon shapes and icon-to-button proportions.

# Context
- Baseline main d9b2f40 includes completed menu/navigation work (task_029) and GUI-owned cyclic GC (task_030); this request is a follow-up, not evidence those changes caused the reported freeze.
- _stop_acquisition already requests stop asynchronously and starts a shutdown timer. Investigate completion, ingestion draining, history readiness, graph refresh, A/B statistics, range-signal recursion and GC using measurements before choosing a repair.
- MeasurementPanel.refresh renders signal_label while graph lane titles and SignalSummaryPanel already use signal_display_title. Example anonymized unwanted title: PowerStatus.Voltage [a1b2c3d4 0x123]; intended title: PowerStatus.Voltage. This is internal identifier exposure in presentation, not a claim of external data exfiltration.
- AcquisitionBar still owns the profile selector, bus state and lifecycle wiring; removing its visible row must first preserve any remaining unique profile selection, recovery, import/export or status access in the existing top menus/header.
- WorkspaceHeaderBar currently assembles Fit, Play, Stop, A/B and readouts before deferrable Follow live/Fit Y; its overflow implementation reparents controls. Review stable ordering after shrink/expand as part of this change.
- Existing text glyphs reuse a play triangle for Follow live and rely on font sizing; use code-native Qt/vector icons with a consistent visual language.

- Operator clarification (2026-09-16): the observed stop can leave the application unresponsive for more than 30 seconds. Feedback within 200 ms is accepted. The operation must either finish in less than 3 seconds or show an explicit saving/finalization popup or progress bar by the 3-second mark, while the GUI remains responsive.
- Read-only evidence inventory: the operator-provided directory ../WORK/roulages/peaklive data contains four ASC/event-sidecar pairs dated 2026-09-16. Locate candidates by timestamp prefix to avoid embedding source-specific names: 10-24-19 has a 12,596,471-byte .asc.partial and .peaklive-events.jsonl.partial with 11 events (connected and 10 error_frame, no disconnected); 10-31-03 has a 5,395,683-byte ASC and 30 events (connected, one error_frame, 27 driver_overrun, disconnected). The connected-to-disconnected interval of the latter is 2202.833 seconds; it is session duration, not measured stop latency. The 10-29-12 and 10-30-28 pairs provide shorter comparison captures. No stop-click timestamp or Follow live state is present in these sidecars; none is yet confirmed as the reported freeze.

# Acceptance criteria
- AC1: Record a reproducible before/after stop investigation comparing Follow live off, full-span and trailing-window modes, with timings and stack evidence identifying the cause or explicitly documenting remaining reproduction limits.
- AC2: Stop immediately transitions to Stopping with feedback within 200 ms. The operation either completes in less than 3 seconds or presents a saving/finalization popup or progress bar by 3 seconds and keeps it visible until success or an explicit timeout/error. The GUI continues processing input and paint events throughout drain/finalization, including delayed or stuck workers; on a documented stress fixture a 50 ms GUI heartbeat has no gap above 250 ms. Record machine, load, click-to-feedback, total shutdown duration and progress visibility separately. A frozen popup or more than 30 seconds of unexplained unresponsiveness fails acceptance.
- AC3: Repeated start/stop, empty acquisition, populated multi-lane acquisition, recording on/off, delayed history writes and shutdown timeout preserve accepted data, recording finalization, stale-generation rejection and safe restart gating. After a successful stop the final samples remain navigable, with a stable viewport and no continuing live-update loop.
- AC4: Every measurement-table Signal cell shows Message.Signal without a DBC hash or arbitration-ID suffix; A/B, delta and statistics remain correct, and duplicate human-readable names retain distinct internal keys and inspectable provenance.
- AC5: No visible Measurement profile row or empty reserved strip remains. Existing profile/configuration and other unique commands remain accessible from the top menus/header, and one bus status indicator lives in the shared Graphs/Trace/Report header, synchronized through idle, starting, running, stopping, stopped, timeout and error states.
- AC6: The shared header uses the documented order: view selector; Play, Stop, bus status; Follow live, Fit XY, Fit Y; cursor A, cursor B, measurement visibility and A/B/delta readout. Groups are visually separated on a single line, with stable order after resize and view changes.
- AC7: Play, Stop, Follow live, A/B and both Fits stay directly accessible on the same header line at supported 1024x768, 1280x720 and 1600x900 windows. A common 28 logical-pixel button box and 16 logical-pixel icon canvas is the starting contract; any adjustment must be shared and documented with visual evidence. Icons are centered, crisp at 100/150/200 percent scaling, with distinct Play/Follow and Fit XY/Fit Y meanings, consistent strokes and clear checked/disabled/hover/focus states.
- AC8: Focused regression tests and visual review cover responsiveness, name collisions, bus state, removed-row geometry, header order, overflow restoration, shortcuts, localized tooltips and accessible names; existing full CI checks pass or pre-existing limitations are explicitly recorded.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_030_peaklive_responsive_stop_and_readable_measurement_controls`
- Architecture decision(s): (none yet)

# References
- src/peaklive/ui/session_controller.py
- src/peaklive/ui/live_handoff.py
- src/peaklive/ui/ingest_controller.py
- src/peaklive/services/worker.py
- src/peaklive/ui/gui_gc.py
- src/peaklive/ui/panels/graph_stack.py
- src/peaklive/ui/panels/graph_navigation.py
- src/peaklive/ui/panels/measurement.py
- src/peaklive/analysis/dbc.py
- src/peaklive/ui/panels/acquisition_bar.py
- src/peaklive/ui/workspace_center.py
- src/peaklive/ui/panels/workspace_header.py
- src/peaklive/ui/panels/graph_controls.py
- src/peaklive/ui/main_window.py
- src/peaklive/ui/actions.py
- src/peaklive/ui/theme.py
- tests/test_ui_lifecycle.py
- tests/test_graph_navigation.py
- tests/test_ui_workspace_refinement.py
- logics/tasks/task_029_deliver_peaklive_operator_menu_catalog_and_graph_canvas_refinement.md
- logics/tasks/task_030_eliminate_the_qt_python_garbage_collection_lock_inversion.md

# Backlog
- `item_139_diagnose_and_repair_acquisition_stop_stalls_with_follow_live`
- `item_140_use_clean_signal_display_titles_in_the_a_b_measurement_table`
- `item_141_remove_the_redundant_profile_row_and_relocate_bus_state_to_the_workspace_header`
- `item_142_unify_graph_header_action_order_and_icon_proportions`
