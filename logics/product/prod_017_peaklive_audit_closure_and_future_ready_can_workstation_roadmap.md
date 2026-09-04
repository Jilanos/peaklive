## prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap - PeakLive audit closure and future-ready CAN workstation roadmap
> Date: 2026-09-04
> Status: Proposed
> Related request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
> Related backlog: `item_057_bound_recording_name_reservation_and_cancel_it_safely`, `item_058_recover_safely_from_a_corrupt_profile_store`, `item_059_separate_exhaustive_ingestion_from_visual_coalescing`, `item_060_disconnect_the_adapter_after_a_post_connect_start_failure`, `item_061_own_export_workers_independently_of_transient_dialogs`, `item_062_rate_limit_adapter_error_events_and_rotate_event_only_recordings`, `item_063_bound_malformed_replay_diagnostics_and_prevent_false_success`, `item_064_enforce_mutually_exclusive_immutable_live_and_replay_sessions`, `item_065_drain_abandoned_workers_safely_at_process_exit`, `item_066_make_profile_writes_durable_and_multi_instance_safe`, `item_067_debounce_filters_signal_search_and_profile_persistence`, `item_068_make_manual_graph_zoom_disable_live_follow`, `item_069_decimate_plots_and_bound_measurement_recomputation`, `item_070_cache_dbc_decode_lookup_and_deduplicate_conflict_notices`, `item_071_deliver_an_aggregate_identifier_diagnostics_view`, `item_072_replace_the_trace_table_with_a_bounded_virtual_model`, `item_073_synchronize_graph_panels_incrementally_and_destroy_removed_resources`, `item_074_export_immutable_snapshots_with_efficient_row_serialization`, `item_075_log_all_operational_failures_and_expose_driver_overruns`, `item_076_enforce_class_surface_architecture_budgets`, `item_077_introduce_profile_schema_migration_dispatch`, `item_078_inject_a_recorder_factory_into_acquisition_workers`, `item_079_add_complete_interactive_button_states`, `item_080_set_fusion_and_an_application_wide_dark_palette`, `item_081_render_graphs_with_antialiasing_and_palette_derived_axes`, `item_082_standardize_table_chrome_and_data_typography`, `item_083_create_semantic_control_variants_and_dominant_start_stop_actions`, `item_084_tokenize_spacing_geometry_and_stable_focus`, `item_085_add_trace_and_graph_context_commands_with_copy_support`, `item_086_create_an_acquisition_command_surface_with_gated_actions`, `item_087_show_decoded_values_and_graph_identity_across_views`, `item_088_unify_recording_workflow_and_refresh_reports_live`, `item_089_replace_unicode_command_glyphs_with_qpainter_icons`, `item_090_deliver_recent_sessions_and_recent_trace_files`, `item_091_clarify_graph_cursors_and_trace_graph_linkage`, `item_092_add_bus_load_and_real_time_counters`, `item_093_introduce_capture_writer_ports_and_reader_registry`, `item_094_extend_adapter_capability_ports_and_roadmap_discovery`, `item_095_prepare_an_approved_future_can_transmit_product_path`, `item_096_remove_domain_ui_text_and_duplicated_formatting_utilities`, `item_097_align_documentation_with_delivered_and_roadmap_capabilities`
> Related task: `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`
> Related architecture: (none yet)
> Reminder: Update status, linked refs, scope, decisions, success signals, and open questions when you edit this doc.

# Overview
A complete, evidence-driven remediation and delivery roadmap that makes PeakLive correct under load, resilient under failure, legible as a professional CAN diagnostic tool, and deliberately extensible toward new formats, adapters, and later CAN transmission.

# Goals
- Eliminate the audit's P0 freezes, crashes, silent data loss, and false-success outcomes.
- Preserve exhaustive measurement facts while bounding visual work and continuous-input work.
- Make the most important diagnostic workflows discoverable, fast, and visually unambiguous.
- Replace accidental architecture constraints with tested extension seams and an honest capability roadmap.
- Keep implementation evidence current rather than relying on historical Done status.

# Non-goals
- Guarantee Windows or physical-PCAN certification in this delivery; those remain tracked acceptance work after Linux proof.
- Ship CAN transmission before its separate product and safety decision chain is approved.
- Add remote telemetry, cloud services, or automatic software updates.
- Perform a wholesale rewrite where a bounded, tested correction is sufficient.

# Scope and guardrails
- In: scaffolded request, product, backlog, orchestration task, validation, and handoff context.
- Out: unrelated workflow docs and implementation of generated tasks.

# Key product decisions
- Use structured input as the source of truth for generated docs.
- Keep generated write paths local and repo-bounded.

# Success signals
- Generated docs pass lint and audit without broad manual rewrites.
- Context-pack output can be handed to an implementation agent directly.

# References
- Product back-reference: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Task back-reference: `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`
