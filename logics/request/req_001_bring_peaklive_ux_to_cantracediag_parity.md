## req_001_bring_peaklive_ux_to_cantracediag_parity - Bring PeakLive UX to CanTraceDiag parity
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 95%
> Confidence: 90%
> Complexity: High
> Theme: Desktop diagnostic UX parity
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-08-24 14:43:18

# AI Context
- Summary: Defines the PeakLive desktop UX parity push that translates CanTraceDiag's proven multi-DBC, signal, plot, trace, inspector, and instrument-style workflows into Qt.
- Keywords: bring, peaklive, cantracediag, parity
- Use when: Planning or implementing the next PeakLive UI/UX wave for DBC library management, acquisition setup, signal navigation, multi-graph measurements, collapsible panels, or CanTraceDiag-aligned visual polish.
- Skip when: Working only on low-level CAN driver behavior, recording integrity, installer packaging, or long hardware qualification unrelated to the desktop UX parity delta.

# Needs
- Close the practical UX gap between PeakLive and the validated CanTraceDiag diagnostic workspace before the next hands-on evaluation.
- Make multi-DBC loading, local DBC library management, DBC selection, removal, and conflict resolution usable from the desktop UI.
- Expose acquisition options clearly, including bitrate, application receive-only operation, passive listen-only, and normal receive with controller acknowledgement.
- Bring the signal explorer, graphing, trace, inspector, and layout controls to the dense instrument-style workflow operators already know from CanTraceDiag.
- Keep validation practical: no live CAN bus test in this request may require more than 2 minutes of connected bus time.

# Context
- The operator tested PeakLive live with a connected PCAN-USB and reported that core acquisition works.
- The operator supplied the sibling CanTraceDiag checkout as the UX and visual reference for DBC library, signal explorer, plots, trace, inspector, and instrument styling.
- CanTraceDiag's reference UI uses an instrument-style dark theme, compact panel chrome, DBC-grouped signal navigation, favorites, displayed-only filtering, stacked plots, A/B cursors, and collapsible workspace regions.
- PeakLive is a native PySide6 desktop application, not a browser PWA, so implementation should translate the interaction model into Qt widgets and existing domain services rather than copying web code.
- The current PeakLive UI has a basic DBC file picker, flat signal list, one plot preview, one trace table, and an inspector label; this request should first capture a concrete delta map before changing behavior.
- DBC files may be UTF-8, UTF-8 with BOM, CP-1252, or Latin-1 and may contain units such as the degree symbol.
- The MVP remains application-level receive-only. Normal receive may acknowledge valid frames at controller level, while passive listen-only must never acknowledge traffic.
- Live bus validation remains bounded: use fake/replay fixtures for broad coverage and at most 2 minutes of real PCAN bus time for hardware smoke evidence.

# Acceptance criteria
- AC1: A checked-in delta analysis maps CanTraceDiag UX patterns to current PeakLive gaps, Qt implementation targets, and test evidence for DBC loading, acquisition setup, signal explorer, plots, trace, inspector, layout, and visual style.
- AC2: PeakLive lets operators load multiple DBCs in one action, keeps a local in-memory DBC library for the session/profile, shows each DBC as selectable state, supports add/remove/disable flows, and provides deterministic conflict resolution for non-equivalent arbitration IDs.
- AC3: Acquisition setup exposes supported bitrate choices, channel selection, application receive-only status, passive listen-only, and normal receive with controller acknowledgement semantics without exposing any transmit action.
- AC4: The signal panel matches the CanTraceDiag workflow in desktop form: DBC-origin grouping, message-level grouping where useful, dropdown/search navigation for dense catalogs, favorites, shown/displayed filtering, and clickable signal rows that add or remove plots.
- AC5: The workspace supports multiple simultaneous graphs, A/B cursors with delta readouts, graph/trace combo views, and user-selectable visible panels for graphs, trace, inspector, and signals.
- AC6: The signal, inspector, graph, and trace panels are independently collapsible without losing selected signals, DBC state, acquisition state, or profile persistence.
- AC7: PeakLive adopts a more finished CanTraceDiag-aligned instrument visual style using consistent tokens, dense data typography, compact controls, status semantics, and polished empty/error/loading states.
- AC8: Automated coverage validates multi-DBC workflows, conflict handling, acquisition option state, signal filtering/grouping, multi-graph/cursor behavior, panel collapse/persistence, and style-critical UI smoke paths without requiring live hardware.
- AC9: Any live CAN validation for this request is optional hardware smoke evidence and must be capped at 2 minutes or less; no acceptance gate may require a longer connected-bus run.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_002_peaklive_cantracediag_grade_diagnostic_workspace`
- Architecture decision(s): (none yet)

# References
- README.md
- docs/product-scope.md
- docs/architecture.md
- docs/windows-hardware-acceptance.md
- src/peaklive/ui/main_window.py
- src/peaklive/analysis/dbc.py
- src/peaklive/services/profiles.py
- tests/test_ui.py
- tests/test_dbc.py
- tests/test_pcan_adapter.py

# Backlog
- `item_009_analyze_the_cantracediag_to_peaklive_ux_delta`
- `item_010_deliver_multi_dbc_library_and_conflict_management`
- `item_011_upgrade_acquisition_setup_controls`
- `item_012_bring_the_signal_explorer_to_cantracediag_parity`
- `item_013_deliver_multi_graph_measurements_and_configurable_workspace_panels`
- `item_014_apply_the_cantracediag_instrument_visual_system_to_peaklive`
- `item_015_validate_the_ux_parity_delivery_with_bounded_hardware_evidence`
