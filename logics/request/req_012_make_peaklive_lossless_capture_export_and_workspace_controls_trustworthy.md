## req_012_make_peaklive_lossless_capture_export_and_workspace_controls_trustworthy - Make PeakLive lossless capture export and workspace controls trustworthy
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Lossless capture export and reachable workspace controls
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-02 15:06:27

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: peaklive, lossless, capture, export, workspace, controls, trustworthy
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Needs
- Let an operator save a completed acquisition as an interoperable raw CAN capture in ASC or PCAN-View text TRC, with an explicit integrity statement that distinguishes every acquired frame from bounded, decoded signal export.
- Keep CSV and Parquet available for decoded signal analysis, but make their full retained buffer scope unambiguous: it is not a raw-frame capture guarantee.
- Remove visually animated deployment of the measurement-profile, channel, bitrate, and other application-owned selection menus.
- Make the workspace mode selector large enough to show its complete labels and reachable in every workspace mode, including Trace-only, so no analyst is trapped in a mode.
- Audit and correct undersized menu and button controls across supported workspace modes and desktop viewports, without clipping their user-visible text.

# Context
- The existing ExportDialog offers only CSV and Parquet from SeriesStore. Its all scope enumerates retained decoded samples, while SeriesStore and the displayed trace are bounded projections; it does not represent every raw adapter-delivered CAN frame.
- The acquisition path already passes each adapter-delivered frame through AcquisitionSession before presentation filtering. When profile recording is enabled, AscRecorder writes those frames to ASC, but that contract is not exposed as a clear post-acquisition ASC/TRC save choice and it has no TRC writer.
- A capture that was not recorded from acquisition start cannot honestly be reconstructed later from a bounded trace or retained-signal buffer. The UI must make this limitation and the capture completeness state explicit.
- GraphControlsBar fixes workspaceModeSelector to 76 px despite translated mode labels such as Graph only and Trace only. The selector is a child of GraphStackPanel, and MainWindow hides that panel in Trace-only and Report-only modes, leaving no visible way to select another mode.
- AcquisitionBar owns the profile, channel, bitrate, and controller-mode QComboBox controls. The shared dark theme styles combo popup views but does not define a no-animation interaction policy. Other workspace controls have deliberately compact geometry that needs systematic verification rather than isolated fixes.
- PeakLive is a native PySide6 desktop CAN-analysis application. The change must preserve receive-only acquisition, existing profile persistence, raw-recording integrity protections, decoded CSV/Parquet export, graph navigation, Trace and Report workflows, i18n, keyboard operation, and headless offscreen testability.
- The worktree contains unrelated replay edits and externally supplied artefacts. Delivery must leave them untouched and scope implementation to the new capture/export and control-accessibility work.

# Acceptance criteria
- AC1: The save/export workflow clearly separates decoded CSV/Parquet signal export from raw acquisition capture export. Full retained buffer is labelled as the entire retained decoded-signal range, never as a complete raw-frame capture.
- AC2: Before an acquisition starts, an operator can choose an interoperable raw capture format of ASC or PCAN-View text TRC. The selected writer receives every adapter-delivered CAN frame before UI filtering, display bounds, trace filtering, or decoded-series retention can discard presentation data.
- AC3: A clean acquisition produces a valid ASC or TRC artifact containing every acquired frame in source order with timestamp, channel, arbitration ID, frame kind, DLC, payload, and supported direction semantics. Deterministic fixtures prove exact frame count and content for both formats, including extended, remote, and error/event handling where format support permits it.
- AC4: Rotation, cancellation, recorder queue/worker failure, disk failure, and unclean stop cannot label an incomplete capture as complete. The UI reports capture state and artifact location without pretending a later bounded export can restore omitted raw frames.
- AC5: Existing decoded CSV and Parquet export scopes remain available and correct. Their labels, help, and completion feedback explain the selected signal/range semantics and distinguish them from raw capture export.
- AC6: Profile, channel, bitrate, controller-mode, export, and workspace selection popups open and close without application-configured reveal, fade, slide, or deployment animation, while remaining keyboard and screen-reader operable.
- AC7: At 1024x768, 1280x720, and 1600x900, every workspace-mode label is fully visible in its selector. A persistent or otherwise always-reachable mode control remains available in Combo, Graph-only, Trace-only, and Report-only states and can move directly between every state without resetting session data or layout unexpectedly.
- AC8: A focused audit of visible application buttons, menu entries, combo boxes, and control labels across all workspace modes and benchmark viewports finds no clipped, overlapped, or text-smaller-than-control regression. Where compact icon-only controls are retained, they have a meaningful accessible name and tooltip.
- AC9: Headless regression tests cover the capture/export distinction, complete ASC/TRC writer contract and incomplete-capture signalling, popup interaction policy, all-mode reachability, text containment, accessibility, persisted layout, and preservation of acquisition, trace, graph, report, and existing export behaviour.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_012_peaklive_trustworthy_raw_captures_and_universally_reachable_workspace_controls`
- Architecture decision(s): (none yet)

# References
- src/peaklive/ui/dialogs/export.py
- src/peaklive/analysis/export.py
- src/peaklive/services/export_worker.py
- src/peaklive/services/worker.py
- src/peaklive/services/acquisition.py
- src/peaklive/recording/asc.py
- src/peaklive/ui/panels/acquisition_bar.py
- src/peaklive/ui/panels/graph_controls.py
- src/peaklive/ui/workspace_center.py
- src/peaklive/ui/main_window.py
- src/peaklive/ui/theme.py
- tests/test_ui_analyst.py
- tests/test_ui_workspace_refinement.py
- tests/test_ui_parity.py

# Backlog
- `item_046_deliver_explicit_lossless_asc_and_trc_acquisition_capture_export`
- `item_047_make_every_workspace_selector_and_visible_control_legible_stable_and_reachable`
