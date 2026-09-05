## task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone - Deliver every September 2026 audit correction and future roadmap milestone
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: paul.mondou@circle-mobility.com
> Indicators reviewed: 2026-09-05 10:41:25

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: deliver, september, 2026, audit, correction, future, roadmap, milestone
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [x] 1. Wave 1 High: reproduce all P0 defects as failing Linux tests, land profile recovery, bounded reservation, post-connect cleanup, malformed replay handling, session isolation, error backoff/reconnect, export ownership, abandoned-worker cleanup, and durable profile writes.
- [x] 2. Wave 2 High: separate exhaustive data ingestion from visual coalescing; prove facts, caches, deferred decode, series, and reports against high-rate live and replay fixtures.
- [x] 3. Wave 3 Medium: deliver bounded input, decode, graph, export, trace, and architecture work, prioritizing responsiveness proofs before UI evolution.
- [x] 4. Wave 4 Medium: deliver the Fusion English visual system and diagnostic workflows, including aggregate IDs and always-gated acquisition controls.
- [x] 5. Wave 5 Low: deliver finish work, recents, graph linkage, counters, extension ports, and an honest staged roadmap for bitrate scan, discovery, BLF/MDF, adapters, and future CAN transmit.
- [x] 6. After every wave run focused tests; at closeout run the full Linux suite, Logics validation, lint, audit, and documentation consistency checks. Include the audit and supplied external evidence in the commit under operator control.
- [x] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [x] Keep commit creation under operator control; do not force one commit per micro-step.
- [x] GATE: do not close until lint, audit, and scaffold validation pass.

# Backlog
- `item_057_bound_recording_name_reservation_and_cancel_it_safely`
- `item_058_recover_safely_from_a_corrupt_profile_store`
- `item_059_separate_exhaustive_ingestion_from_visual_coalescing`
- `item_060_disconnect_the_adapter_after_a_post_connect_start_failure`
- `item_061_own_export_workers_independently_of_transient_dialogs`
- `item_062_rate_limit_adapter_error_events_and_rotate_event_only_recordings`
- `item_063_bound_malformed_replay_diagnostics_and_prevent_false_success`
- `item_064_enforce_mutually_exclusive_immutable_live_and_replay_sessions`
- `item_065_drain_abandoned_workers_safely_at_process_exit`
- `item_066_make_profile_writes_durable_and_multi_instance_safe`
- `item_067_debounce_filters_signal_search_and_profile_persistence`
- `item_068_make_manual_graph_zoom_disable_live_follow`
- `item_069_decimate_plots_and_bound_measurement_recomputation`
- `item_070_cache_dbc_decode_lookup_and_deduplicate_conflict_notices`
- `item_071_deliver_an_aggregate_identifier_diagnostics_view`
- `item_072_replace_the_trace_table_with_a_bounded_virtual_model`
- `item_073_synchronize_graph_panels_incrementally_and_destroy_removed_resources`
- `item_074_export_immutable_snapshots_with_efficient_row_serialization`
- `item_075_log_all_operational_failures_and_expose_driver_overruns`
- `item_076_enforce_class_surface_architecture_budgets`
- `item_077_introduce_profile_schema_migration_dispatch`
- `item_078_inject_a_recorder_factory_into_acquisition_workers`
- `item_079_add_complete_interactive_button_states`
- `item_080_set_fusion_and_an_application_wide_dark_palette`
- `item_081_render_graphs_with_antialiasing_and_palette_derived_axes`
- `item_082_standardize_table_chrome_and_data_typography`
- `item_083_create_semantic_control_variants_and_dominant_start_stop_actions`
- `item_084_tokenize_spacing_geometry_and_stable_focus`
- `item_085_add_trace_and_graph_context_commands_with_copy_support`
- `item_086_create_an_acquisition_command_surface_with_gated_actions`
- `item_087_show_decoded_values_and_graph_identity_across_views`
- `item_088_unify_recording_workflow_and_refresh_reports_live`
- `item_089_replace_unicode_command_glyphs_with_qpainter_icons`
- `item_090_deliver_recent_sessions_and_recent_trace_files`
- `item_091_clarify_graph_cursors_and_trace_graph_linkage`
- `item_092_add_bus_load_and_real_time_counters`
- `item_093_introduce_capture_writer_ports_and_reader_registry`
- `item_094_extend_adapter_capability_ports_and_roadmap_discovery`
- `item_095_prepare_an_approved_future_can_transmit_product_path`
- `item_096_remove_domain_ui_text_and_duplicated_formatting_utilities`
- `item_097_align_documentation_with_delivered_and_roadmap_capabilities`

