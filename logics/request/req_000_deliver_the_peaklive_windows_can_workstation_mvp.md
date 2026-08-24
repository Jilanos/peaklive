## req_000_deliver_the_peaklive_windows_can_workstation_mvp - Deliver the PeakLive Windows CAN workstation MVP
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 95%
> Confidence: 90%
> Complexity: High
> Theme: Windows CAN diagnostics
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-08-24 12:28:10

# AI Context
- Summary: Defines the complete receive-only Windows MVP, from one live Classic CAN channel through trustworthy recording, DBC analysis, plots, replay, export, and installation.
- Keywords: deliver, peaklive, windows, can, workstation, mvp
- Use when: Planning or validating any PeakLive MVP slice that changes acquisition, saved evidence, live/offline analysis, privacy, or Windows delivery.
- Skip when: Working only on the companion browser trace reader or on post-MVP transmission, dashboards, alarms, CAN FD, or multi-channel support.

# Needs
- Give a three-engineer team an installable Windows application for live Classic CAN acquisition, decoding, plotting, recording, and replay.
- Make saved evidence independent from display filtering and UI performance.
- Provide materially stronger large-trace and live-compute behaviour than the companion browser-only trace reader.
- Keep the MVP application-level receive-only while explicitly modelling controller acknowledgement and passive listen-only behaviour for later safe transmission support.
- Keep all vehicle data local and make future hardware adapters possible without rewriting the product core.

# Context
- The initial hardware is one currently connected Classic USB CAN adapter exposed through an installed Windows driver API.
- The desired visual language and analysis workflows come from the existing companion trace-analysis product.
- ASC is the primary interoperable recording format and supported text TRC files must remain readable.
- Display filters must never remove frames from active recordings, and driver or recording errors must be preserved.
- The MVP excludes frame transmission, dashboards, and alarms but must retain clean architecture seams for those later capabilities.
- The public source repository is licensed under Apache-2.0.

# Acceptance criteria
- AC1: A self-contained x64 installer deploys and launches PeakLive on supported Windows 10/11 machines without requiring a separately installed Python runtime.
- AC2: PeakLive discovers the supported Classic USB CAN channel, connects with a manually selected 125/250/500/1000 kbit/s bitrate, exposes normal receive versus passive listen-only when supported, and never exposes frame transmission in the MVP.
- AC3: An assisted bitrate scan can evaluate common rates without claiming certainty on a quiet or acknowledgement-dependent bus, and reports confidence and failure reasons.
- AC4: Physical disconnect, reconnect, bus warning/passive/off, driver overrun, and unsupported configuration states are visible, preserved as events, and do not require an application restart for recovery where the driver permits.
- AC5: Start Acquisition applies the visible profile and opens recording when configured; Stop Acquisition finalizes it, while every adapter-delivered frame is recorded regardless of display filters, representable errors/events remain in ASC, non-portable events remain in a JSONL sidecar, and known loss or unclean close is marked.
- AC6: A 60-minute practical-maximum Classic CAN load test completes without recorder queue overflow on the documented reference machine, while the UI remains interactive and any upstream driver loss remains explicitly detectable.
- AC7: The live trace presents chronological raw frames and decoded messages with identifier, direction/type, DLC, payload, timestamp/delta, channel, and error/state information; filters affect presentation only.
- AC8: Users can load multiple DBC files, resolve non-equivalent arbitration-ID conflicts deterministically, inspect decoded values and enums, and retain undecodable frames unchanged.
- AC9: Users can select and render at least eight live decoded signals with a typical presentation latency below 250 ms, bounded memory, zoom/pan, and A/B measurement cursors under the reference load.
- AC10: PeakLive replays ASC and supported text TRC files incrementally, preserves malformed records as anomalies where recovery is safe, and supports large traces without loading the complete file into UI memory.
- AC11: Users can export selected decoded signals and time ranges to streamed CSV and Parquet outputs.
- AC12: Named measurement profiles persist channel, bitrate, controller mode, ordered DBCs/conflict choices, favorites, filters, plots, layout, recording policy, capture path, and collision-safe date/time/profile/iteration filename template; the last profile is displayed at startup without silently reconnecting.
- AC13: The application opens no listening network service, performs no upload or analytics, and stores captures, DBC references, caches, and settings only in documented local paths.
- AC14: Automated tests exercise the domain core with fake/replay adapters, synthetic saturated/error traffic, available anonymized real captures, parsing and DBC fixtures, recorder recovery, display-only filtering, error preservation, and an install smoke test; hardware acceptance steps are documented and repeatable.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_001_peaklive_windows_can_workstation`
- Architecture decision(s): (none yet)

# References
- README.md
- docs/product-scope.md
- docs/architecture.md
- docs/adr/0001-native-python-qt-stack.md
- docs/adr/0002-lossless-recording-bounded-projections.md
- docs/adr/0003-hardware-adapter-boundary.md

# Backlog
- `item_001_establish_the_native_windows_application_foundation`
- `item_002_integrate_robust_classic_usb_can_acquisition`
- `item_003_build_the_complete_and_recoverable_recording_pipeline`
- `item_004_deliver_the_live_trace_and_display_only_filtering_workspace`
- `item_005_add_deterministic_multi_dbc_live_decoding`
- `item_006_render_bounded_real_time_signal_plots_and_measurements`
- `item_007_implement_incremental_asc_and_trc_replay_with_decoded_export`
- `item_008_package_and_qualify_the_windows_mvp`
