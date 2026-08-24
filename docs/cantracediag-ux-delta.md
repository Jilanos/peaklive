# CanTraceDiag to PeakLive UX Delta

This document records the implementation map for the CanTraceDiag-grade UX wave.
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

## Validation boundary

Automated tests cover this UX delivery with fake adapters and DBC fixtures. Any
optional live PCAN smoke check for this request must be capped at 2 minutes or
less. No acceptance criterion in this UX wave requires longer connected-bus
time.