# Definition of Done (DoD)
- [x] Generated request, product, backlog, and task docs are present.
- [x] Context-pack handoff is available when requested.
- [x] Validation passes.
- [x] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC5 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC1 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC5 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC1 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC2 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC1 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC5 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC1 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC5 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC1 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC4 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC1 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC5 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC1 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC3 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC1 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC5 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC1 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC5 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC7 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC7 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC7 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC7 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC8 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC7 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC7 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC7 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC4 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC9 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC9 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC7 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC6 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC6 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC6 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC6 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC6 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC6 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC6 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC6 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC6 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC6 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC6 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC8 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC6 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC8 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC8 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC8 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC8 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC9 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC9 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC9 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`
- request-AC10 -> This task. Proof: Implemented across task 18 delivery commits; validated with QT_QPA_PLATFORM=offscreen uv run python -m pytest (520 passed), uv run ruff check ., logics-manager lint --require-status, and logics-manager audit --group-by-doc. Source: `ce7103f`

# Validation
- (no validation recorded yet)
- command: `QT_QPA_PLATFORM=offscreen uv run python -m pytest` | result: passed | date: 2026-09-05
- Finish workflow executed on 2026-09-05.
- Linked backlog/request close verification passed.

# Report
- Not started.
- Finished on 2026-09-05.
- Linked backlog item(s): `item_057_bound_recording_name_reservation_and_cancel_it_safely`, `item_058_recover_safely_from_a_corrupt_profile_store`, `item_059_separate_exhaustive_ingestion_from_visual_coalescing`, `item_060_disconnect_the_adapter_after_a_post_connect_start_failure`, `item_061_own_export_workers_independently_of_transient_dialogs`, `item_062_rate_limit_adapter_error_events_and_rotate_event_only_recordings`, `item_063_bound_malformed_replay_diagnostics_and_prevent_false_success`, `item_064_enforce_mutually_exclusive_immutable_live_and_replay_sessions`, `item_065_drain_abandoned_workers_safely_at_process_exit`, `item_066_make_profile_writes_durable_and_multi_instance_safe`, `item_067_debounce_filters_signal_search_and_profile_persistence`, `item_068_make_manual_graph_zoom_disable_live_follow`, `item_069_decimate_plots_and_bound_measurement_recomputation`, `item_070_cache_dbc_decode_lookup_and_deduplicate_conflict_notices`, `item_071_deliver_an_aggregate_identifier_diagnostics_view`, `item_072_replace_the_trace_table_with_a_bounded_virtual_model`, `item_073_synchronize_graph_panels_incrementally_and_destroy_removed_resources`, `item_074_export_immutable_snapshots_with_efficient_row_serialization`, `item_075_log_all_operational_failures_and_expose_driver_overruns`, `item_076_enforce_class_surface_architecture_budgets`, `item_077_introduce_profile_schema_migration_dispatch`, `item_078_inject_a_recorder_factory_into_acquisition_workers`, `item_079_add_complete_interactive_button_states`, `item_080_set_fusion_and_an_application_wide_dark_palette`, `item_081_render_graphs_with_antialiasing_and_palette_derived_axes`, `item_082_standardize_table_chrome_and_data_typography`, `item_083_create_semantic_control_variants_and_dominant_start_stop_actions`, `item_084_tokenize_spacing_geometry_and_stable_focus`, `item_085_add_trace_and_graph_context_commands_with_copy_support`, `item_086_create_an_acquisition_command_surface_with_gated_actions`, `item_087_show_decoded_values_and_graph_identity_across_views`, `item_088_unify_recording_workflow_and_refresh_reports_live`, `item_089_replace_unicode_command_glyphs_with_qpainter_icons`, `item_090_deliver_recent_sessions_and_recent_trace_files`, `item_091_clarify_graph_cursors_and_trace_graph_linkage`, `item_092_add_bus_load_and_real_time_counters`, `item_093_introduce_capture_writer_ports_and_reader_registry`, `item_094_extend_adapter_capability_ports_and_roadmap_discovery`, `item_095_prepare_an_approved_future_can_transmit_product_path`, `item_096_remove_domain_ui_text_and_duplicated_formatting_utilities`, `item_097_align_documentation_with_delivered_and_roadmap_capabilities`
- Related request(s): `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`

# Links
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
