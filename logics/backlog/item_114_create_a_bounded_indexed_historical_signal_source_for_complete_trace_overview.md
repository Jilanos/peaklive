## item_114_create_a_bounded_indexed_historical_signal_source_for_complete_trace_overview - Create a bounded indexed historical signal source for complete trace overview
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 80%
> Complexity: High
> Theme: Indexed replay source and multiresolution overview
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-10 12:36:27

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: create, bounded, indexed, historical, signal, source, complete, trace, overview
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- The 20,000-sample SignalSeries and 50,000-frame FrameCache are deliberately bounded, but they make early high-rate decoded values unreachable after a long replay.
- Plot-library downsampling only operates on retained values and therefore cannot represent the whole capture truthfully once the beginning has been discarded.
- A complete-history solution must enable range reads without turning trace loading into an eager, unbounded memory allocation.

# Scope
- In:
  - Define and implement a validated, temporary or session-scoped seek/index contract for supported replay files, including timestamp-to-source-range lookup and source identity checks.
  - Build bounded, deterministic multiresolution signal overview data while replaying or through indexed background work, preserving per-bucket extrema and source time coverage.
  - Expose a source-backed signal-series interface that distinguishes overview samples from exact samples and retains explicit capacity and cleanup rules.
  - Cover ASC and text TRC source indexing, malformed records, source replacement, file modification or disappearance, DBC decode failures, and cleanup on session reset.
- Out:
  - Unbounded in-memory source-frame retention or persistent user-visible cache files without an explicit lifecycle policy.
  - Changing DBC loading, CAN decoding meanings, recording output, or live acquisition data retention.

# Acceptance criteria
- AC1: A long high-rate replay has a full-span overview for a selected signal even when its raw sample total exceeds 20,000.
- AC2: Overview point count follows the documented resolution budget and each bucket preserves its source time coverage and visible extrema.
- AC4: Overview provenance identifies source-derived versus representative data and does not invent values or timestamps.
- AC6: Source/index and overview memory/disk use are bounded and reset safely with the replay session.
- AC8: Fixture-driven tests cover source indexing, complete coverage, extrema, retention bounds, and source integrity failures.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: A long high-rate replay has a full-span overview for a selected signal even when its raw sample total exceeds 20,000.
- request-AC2 -> This backlog slice. Proof: AC2: Overview point count follows the documented resolution budget and each bucket preserves its source time coverage and visible extrema.
- request-AC4 -> This backlog slice. Proof: AC4: Overview provenance identifies source-derived versus representative data and does not invent values or timestamps.
- request-AC6 -> This backlog slice. Proof: AC6: Source/index and overview memory/disk use are bounded and reset safely with the replay session.
- request-AC8 -> This backlog slice. Proof: AC8: Fixture-driven tests cover source indexing, complete coverage, extrema, retention bounds, and source integrity failures.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_022_peaklive_multiresolution_lossless_historical_trace_detail`
- Architecture decision(s): (none yet)
- Request: `req_023_deliver_multiresolution_trace_graphs_with_precise_on_demand_zoom_detail`
- Primary task(s): `task_023_deliver_bounded_multiresolution_overview_and_exact_zoom_detail_for_historical_traces`

# Priority
- Priority: High - high-rate signals currently lose most of their historical evidence after loading a real diagnostic capture.
- Rationale: Set by scaffold input or defaulted for grooming.
