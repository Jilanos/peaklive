## task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone - Deliver every September 2026 audit correction and future roadmap milestone
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 46%
> Complexity: Medium
> Theme: Implementation delivery
> Reminder: Update status/understanding/confidence/progress and linked request/backlog references when you edit this doc.
> Owner: paul.mondou@circle-mobility.com
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: deliver, september, 2026, audit, correction, future, roadmap, milestone
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Context
- Orchestrate the scaffolded request chain and keep sibling implementation slices linked.

# Plan
- [ ] 1. Wave 1 High: reproduce all P0 defects as failing Linux tests, land profile recovery, bounded reservation, post-connect cleanup, malformed replay handling, session isolation, error backoff/reconnect, export ownership, abandoned-worker cleanup, and durable profile writes.
- [ ] 2. Wave 2 High: separate exhaustive data ingestion from visual coalescing; prove facts, caches, deferred decode, series, and reports against high-rate live and replay fixtures.
- [ ] 3. Wave 3 Medium: deliver bounded input, decode, graph, export, trace, and architecture work, prioritizing responsiveness proofs before UI evolution.
- [ ] 4. Wave 4 Medium: deliver the Fusion English visual system and diagnostic workflows, including aggregate IDs and always-gated acquisition controls.
- [ ] 5. Wave 5 Low: deliver finish work, recents, graph linkage, counters, extension ports, and an honest staged roadmap for bitrate scan, discovery, BLF/MDF, adapters, and future CAN transmit.
- [ ] 6. After every wave run focused tests; at closeout run the full Linux suite, Logics validation, lint, audit, and documentation consistency checks. Include the audit and supplied external evidence in the commit under operator control.
- [ ] ADR 009 checkpoint: update affected Logics docs during each meaningful wave and leave the repo commit-ready.
- [ ] Keep commit creation under operator control; do not force one commit per micro-step.
- [ ] GATE: do not close until lint, audit, and scaffold validation pass.

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
- [ ] Generated request, product, backlog, and task docs are present.
- [ ] Context-pack handoff is available when requested.
- [ ] Validation passes.
- [ ] Meaningful waves followed ADR 009: affected docs updated and the repo left commit-ready without automatic commits.

