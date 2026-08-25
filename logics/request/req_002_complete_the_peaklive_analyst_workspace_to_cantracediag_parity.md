## req_002_complete_the_peaklive_analyst_workspace_to_cantracediag_parity - Complete the PeakLive analyst workspace to CanTraceDiag parity
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Desktop diagnostic analyst workspace
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-08-25 11:35:46

# AI Context
- Summary: Defines the second PeakLive parity wave, which turns the delivered DBC/signal/plot workspace into an analyst tool: selection-driven frame inspection, cursors that hold their position, range statistics, display-only trace filtering, configurable trace columns, reachable CSV/Parquet export, a session diagnostic report, explicit bus and error states, keyboard operation, and the decomposition of the monolithic main window.
- Keywords: inspector, cursors, range statistics, trace filters, trace columns, export scope, diagnostic report, bus state, keyboard accessibility, ui decomposition
- Use when: Implementing or reviewing any PeakLive workspace behavior below the signal explorer - frame inspection, cursor measurement, range statistics, trace filtering or columns, export, reporting, operator feedback states, shortcuts and layout persistence, or the split of src/peaklive/ui/main_window.py.
- Skip when: Working on the already delivered req_001 surface (multi-DBC library, conflict resolution, signal explorer grouping, stacked plot creation, instrument stylesheet tokens), on CAN driver or adapter behavior, on recorder integrity, on installer packaging, or on anything that would introduce a transmit path.

# Needs
- Close the analyst-facing gap that remains after the first CanTraceDiag parity wave, which delivered the DBC library, signal explorer, stacked graphs, and instrument styling but left measurement, trace inspection, export, and reporting behind.
- Make the frame inspector usable: it must describe the frame the operator selected in the trace, not the last decoded signal that happened to stream past.
- Let operators keep an A/B measurement in place during live acquisition and read real signal statistics from it, not only a time delta.
- Give the trace view the display-only filtering and configurable columns the product scope already promises, with bounded memory and no quadratic row churn.
- Make the already implemented CSV/Parquet export and a session diagnostic report reachable from the workspace instead of only from library code.
- Make bus state, decode conflicts, recording warnings, and loading progress visible where the operator is looking, instead of in a transient status-bar message.
- Make the workspace operable from the keyboard and stable across bench screen sizes, and split the monolithic main window so further UX work stops compounding in one file.
- Keep validation practical: no live CAN bus test in this request may require more than 2 minutes of connected bus time.

# Context
- The first parity request (req_001) is closed and delivered the multi-DBC library with conflict resolution, the grouped signal explorer with search and favorites, stacked per-signal plots with A/B cursors, collapsible panels, and the darker instrument stylesheet. docs/cantracediag-ux-delta.md records that map.
- A follow-up diagnostic against the sibling CanTraceDiag checkout found the remaining delta concentrated in measurement, trace inspection, export, reporting, feedback states, and accessibility.
- src/peaklive/ui/main_window.py is a single 863-line module holding the top bar, DBC library, signal explorer, graph stack, trace table, inspector, and the inline stylesheet; every remaining gap lands in that one file.
- The inspector is a QLabel written from inside the frame-render loop. There is no trace selection handler at all, so selecting a trace row does nothing.
- The graph refresh path re-pins cursor A to the first sample and cursor B to the last sample on every incoming batch, so a placed measurement cannot survive live acquisition.
- The cursor readout reports timestamps and a time delta only. No signal value, count, min, max, mean, standard deviation, RMS, or enum distribution is computed anywhere in the application.
- The trace table has six hard-coded columns, no filter controls, and caps itself at 5000 rows by removing the first row repeatedly, which is quadratic under load. profile.trace_filters currently stores only the workspace mode and DBC state.
- peaklive.analysis.export exposes export_csv and export_parquet with a batched Parquet writer, but no UI code path calls either function.
- There is no session report, no bus-state indicator beyond the controller-mode pill, no progress or cancel affordance for DBC loading and replay, and no persisted splitter geometry.
- The module contains no QShortcut, no QKeySequence, and no tooltip; recent controls carry English string literals rather than i18n keys, and i18n.py loads only en.json.
- CanTraceDiag validates its layout at 1024x768, 1280x720, and 1600x900; PeakLive sets no minimum window size and has no layout verification.
- PeakLive stays application-level receive-only. This request introduces no transmit path, no cyclic transmit, and no diagnostic protocol.
- PeakLive is a native PySide6 application. CanTraceDiag behaviors must be translated into Qt widgets and existing domain services, never ported as web code.
- Live bus validation remains bounded: fake adapters and replay fixtures carry broad coverage, and at most 2 minutes of real PCAN bus time may be used for hardware smoke evidence.

