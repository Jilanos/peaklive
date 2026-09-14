## item_131_deliver_ordered_bounded_replay_batches_for_frames_and_bus_events - Deliver ordered bounded replay batches for frames and bus events
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 60%
> Complexity: High
> Theme: Replay transport integrity
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-13 23:46:55

# AI Context
- Summary: Prevent valid bus events from overtaking buffered frames or bypassing replay capacity.
- Keywords: deliver, ordered, bounded, replay, batches, frames, bus, events
- Use when: Implementing a shared ordered record transport with explicit acknowledgement and EOF semantics.
- Skip when: Changing bus event meaning or dropping authoritative events for presentation speed.

# Problem
- Valid bus events bypass the four-batch semaphore and overtake earlier frames buffered in ReplayWorker.

# Scope
- In:
  - Priority rationale: event floods can freeze loading and event reordering changes measurement evidence.
  - Use one ordered batch representation for normalized frame and bus-event records with explicit queue ownership, size and acknowledgement invariants.
  - Adapt GUI projection and session facts to consume ordered records without one unbounded Qt event per source event.
  - Keep malformed-record aggregation bounded and distinct from authoritative valid event counts.
  - Cover Stop, replacement, queued terminal signals and EOF after an event-only or mixed final batch.
- Out:
  - Changing CAN parsing semantics, inventing event timestamps or dropping valid events to meet a bound.
  - Live adapter event policy redesign unless shared integration requires a compatible interface.

# Acceptance criteria
- AC1: Source frame(0.000), event(0.001), frame(0.002) is observed in the same order by trace and facts consumers.
- AC2: A blocked GUI cannot cause 10000 valid events to bypass transport capacity; event-only and mixed loads retain exact counts after drain.
- AC3: Completion requires settlement of every accepted record; cancel/replacement release only owned permits and cannot install stale records.
- AC4: Existing ASC/TRC replay, CAN identity and progress integrity tests remain green.

# AC Traceability
- request-AC2 -> This backlog slice. Proof: `tests/test_replay_ordered_transport.py::test_a_mixed_frame_event_frame_capture_is_observed_in_source_order`.
- request-AC6 -> This backlog slice. Proof: `tests/test_replay_ordered_transport.py::test_10000_valid_events_cannot_bypass_transport_capacity_without_acknowledgement` and `::test_event_only_and_mixed_loads_retain_exact_counts_after_drain`.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_027_peaklive_responsive_and_trustworthy_long_trace_preparation`
- Architecture decision(s): (none yet)
- Request: `req_029_make_long_trace_loading_responsive_ordered_and_failure_explicit`
- Primary task(s): `task_028_deliver_responsive_ordered_and_measurable_long_trace_loading`

# Priority
- Priority: High
- Rationale: Event floods can freeze loading and reordering changes measurement evidence.

# Validation
- Wave 1 (2026-09-14): `ReplayWorker` now dispatches one `records_received(list)` signal carrying frames and valid bus events together, in source order, through the existing four-permit acknowledged semaphore; the previous unbounded, unacknowledged `event_received` channel is removed. Anomaly-summary events are appended to the same trailing batch instead of being emitted out of band. `session_controller.py`/`ingest_controller.py` consume one ordered batch by grouping consecutive same-type runs (`_ingest_replay_records`) and processing the runs strictly in arrival order, so frame/event interleaving from the source is preserved into `TraceBuffer`/`SessionFacts`. Local proof: `uv run python -m pytest tests/` -> 629 passed (626 baseline + 3 new); `tests/test_replay_ordered_transport.py` covers AC1 (exact frame/event/frame source order), AC2 (a stalled/unacknowledged consumer bounds pending permits and delivered events to `MAX_PENDING_BATCHES * BATCH_SIZE` instead of flooding through 10000 events), and exact frame/event counts after drain on a mixed capture; `tests/test_replay_worker.py`, `tests/test_replay_integrity.py`, `tests/test_trace_performance.py` and `tests/test_ui_structure.py` (module line budget) pass unchanged.

# Report
- AC3 (settlement/cancel/replacement permit ownership) is covered indirectly by the unchanged generation-check and `_clear_pending_replay_batches`/`abandon_worker` machinery, which now applies uniformly to mixed batches; no new dedicated regression was added for it in this wave because the existing cancellation/replacement tests already exercise that path and stayed green. `logics/analysis/trace_load_followup_probe.py` (the audit's diagnostic script) still calls the old `frames_received`/`event_received` API and will raise `AttributeError` if re-run as-is; it is left unmodified as a frozen record of the pre-fix reproduction, superseded by `tests/test_replay_ordered_transport.py` and the item_130 harness.