# AC Traceability
- request-AC1 -> `item_057_bound_recording_name_reservation_and_cancel_it_safely`. Proof deferred to slice closeout.
- request-AC5 -> `item_057_bound_recording_name_reservation_and_cancel_it_safely`. Proof deferred to slice closeout.
- request-AC1 -> `item_058_recover_safely_from_a_corrupt_profile_store`. Proof deferred to slice closeout.
- request-AC5 -> `item_058_recover_safely_from_a_corrupt_profile_store`. Proof deferred to slice closeout.
- request-AC1 -> `item_059_separate_exhaustive_ingestion_from_visual_coalescing`. Proof deferred to slice closeout.
- request-AC2 -> `item_059_separate_exhaustive_ingestion_from_visual_coalescing`. Proof deferred to slice closeout.
- request-AC1 -> `item_060_disconnect_the_adapter_after_a_post_connect_start_failure`. Proof deferred to slice closeout.
- request-AC5 -> `item_060_disconnect_the_adapter_after_a_post_connect_start_failure`. Proof deferred to slice closeout.
- request-AC1 -> `item_061_own_export_workers_independently_of_transient_dialogs`. Proof deferred to slice closeout.
- request-AC5 -> `item_061_own_export_workers_independently_of_transient_dialogs`. Proof deferred to slice closeout.
- request-AC1 -> `item_062_rate_limit_adapter_error_events_and_rotate_event_only_recordings`. Proof deferred to slice closeout.
- request-AC4 -> `item_062_rate_limit_adapter_error_events_and_rotate_event_only_recordings`. Proof deferred to slice closeout.
- request-AC1 -> `item_063_bound_malformed_replay_diagnostics_and_prevent_false_success`. Proof deferred to slice closeout.
- request-AC5 -> `item_063_bound_malformed_replay_diagnostics_and_prevent_false_success`. Proof deferred to slice closeout.
- request-AC1 -> `item_064_enforce_mutually_exclusive_immutable_live_and_replay_sessions`. Proof deferred to slice closeout.
- request-AC3 -> `item_064_enforce_mutually_exclusive_immutable_live_and_replay_sessions`. Proof deferred to slice closeout.
- request-AC1 -> `item_065_drain_abandoned_workers_safely_at_process_exit`. Proof deferred to slice closeout.
- request-AC5 -> `item_065_drain_abandoned_workers_safely_at_process_exit`. Proof deferred to slice closeout.
- request-AC1 -> `item_066_make_profile_writes_durable_and_multi_instance_safe`. Proof deferred to slice closeout.
- request-AC5 -> `item_066_make_profile_writes_durable_and_multi_instance_safe`. Proof deferred to slice closeout.
- request-AC7 -> `item_067_debounce_filters_signal_search_and_profile_persistence`. Proof deferred to slice closeout.
- request-AC7 -> `item_068_make_manual_graph_zoom_disable_live_follow`. Proof deferred to slice closeout.
- request-AC7 -> `item_069_decimate_plots_and_bound_measurement_recomputation`. Proof deferred to slice closeout.
- request-AC7 -> `item_070_cache_dbc_decode_lookup_and_deduplicate_conflict_notices`. Proof deferred to slice closeout.
- request-AC8 -> `item_071_deliver_an_aggregate_identifier_diagnostics_view`. Proof deferred to slice closeout.
- request-AC7 -> `item_072_replace_the_trace_table_with_a_bounded_virtual_model`. Proof deferred to slice closeout.
- request-AC7 -> `item_073_synchronize_graph_panels_incrementally_and_destroy_removed_resources`. Proof deferred to slice closeout.
- request-AC7 -> `item_074_export_immutable_snapshots_with_efficient_row_serialization`. Proof deferred to slice closeout.
- request-AC4 -> `item_075_log_all_operational_failures_and_expose_driver_overruns`. Proof deferred to slice closeout.
- request-AC9 -> `item_076_enforce_class_surface_architecture_budgets`. Proof deferred to slice closeout.
- request-AC9 -> `item_077_introduce_profile_schema_migration_dispatch`. Proof deferred to slice closeout.
- request-AC7 -> `item_078_inject_a_recorder_factory_into_acquisition_workers`. Proof deferred to slice closeout.
- request-AC6 -> `item_079_add_complete_interactive_button_states`. Proof deferred to slice closeout.
- request-AC6 -> `item_080_set_fusion_and_an_application_wide_dark_palette`. Proof deferred to slice closeout.
- request-AC6 -> `item_081_render_graphs_with_antialiasing_and_palette_derived_axes`. Proof deferred to slice closeout.
- request-AC6 -> `item_082_standardize_table_chrome_and_data_typography`. Proof deferred to slice closeout.
- request-AC6 -> `item_083_create_semantic_control_variants_and_dominant_start_stop_actions`. Proof deferred to slice closeout.
- request-AC6 -> `item_084_tokenize_spacing_geometry_and_stable_focus`. Proof deferred to slice closeout.
- request-AC6 -> `item_085_add_trace_and_graph_context_commands_with_copy_support`. Proof deferred to slice closeout.
- request-AC6 -> `item_086_create_an_acquisition_command_surface_with_gated_actions`. Proof deferred to slice closeout.
- request-AC6 -> `item_087_show_decoded_values_and_graph_identity_across_views`. Proof deferred to slice closeout.
- request-AC6 -> `item_088_unify_recording_workflow_and_refresh_reports_live`. Proof deferred to slice closeout.
- request-AC6 -> `item_089_replace_unicode_command_glyphs_with_qpainter_icons`. Proof deferred to slice closeout.
- request-AC8 -> `item_090_deliver_recent_sessions_and_recent_trace_files`. Proof deferred to slice closeout.
- request-AC6 -> `item_091_clarify_graph_cursors_and_trace_graph_linkage`. Proof deferred to slice closeout.
- request-AC8 -> `item_092_add_bus_load_and_real_time_counters`. Proof deferred to slice closeout.
- request-AC8 -> `item_093_introduce_capture_writer_ports_and_reader_registry`. Proof deferred to slice closeout.
- request-AC8 -> `item_094_extend_adapter_capability_ports_and_roadmap_discovery`. Proof deferred to slice closeout.
- request-AC8 -> `item_095_prepare_an_approved_future_can_transmit_product_path`. Proof deferred to slice closeout.
- request-AC9 -> `item_095_prepare_an_approved_future_can_transmit_product_path`. Proof deferred to slice closeout.
- request-AC9 -> `item_096_remove_domain_ui_text_and_duplicated_formatting_utilities`. Proof deferred to slice closeout.
- request-AC9 -> `item_097_align_documentation_with_delivered_and_roadmap_capabilities`. Proof deferred to slice closeout.
- request-AC10 -> `item_097_align_documentation_with_delivered_and_roadmap_capabilities`. Proof deferred to slice closeout.

# Validation
- (no validation recorded yet)

# Report
- Not started.

# Links
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