# Acceptance criteria
- AC1: Selecting a row in the trace view drives the inspector, which shows the frame identity (timestamp, arbitration ID with extended flag, DLC, channel, direction), the raw payload in hexadecimal and per-byte form, the resolved message name with its source DBC, the decode status, and every decoded physical signal with raw value, physical value, and unit; the same behavior holds during live acquisition and replay.
- AC2: A/B cursors keep the position the operator gave them across incoming data batches, profile reloads, and view switches, and the graph stack offers zoom, pan, fit-to-extent, and grid toggling on a shared time axis with a visible time window and zoom-factor readout.
- AC3: A measurement table under the graph stack lists, per shown signal, the values at cursor A and cursor B, their delta, and the A-B range statistics (sample count, min, max, mean, standard deviation, RMS) for numeric signals, and a value distribution for enumerated or textual signals; the table states explicitly when both cursors are not yet placed.
- AC4: The trace view offers display-only filtering by arbitration ID, message name, signal name, direction, event kind, decode status, and time range, plus frames-only and events-only toggles; active filters are shown as individually removable chips with a clear-all action, secondary filters are progressively disclosed, filtering never alters recorded data, and the filter set persists in the measurement profile.
- AC5: Trace columns are configurable for visibility, order, width, and value format (time, hexadecimal, decimal, binary, status), the configuration persists per profile, and the trace view stays bounded in memory under sustained load without per-row quadratic pruning.
- AC6: Operators can export selected decoded signals to CSV or Parquet from the workspace, choosing the range between cursors A and B, the visible time window, or the full retained buffer; the export streams with bounded memory, reports progress, can be cancelled, and reports written row counts and failures inline.
- AC7: A session diagnostic report view summarizes the acquisition or replay: time range, frame and event volumes, frames per second, loaded DBCs with signal counts and enabled state, decode coverage, and anomalies grouped by type (unknown arbitration IDs, DBC conflicts, malformed records, bus errors, recording warnings); the report can be refreshed and exported to a local file.
- AC8: A bus-state indicator shows connection state (idle, connecting, running, reconnecting, bus error, bus-off, stopped) with a text label next to it, and every failure or waiting condition has an explicit panel-local state: empty trace, filtered-to-empty trace, DBC parse or conflict error, plot without data, export failure, recording disk warning, and a progress indicator with cancellation for DBC loading and replay import.
- AC9: The workspace is fully operable from the keyboard: shortcuts cover start and stop acquisition, view switching, panel collapse, cursor A and B placement, fit view, filter focus, and fullscreen; every actionable control carries a tooltip and an accessible name; tab order reaches the DBC library, signal explorer, filter fields, trace rows, measurement table, and every dialog.
- AC10: The workspace exposes a menu bar (File, View, Help) covering the actions previously available only as top-bar buttons plus an About entry, a fullscreen mode, a resizable divider between the graph stack and the trace view, and splitter geometry and collapse state persisted per profile; the layout stays usable at 1024x768, 1280x720, and 1600x900 with a declared minimum window size.
- AC11: src/peaklive/ui/main_window.py is decomposed into focused UI modules (at minimum acquisition bar, DBC library, signal explorer, graph stack, trace view, inspector, report, and stylesheet tokens) with the main window reduced to composition and wiring, no behavior regression against the delivered req_001 parity map, and every user-visible string routed through the i18n layer.
- AC12: Automated coverage runs headless under QT_QPA_PLATFORM=offscreen and validates inspector selection, cursor persistence, range statistics, trace filtering and chips, column configuration and bounded pruning, export scopes and cancellation, report contents, bus-state and error states, keyboard shortcuts and tab order, and layout persistence; no acceptance gate depends on connected hardware, and any live PCAN smoke evidence is optional and capped at 2 minutes.
- AC13: No transmit, cyclic transmit, or diagnostic-protocol capability is introduced, and passive listen-only still never acknowledges traffic.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_003_peaklive_analyst_measurement_and_reporting_workspace`
- Architecture decision(s): (none yet)

# References
- README.md
- docs/product-scope.md
- docs/architecture.md
- docs/cantracediag-ux-delta.md
- docs/windows-hardware-acceptance.md
- src/peaklive/ui/main_window.py
- src/peaklive/analysis/export.py
- src/peaklive/analysis/dbc.py
- src/peaklive/analysis/replay.py
- src/peaklive/domain/models.py
- src/peaklive/services/profiles.py
- src/peaklive/services/replay_worker.py
- src/peaklive/i18n.py
- tests/test_ui.py
- tests/test_export.py
- tests/test_replay.py

# Backlog
- `item_016_make_the_frame_inspector_selection_driven`
- `item_017_stabilize_a_b_cursors_and_add_graph_time_navigation`
- `item_018_deliver_the_range_measurement_table`
- `item_019_deliver_display_only_trace_filtering_with_active_filter_chips`
- `item_020_deliver_configurable_bounded_trace_columns_and_paging`
- `item_021_expose_streamed_csv_and_parquet_export_from_the_workspace`
- `item_022_deliver_the_session_diagnostic_report`
- `item_023_deliver_bus_state_error_and_loading_feedback`
- `item_024_deliver_keyboard_accessibility_menus_and_layout_persistence`
- `item_025_decompose_the_workspace_ui_into_modules_with_parity_regression_coverage`
