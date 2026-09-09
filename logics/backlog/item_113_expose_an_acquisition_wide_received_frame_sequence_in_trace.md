## item_113_expose_an_acquisition_wide_received_frame_sequence_in_trace - Expose an acquisition-wide received-frame sequence in Trace
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 90%
> Complexity: Medium
> Theme: Trace provenance
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-09 18:47:28

# AI Context
- Summary: Adds a CAN-frame-only, session-monotonic sequence number to TraceRecord/TraceBuffer and a default-visible, translated Trace "Frame #" column, so a displayed row's place in the whole acquisition survives the bounded 5,000-row retention window.
- Keywords: expose, acquisition, wide, received, frame, sequence, trace
- Use when: Changing how a Trace row's global position is numbered or explained, or auditing that the sequence stays frame-only, monotonic, and unaffected by filtering/rotation.
- Skip when: Changing the TraceBuffer's retention bound, ASC/TRC file formats, arbitration-ID assignment, or physical CAN frame ordering.

# Problem
- The TraceBuffer's 5,000-row retention bound means a row position is not a session-wide frame number.
- Its internal record index is not suitable as the requested frame number because it includes bus-event rows as well as CAN frames.
- An operator needs a stable frame sequence for the received CAN records retained in the current display window.

# Scope
- In:
  - Add a frame-only monotonic session sequence at ingestion, starting at 1 for every new live or replay session.
  - Expose it as an optional-by-default or default-visible Trace column with a concise i18n label and sensible width.
  - Leave event records blank in this column while retaining their existing stable record selection identity.
  - Ensure the number remains global after trace retention removes older rows, and document that it is sequence/provenance rather than the number of rows currently retained.
  - Add final regression coverage for live and replay sessions, interleaved events, buffer rotation, filtering, selection, copying, column persistence, and no change to recording or decode paths.
- Out:
  - Increasing the TraceBuffer capacity or storing all session frames in memory.
  - Changing ASC/TRC file formats, assigning a CAN identifier, or changing physical CAN frame order.
  - Renumbering historical recordings when they are reopened.

# Acceptance criteria
- AC1: Received CAN frames show the sequence 1, 2, 3 and so on from session start; event rows are blank and do not consume a sequence value.
- AC2: After more than 5,000 trace records, the retained tail displays its original global frame numbers rather than a local X/5000 count.
- AC3: The sequence survives trace filtering and does not disrupt selection, copy-row actions, display-only filtering, recording, replay, or session reports.
- AC4: The column label and explanatory text are translated and make clear that trace retention remains bounded.

# AC Traceability
- request-AC4 -> This backlog slice. Proof: AC1: Received CAN frames show the sequence 1, 2, 3 and so on from session start; event rows are blank and do not consume a sequence value.
- request-AC5 -> This backlog slice. Proof: AC2: After more than 5,000 trace records, the retained tail displays its original global frame numbers rather than a local X/5000 count.
- request-AC6 -> This backlog slice. Proof: AC3: The sequence survives trace filtering and does not disrupt selection, copy-row actions, display-only filtering, recording, replay, or session reports.
- request-AC7 -> This backlog slice. Proof: AC4: The column label and explanatory text are translated and make clear that trace retention remains bounded.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_021_peaklive_self_identifying_graph_lanes_and_durable_frame_sequence`
- Architecture decision(s): (none yet)
- Request: `req_022_make_peaklive_graph_lanes_self_identifying_and_received_frames_globally_numbered`
- Primary task(s): `task_022_deliver_readable_graph_lanes_and_a_global_received_frame_sequence`

# Priority
- Priority: High - the current retained-row count does not tell an operator where a displayed frame falls within a live session.
- Rationale: Set by scaffold input or defaulted for grooming.
