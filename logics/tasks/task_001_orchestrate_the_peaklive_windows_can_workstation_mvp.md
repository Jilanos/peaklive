## task_001_orchestrate_the_peaklive_windows_can_workstation_mvp - Orchestrate the PeakLive Windows CAN workstation MVP
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Indicators reviewed: 2026-08-24 12:28:10
> Owner: Codex

# AI Context
- Summary: Sequences the eight PeakLive MVP delivery slices so recording integrity and adapter contracts precede dependent UI, analysis, and packaging work.
- Keywords: orchestrate, peaklive, windows, can, workstation, mvp
- Use when: Coordinating or implementing the end-to-end MVP and deciding which ready backlog slice should execute next.
- Skip when: Implementing an unrelated companion-reader feature or a capability explicitly deferred beyond the MVP.

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Establish the application foundation, domain contracts, fake adapter, test harness, and visual shell.
- [x] 2. Integrate the first Classic USB adapter and validate explicit receive/passive semantics and recovery states.
- [x] 3. Build and benchmark the recording pipeline before connecting presentation filters.
- [x] 4. Deliver the batched live trace and deterministic multi-DBC decode path.
- [x] 5. Add bounded plots and cursor measurements against the measured live pipeline.
- [x] 6. Implement incremental ASC/TRC replay and streamed decoded exports.
- [x] 7. Package the Windows application and execute clean-machine and hardware acceptance evidence.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_001_establish_the_native_windows_application_foundation`
- `item_002_integrate_robust_classic_usb_can_acquisition`
- `item_003_build_the_complete_and_recoverable_recording_pipeline`
- `item_004_deliver_the_live_trace_and_display_only_filtering_workspace`
- `item_005_add_deterministic_multi_dbc_live_decoding`
- `item_006_render_bounded_real_time_signal_plots_and_measurements`
- `item_007_implement_incremental_asc_and_trc_replay_with_decoded_export`
- `item_008_package_and_qualify_the_windows_mvp`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC12 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC13 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC14 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC2 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC3 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC4 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC14 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC4 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC5 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC6 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC13 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC14 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC4 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC7 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC12 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC8 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC9 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC11 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC12 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC14 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC6 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC8 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC9 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC12 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC8 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC10 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC11 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC13 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC14 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC1 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC2 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC4 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC6 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC9 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC13 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`
- request-AC14 -> This task. Proof: Validated in working tree on 2026-08-24 with Linux and Windows pytest 26 passed, ruff check, i18n validate, Windows build script smoke/build evidence, PCAN passive 500 kbit/s hardware probes, corrected PCAN error-frame/overrun event handling, 60-second capture of 47,424 frames, and operator-approved deferral of the full 60-minute run. Source: `working-tree-2026-08-24`

# Validation
- (no validation recorded yet)
- QT_QPA_PLATFORM=offscreen uv run python -m pytest passed on 2026-08-24: 26 passed.
- uv run ruff check . passed on 2026-08-24: All checks passed.
- powershell.exe / uv run python -m pytest passed on 2026-08-24: 26 passed on Windows .venv-win.
- scripts/build-windows.ps1 passed on 2026-08-24 after native-step exit-code fix; dist/PeakLive.exe smoke-launched for 8 seconds; SHA256 7E8116755B640A613CE3BE00F8F0EF3F81BC59A37D2C39217B2DF1F43637E623.
- PCAN_USBBUS1 hardware evidence on 2026-08-24: 500 kbit/s passive probe valid, 60-second capture recorded 47,424 frames, wrong bitrate error frames normalize to events, interrupted long run deferred by operator decision.
- Finish workflow executed on 2026-08-24.
- Linked backlog/request close verification passed.

# Report
- Not started.
- Finished on 2026-08-24.
- Linked backlog item(s): `item_001_establish_the_native_windows_application_foundation`, `item_002_integrate_robust_classic_usb_can_acquisition`, `item_003_build_the_complete_and_recoverable_recording_pipeline`, `item_004_deliver_the_live_trace_and_display_only_filtering_workspace`, `item_005_add_deterministic_multi_dbc_live_decoding`, `item_006_render_bounded_real_time_signal_plots_and_measurements`, `item_007_implement_incremental_asc_and_trc_replay_with_decoded_export`, `item_008_package_and_qualify_the_windows_mvp`
- Related request(s): `req_000_deliver_the_peaklive_windows_can_workstation_mvp`

# Links
- Request: `req_000_deliver_the_peaklive_windows_can_workstation_mvp`
- Product brief(s): `prod_001_peaklive_windows_can_workstation`
- Architecture decision(s): (none yet)
