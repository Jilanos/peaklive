## task_029_deliver_peaklive_operator_menu_catalog_and_graph_canvas_refinement - Deliver PeakLive operator menu, catalog, and graph-canvas refinement
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 95%
> Confidence: 95%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: maintainer@example.invalid
> Indicators reviewed: 2026-09-14 16:30:50

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: deliver, peaklive, operator, menu, catalog, graph, canvas, refinement
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Deliver the confirmed Recording, Setup, and DBC menu-bar ownership wave, preserving Save measurement setup as the existing profile save-as behavior; include safe cascading setting menus, recording-format relocation, lifecycle synchronization, i18n, and regression coverage.
- [x] 2. Deliver the DBC menu and displayed-signal summary wave with at-most-once-per-second summary refreshes, while preserving asynchronous catalog ownership and source-of-truth value semantics.
- [x] 3. Deliver shared graph X-range clamping, View-selectable Follow live modes with Full acquisition span as default, fit-control regrouping, and measured gutter reduction without taking over active historical/workspace scope.
- [x] 4. Run focused and full headless suites, Windows offscreen UI coverage, Ruff, i18n validation, Logics validation, lint, and audit. Record each completed wave with the evidence actually run; this corpus creation does not start implementation.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_135_organize_recording_and_setup_commands_around_safe_profile_ownership`
- `item_136_move_dbc_management_to_its_own_menu_and_summarize_displayed_signals`
- `item_137_bound_graph_time_navigation_and_reclaim_safe_graph_canvas_width`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> This task. Proof: View now holds only navigation/panel-visibility commands; Recording owns Start/Stop/Recording settings; header lifecycle controls unchanged; Stop carries the `active` dynamic property styled red only in STOPPABLE_PHASES (`acquisition_bar.py::set_lifecycle_phase`, `theme.py`). Verified by `test_header_stop_is_red_only_while_stoppable`, `test_recording_and_setup_menus_own_the_relocated_commands`.
- request-AC2 -> This task. Proof: Recording and Setup are new menu-bar menus; Setup holds Save measurement setup (unchanged `_save_profile_as`) plus Channel/Bitrate/Controller-mode cascading submenus mirroring the AcquisitionBar combos via `_build_choice_submenu`, gated by lifecycle (`STARTABLE_PHASES`) and synced on every phase change. Verified by `test_setup_cascading_submenus_mirror_and_drive_the_acquisition_bar_combos`.
- request-AC3 -> This task. Proof: ASC/TRC selection moved from AcquisitionBar into `RecordingSettingsDialog.capture_format_selector`, writing `profile.recording.capture_format` directly; no top-bar capture-format control remains. Verified by `test_ui_parity.py::test_parity_acquisition_setup_persists_and_stays_receive_only`.
- request-AC4 -> This task. Proof: A top-level DBC menu (`menu_dbc`) lists every loaded definition as a checkable action plus Add/Remove/Conflicts entry points; `DbcLibraryPanel` and its Signals embedding are removed. Verified by `test_dbc_enablement_stays_in_the_dbc_menu_and_is_not_duplicated`, `test_parity_multi_dbc_menu_shows_state_and_supports_disable_and_remove`, `test_parity_dbc_conflicts_are_explicit_and_resolution_persists`.
- request-AC5 -> This task. Proof: `SignalSummaryPanel` leads Signals, showing every currently shown signal's latest value/unit via `SeriesStore`, refreshed at most once/second through `WorkspaceSignalSummary` (immediate first refresh, coalesced afterward), with unavailable values marked explicitly. Verified by `tests/test_signal_summary.py` (5 tests) including the coalescing test.
- request-AC6 -> This task. Proof: `_clamp_x_range`/`_clamp_manual_range` in `graph_navigation.py` bound every manual pan/zoom to the extent plus max(5% of span, 0.5s floor), applied via `_x_range_changed`; Fit/Follow-live already compute ranges from the extent so stay inherently within it. Verified by `test_manual_navigation_cannot_travel_far_past_either_data_edge`, `test_manual_navigation_within_bounds_is_left_untouched`.
- request-AC7 -> This task. Proof: Empty/one-sample extents clamp to a finite, non-degenerate window with no NaN and no recursive range signalling (`_applying_range` guard). Verified by `test_the_clamp_stays_finite_and_non_degenerate_for_a_single_sample`, `test_the_clamp_stays_finite_and_non_degenerate_for_an_empty_extent`.
- request-AC8 -> This task. Proof: View > Follow live offers Full acquisition span (default) and Trailing window via `GraphNavigation.set_follow_live_mode`, persisted on `MeasurementProfile.layout.follow_live_mode`; `SHARED_LEFT_AXIS_WIDTH` reduced 88px -> 64px. Existing Fit/Fit Y/Follow-live/cursor grouping already matched navigation intent (pre-existing `test_follow_live_shares_the_fit_commands_row`), so no control reorder was needed. Verified by `test_the_menu_bar_offers_full_and_trailing_follow_live_modes`, `test_choosing_trailing_mode_restores_the_pinned_narrow_window_on_follow`, `test_full_mode_shows_the_whole_extent_even_after_a_narrow_zoom`.
- request-AC9 -> This task. Proof: New/changed keys added to `src/peaklive/i18n/en.json` (the project's only locale file) for every relocated/added menu, DBC, and summary string; all touched controls keep accessible names/tooltips and keyboard activation (cascading submenus and DBC/Conflicts menus use standard `QAction`/`QActionGroup` keyboard navigation). Verified by the full pytest suite (no regressions) plus the i18n-key assertions already exercised by `test_ui_structure.py::test_every_translate_key_used_by_the_ui_resolves` and `test_the_catalog_covers_every_key_the_ui_asks_for`.

# Validation
- `uv run ruff check src/peaklive tests` passed on 2026-09-14: All checks passed!
- `QT_QPA_PLATFORM=offscreen uv run python -m pytest -ra -q -o faulthandler_timeout=120` passed on 2026-09-14: full suite green (same pre-existing Windows-offscreen xfail/xpass set as baseline; no regressions across all three waves).
- `logics-manager lint` passed on 2026-09-14: Logics lint: OK.
- `logics-manager audit` passed on 2026-09-14: Workflow audit: OK (warnings only, all pre-existing).
- pytest full suite + ruff + logics-manager lint/audit all passed on 2026-09-14
- Finish workflow executed on 2026-09-14.
- Linked backlog/request close verification passed.

# Report
- Delivered in three sequential waves (menu reorganization, DBC menu + signal summary, graph clamp/follow-live/gutter), each validated with focused and full headless test runs, ruff, and Logics lint/audit before moving on. Repo left commit-ready; commit creation left to the operator per the task's explicit instruction.
- Finished on 2026-09-14.
- Linked backlog item(s): `item_135_organize_recording_and_setup_commands_around_safe_profile_ownership`, `item_136_move_dbc_management_to_its_own_menu_and_summarize_displayed_signals`, `item_137_bound_graph_time_navigation_and_reclaim_safe_graph_canvas_width`
- Related request(s): `req_030_refine_peaklive_operator_menus_catalog_access_and_graph_navigation`

# Links
- Request: `req_030_refine_peaklive_operator_menus_catalog_access_and_graph_navigation`
- Product brief(s): `prod_028_peaklive_focused_operator_controls_and_bounded_measurement_canvas`
- Architecture decision(s): (none yet)
