## req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap - Close the September 2026 PeakLive audit and deliver its future-ready roadmap
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Trustworthy, responsive, and future-ready CAN workstation
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-05 10:41:25

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: close, september, 2026, peaklive, audit, deliver, future, ready, roadmap
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Needs
- Resolve every finding in the September 2026 audit without treating completed historical Logics work as proof that its claimed outcome remains present.
- Restore measurement correctness: all acquired and replayed frames must feed facts, the frame cache, deferred decode, and series state; only visual projection may be coalesced.
- Make routine failure modes recoverable and explicit, including corrupt profiles, unavailable adapters, collision-safe recording, malformed traces, and application close during export.
- Deliver a coherent English diagnostic-tool interface and a sequenced roadmap for capabilities that are intentionally deferred or depend on future adapters and formats.

# Context
- docs/audit-2026-09.md is the authoritative evidence source. It records 96 findings, eight P0 reliability failures, performance and visual-system defects, product capability gaps, and architecture debt. Its Linux/offscreen measurements are acceptance baselines, not Windows or hardware certification.
- The operator confirmed scope covers all 44 audit roadmap actions. Existing Done Logics chains are not accepted as evidence and must not be relied upon without current tests or code evidence.
- Validation scope is correction plus Linux automated tests. Windows and live PCAN acceptance are roadmap evidence, not a release gate for this corpus.
- Adapter policy is automatic reconnect with a visible alert. Live acquisition and replay are mutually exclusive: attempting the other source is refused with a clear alert, preserving the active session. The operator chose an export wait dialog with an explicit confirm-to-force-close action.
- Corrupt profiles are renamed to a timestamped backup, a default profile is used, and a warning dialog is shown. Non-discriminating recording templates receive a numeric suffix; reservation searches at most 10000 candidates.
- The required aggregate-ID view defaults to identifier, latest frame, count, mean period, current delta-t, bus load or bitrate contribution when available, and decode status. Recent sessions and files are implementation scope; bitrate scan and adapter discovery are roadmap commitments.
- The UI language, product copy, and Logics documents are English. The visual baseline is a Fusion dark application palette, semantic control variants, explicit interactive states, QPainter icons, and diagnostic-data legibility.
- Future BLF/MDF, additional adapters, and CAN transmit are roadmap commitments. CAN transmit remains explicitly out of the current delivered product scope until a separately approved implementation chain is promoted.

# Acceptance criteria
- AC1: Every P0 item is implemented with focused Linux automated tests that fail against the audited behaviour; no P0 failure can freeze, silently corrupt a result, or silently prevent application start.
- AC2: All captured and replayed frames update session facts, frame cache, deferred decode inputs, and series state exactly once; trace and graph rendering may remain bounded and coalesced independently.
- AC3: Acquisition and replay cannot mix their data. Configuration passed to a worker is immutable for that session, and invalid recording templates cannot be persisted.
- AC4: Adapter error recovery uses bounded automatic reconnect with an explicit operator alert and rate-limited, rotating recording evidence.
- AC5: A malformed profile or trace, a failed post-connect recording start, an export during close, and recording-name collisions each have an explicit, tested operator outcome.
- AC6: The UI has an application-wide Fusion dark palette, accessible semantic states, consistent control geometry, data-aligned typography, and tests or targeted assertions for stateful behaviour where practical.
- AC7: Filtering, signal search, profile persistence, graph refresh, DBC decoding, export, replay, and trace browsing meet documented bounded-work rules and their tests assert counts or deterministic bounds rather than elapsed time alone.
- AC8: The aggregate identifier view and recent-session/file workflows are delivered, and the roadmap explicitly sequences bitrate scanning, adapter enumeration, capture-format ports, additional adapters, BLF/MDF, and future CAN transmission.
- AC9: Documentation makes no claim for a feature that is absent from code, and explains which roadmap items require hardware or a later product decision.
- AC10: The generated request chain validates with Logics Manager, includes a deep context pack, passes lint and audit, and is commit-ready with the audit and supplied external evidence.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)

# References
- docs/audit-2026-09.md
- README.md
- docs/architecture.md
- docs/product-scope.md
- docs/cantracediag-ux-delta.md
- src/peaklive
- tests

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
