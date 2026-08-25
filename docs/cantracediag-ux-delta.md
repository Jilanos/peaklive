# CanTraceDiag to PeakLive UX Delta

## Wave 1 - workspace parity (req_001, delivered)

This section records the implementation map for the first CanTraceDiag-grade UX wave.
It translates the browser reference patterns into native Qt behavior without
adding any transmit workflow to PeakLive.

| Area | CanTraceDiag reference pattern | Previous PeakLive gap | Qt target delivered | Evidence |
| --- | --- | --- | --- | --- |
| DBC loading | Operators can work from a DBC library instead of a single file action. | One file picker loaded one DBC and hid session state. | `Load DBC` accepts multiple files; loaded DBCs appear in the DBC library with enabled/disabled state and remove support. | `tests/test_ui.py::test_main_window_manages_multi_dbc_signals_favorites_and_graphs` |
| DBC conflicts | Dense diagnostic workflows make ambiguity explicit. | Non-equivalent frame-ID collisions surfaced only while decoding. | The DBC library exposes conflict choices by arbitration ID and persists deterministic resolution by DBC hash. | `tests/test_dbc.py::test_catalog_requires_explicit_resolution_for_non_equivalent_messages` |
| DBC state | Reference workspace keeps DBC origin visible while navigating signals. | Signals were flattened into `Message.Signal`. | Signal explorer groups by source DBC and message, retaining DBC hash in the tree. | `tests/test_dbc.py::test_catalog_lists_signals_by_dbc_and_ignores_disabled_conflicts` |
| Acquisition setup | Operator sees bitrate and controller mode before connecting. | Bitrate/mode were profile text only. | The top bar exposes channel, supported bitrates, passive listen-only, normal receive with controller ACK, and explicit app read-only status. | `tests/test_ui.py::test_main_window_persists_acquisition_mode_and_collapsible_panels` |
| Signal navigation | Reference signal explorer supports dense filtering, favorites, and displayed-only views. | Signal list had no grouping, no search, no favorite state, and only one selected signal. | Qt tree adds search, shown-only, favorites-only, per-signal shown checkbox, and per-signal favorite checkbox. | `tests/test_ui.py::test_main_window_manages_multi_dbc_signals_favorites_and_graphs` |
| Graphs | Reference plots can show several selected signals and cursor readouts. | PeakLive had one preview plot. | Graph stack renders one plot per shown signal, keeps the raw-byte preview when no DBC signal is shown, and adds A/B movable cursors with delta readouts. | `tests/test_ui.py::test_main_window_manages_multi_dbc_signals_favorites_and_graphs` |
| Workspace layout | Reference workspace lets operators collapse regions and choose graph/trace combinations. | PeakLive panels were fixed. | Signals, graph/trace, and inspector panels are independently collapsible; graph/trace modes support combo, graphs-only, and trace-only. | `tests/test_ui.py::test_main_window_persists_acquisition_mode_and_collapsible_panels` |
| Visual style | Reference uses compact dark instrument panels, data typography, and status semantics. | PeakLive had only the initial MVP style pass. | The Qt stylesheet now uses darker instrument tokens, amber headings, status pills, denser controls, and polished grouped panels. | `QT_QPA_PLATFORM=offscreen uv run python -m pytest tests/test_ui.py` |

### Validation boundary

Automated tests cover this UX delivery with fake adapters and DBC fixtures. Any
optional live PCAN smoke check for this request must be capped at 2 minutes or
less. No acceptance criterion in this UX wave requires longer connected-bus
time.


## Wave 2 - analyst workspace (req_002, delivered)

A follow-up diagnostic against the sibling checkout found the remaining delta
concentrated below the signal explorer: measurement, trace inspection, export,
reporting, operator feedback, and keyboard operation.

