## req_026_restore_dense_historical_curves_and_preserve_rare_diagnostic_signal_events - Restore dense historical curves and preserve rare diagnostic signal events
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Dense overview coverage and rare-event discoverability
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-12 16:30:42

# AI Context
- Summary: Correct dense-view disappearance and preserve discoverable rare diagnostic events.
- Keywords: restore, dense, historical, curves, preserve, rare, diagnostic, signal, events
- Use when: Scoping the operator-confirmed three-lane wheel-zoom regression and fidelity requirements.
- Skip when: Changing CAN transport or promising full-file late-selection decoding.

# Needs
- Keep all three previously selected historical curves visible when wheel zoom-out crosses approximately 650 s and when fitting the entire capture.
- Preserve diagnostic peaks, rare variations and errors lasting only two 10 ms samples, with source timecodes for precise follow-up; uniform stride or averaging cannot be the rendering policy.
- Apply the useful contracts of the local reference application within the existing Python/PySide6/pyqtgraph/SQLite architecture.
- Make the displayed build identifier selectable and copyable so qualification evidence does not depend on manual transcription.

# Context
- Operator confirmed that three signals from two message groups were selected before capture loading. One zoom-out step hides all curves; one zoom-in step restores them. The typed build is recorded verbatim in the diagnosis and is not yet verified against an artifact.
- Source 7cc00d6 has green Linux/Windows CI. The private source contains 1755746 CAN frames and a diagnostic 100 Hz identity has 94493 samples over 944.781020 s. No private payload or message identity belongs in the corpus.
- The diagnostic reproduces incomplete summaries after bulk plus small appends, pyqtgraph automatic peak reduction erasing a nonempty sparse result, and stale overview data after clear(). It does not reproduce the exact operator DBC/build/650 s boundary yet.
- The reference project counts visible samples, reduces time-bucket extrema to a pixel budget, returns reduction metadata and draws the result without a second automatic reducer. Its DuckDB/browser architecture and raw-range query cost are not adoption requirements.
- This is a corrective and rare-event fidelity extension of the settled historical-navigation brief. Prior task 025 status is not new proof; retain its history and qualify the missing behaviors explicitly.
- Definitions, proposed defaults, operator-confirmed pulse/dip semantics, performance targets and excluded technical debt are in logics/analysis/dense_overview_diagnosis.md.

# Acceptance criteria
- AC1: On synthetic three-lane 1/10/100 ms and irregular sources, plus the operator's preselected three-signal packaged reproduction, zoom 500/640/650/660/800 s and full extent in both directions without an unexplained empty curve when samples or event anchors exist in the viewport. Verify returned coverage and actual rendered data, not only curve options.
- AC2: Identical source rows produce equivalent coverage/extrema independent of append partition (1/16/32/33/256/4096 and mixed final batches, across multiple signals). Only complete committed summaries may serve a range; reset/reload invalidates every persisted and in-memory derivative atomically.
- AC3: Historical display uses a single explicit pixel/density-aware reduction policy, preserving source first/last, bucket extrema, chronological identity and gaps within its declared point budget. Exact overflow, empty, incomplete, loading and error remain distinct; one-point data is represented deliberately. No secondary automatic reduction may erase a prepared envelope.
- AC4: One- and two-sample diagnostic pulses and rare discrete transitions remain discoverable with original timecodes at every overview level, including events that are not bucket extrema. If anchors collide or exceed the point budget, an explicit clustered marker reports their presence/count/range and supports exact drill-down. Mandatory cases include a four-frame assertion after 50000 quiet frames and a 250 A to 180 A dip lasting 100 ms; preserve entry/extremum/recovery timecodes without requiring an amplitude threshold. Generic anomaly classification is excluded; no uniform stride or averaged surrogate is accepted.
- AC5: Navigation retains last valid data while waiting, uses at most one active and one replaceable pending request, rejects stale results including cache-hit A/B/A races, and performs no history scan on the GUI thread. Indexed query work scales with viewport budget rather than raw count; caches obey an explicit 64 MiB total limit. Proposed recorded-machine targets are warm viewport <=250 ms, cold indexed query <=1 s, heartbeat p95 lateness <=50 ms and maximum <=150 ms; index preparation is measured separately.
- AC6: Envelope/marker values never masquerade as exact analytical samples. Historical measurement overflow/missing coverage is explicit, unchanged or hidden A/B work is not reissued by pure viewport changes, and existing export coverage semantics remain unchanged. Loading/error state is nonmodal and clears correctly; investigate the reported busy cursor with evidence.
- AC7: The normal application build label is read-only, selectable and copyable with mouse/keyboard; copied identifier matches build_info().identifier and the artifact's build identity. Existing layout, accessibility and version semantics are preserved.
- AC8: Before closing, attach deterministic coverage/render/rare-event/lifecycle evidence, Linux and Windows CI results including packaging, and the identified Windows artifact's private-trace wheel-zoom reproduction. Unknown DBC/build or unavailable private qualification stays explicitly outstanding; green unit tests alone do not close the task.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_025_discoverable_rare_diagnostic_events_in_dense_historical_views`
- Architecture decision(s): (none yet)

# References
- logics/analysis/dense_overview_diagnosis.md
- logics/analysis/dense_overview_probe.py
- logics/request/req_025_restore_responsive_and_faithful_historical_graph_navigation.md
- logics/product/prod_024_peaklive_responsive_and_faithful_historical_navigation_correction.md
- src/peaklive/analysis/history.py
- src/peaklive/services/history_worker.py
- src/peaklive/ui/panels/graph_history.py
- src/peaklive/ui/panels/graph_stack.py
- src/peaklive/ui/panels/graph_navigation.py
- src/peaklive/ui/panels/measurement.py
- src/peaklive/ui/ingest_controller.py
- src/peaklive/ui/main_window.py
- tests/test_history.py
- tests/test_history_worker.py
- tests/test_graph_performance.py
- tests/test_ui_build_identity.py

# Backlog
- `item_121_make_historical_summary_coverage_complete_and_independent_of_ingest_batches`
- `item_122_render_dense_envelopes_and_rare_event_anchors_without_a_second_lossy_reduction`
- `item_123_bound_viewport_scheduling_and_expose_truthful_loading_and_measurement_states`
- `item_124_qualify_long_view_rare_event_fidelity_on_the_packaged_windows_application`
- `item_125_make_the_application_build_identifier_selectable_and_copyable`
