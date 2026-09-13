## item_131_deliver_ordered_bounded_replay_batches_for_frames_and_bus_events - Deliver ordered bounded replay batches for frames and bus events
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Replay transport integrity
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-13 23:32:48

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
- request-AC2 -> This backlog slice. Proof: AC1: Source frame(0.000), event(0.001), frame(0.002) is observed in the same order by trace and facts consumers.
- request-AC6 -> This backlog slice. Proof: AC2: A blocked GUI cannot cause 10000 valid events to bypass transport capacity; event-only and mixed loads retain exact counts after drain.

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