| Area | CanTraceDiag reference pattern | Wave 1 gap | Qt target delivered | Evidence |
| --- | --- | --- | --- | --- |
| Frame inspection | The inspector describes the frame the operator selected. | The inspector was a `QLabel` written from inside the frame-render loop; no trace selection handler existed at all. | Selecting a trace row drives the inspector: identity, hex and per-byte payload, resolved message, decode status, and every decoded signal. Events render as events. | `tests/test_ui_analyst.py::test_inspector_describes_the_selected_frame` |
| Cursor stability | Placed cursors survive incoming data. | Every batch re-pinned cursor A to the first sample and cursor B to the last, so a live measurement collapsed onto the newest data. | Cursor positions live in `GraphStackPanel`, are seeded once, persisted per profile, and never moved by ingestion. | `tests/test_ui_analyst.py::test_cursors_keep_their_position_across_incoming_batches` |
| Time navigation | Zoom, pan, fit, grid, and a window/zoom readout on a shared axis. | pyqtgraph defaults only; no controls, no shared axis, no readout. | Zoom in/out, fit, grid, follow-live, a linked X axis across the stack, and a `start – end (N×)` readout. | `tests/test_ui_analyst.py::test_graph_navigation_controls_change_the_window_and_report_the_zoom` |
| Range measurement | Cursor values plus n/min/max/mean/std/rms and enum distributions. | The readout showed timestamps and a time delta only; no statistic existed anywhere in the codebase. | `analysis/statistics.py` plus a measurement table per shown signal, with distributions for textual signals. | `tests/test_statistics.py`, `tests/test_ui_analyst.py::test_measurement_table_reports_cursor_values_and_range_statistics` |
| Trace filtering | ID/message/signal/direction/event/status/time filters with removable chips. | No trace filter control existed, although display-only filtering was a stated MVP capability. | A filter bar with progressive disclosure, removable chips, clear-all, and profile persistence; filtering is display-only. | `tests/test_trace_buffer.py`, `tests/test_ui_analyst.py::test_each_trace_filter_narrows_the_display_only` |
| Trace columns | Configurable visibility, order, width, and value format. | Six hard-coded columns. | A columns dialog over per-profile `TraceColumn` settings with time/hex/dec/bin/status formats. | `tests/test_ui_analyst.py::test_column_visibility_order_width_and_format_take_effect` |
| Trace retention | Bounded paging over a large trace. | A 5000-row cap enforced by `removeRow(0)` per aged-out row, which is quadratic. | A `deque(maxlen=...)` buffer plus incremental append and a single-pass head trim; `removeRow` is never called. | `tests/test_ui_analyst.py::test_sustained_ingestion_stays_bounded_without_per_row_removal` |
| Export | Streamed CSV/Parquet over a chosen range. | `export_csv`/`export_parquet` existed with no caller in the UI. | An export dialog with A–B, visible-window, and full-buffer scopes, streamed through `heapq.merge`, progress-reporting, cancellable, and self-cleaning on failure. | `tests/test_ui_analyst.py::test_export_writes_exactly_the_rows_in_each_scope` |
| Reporting | An import synthesis with anomalies by type. | No session synthesis existed. | `analysis/session.py` collects bounded facts; a report view shows volumes, coverage, DBCs, top IDs, and anomalies, and exports verbatim. | `tests/test_session_report.py`, `tests/test_ui_analyst.py::test_report_summarizes_volumes_dbcs_coverage_and_anomalies` |
| Operator feedback | Status LED and explicit empty/error/loading states. | A controller-mode pill; DBC conflicts appeared as a transient status-bar message. | A bus-state LED across seven states, persistent panel-local `StateNote`s, replay/DBC progress, and visible recording disk warnings. | `tests/test_ui_analyst.py::test_bus_state_follows_the_acquisition_lifecycle`, `::test_a_dbc_load_failure_stays_visible_in_the_library_panel` |
| Keyboard and layout | Keyboard-operable controls, verified viewports. | Zero `QShortcut`, zero tooltip, hard-coded splitter sizes, no menu bar. | File/View/Help menus, shortcuts for lifecycle/cursors/fit/filter/fullscreen, tooltips and accessible names on every control, persisted geometry, and 1024×768 / 1280×720 / 1600×900 coverage. | `tests/test_ui_analyst.py::test_the_menu_bar_exposes_the_workspace_actions`, `::test_the_layout_stays_usable_at_the_bench_viewports` |
| UI structure | A front end split by concern. | One 863-line `main_window.py` holding every panel and the stylesheet. | Seventeen focused modules under a 400-line budget, with the shell reduced to composition and every label routed through i18n. | `tests/test_ui_structure.py` |

### Defects the regression suite surfaced

Two latent defects were found by writing the wave-1 parity suite before
touching the code, and are fixed here:

- toggling a DBC checkbox rebuilt the tree from inside its own `itemChanged`
  emission, deleting the item Qt still held — a reproducible segmentation
  fault. Enable and disable now update the affected row in place;
- a malformed DBC raised `cantools`' `UnsupportedDatabaseFormatError`, which
  escaped the `(OSError, ValueError)` boundary the UI catches. `DbcCatalog.load`
  now re-raises it as `ValueError`.

The `warn_free_bytes` recording threshold was also present in the domain model
but never read; it now produces one operator-visible notice per recording.

### Validation boundary

The wave-2 suite runs headless under `QT_QPA_PLATFORM=offscreen` with fake
adapters, DBC fixtures, and synthetic sessions. No acceptance gate depends on
connected hardware; any live PCAN smoke check remains optional and capped at
2 minutes.
