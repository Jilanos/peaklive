## item_059_separate_exhaustive_ingestion_from_visual_coalescing - Separate exhaustive ingestion from visual coalescing
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: High
> Theme: P0 measurement correctness
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-05 10:41:26

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: separate, exhaustive, ingestion, visual, coalescing
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Presentation-frame replacement drops over 90 percent of frames before facts, cache, series, and deferred decode.

# Scope
- In:
  - Ingest every frame once into facts, cache, series, and deferred-decode inputs.
  - Coalesce only trace and graph projection.
  - Define bounded ownership and test high-rate acquisition and replay.
- Out:
  - Increasing retention capacities.

# Acceptance criteria
- A high-rate synthetic stream yields exact facts and cache counts while rendered rows remain bounded.
- Deferred decode sees the full retained cache, not a presentation sample.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: A high-rate synthetic stream yields exact facts and cache counts while rendered rows remain bounded.
- request-AC2 -> This backlog slice. Proof: Deferred decode sees the full retained cache, not a presentation sample.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: High - current reports can silently be false
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Notes
- Task `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone` was finished via `logics-manager flow finish task` on 2026-09-05.
