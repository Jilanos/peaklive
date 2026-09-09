## req_022_make_peaklive_graph_lanes_self_identifying_and_received_frames_globally_numbered - Make PeakLive graph lanes self-identifying and received frames globally numbered
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 90%
> Confidence: 85%
> Complexity: Medium
> Theme: Graph-lane readability and frame provenance
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-09 18:32:05

# AI Context
- Summary: Replaces technical vertical graph labels with coloured horizontal lane identities and adds a CAN-frame-only sequence that stays meaningful after the Trace display window rotates.
- Keywords: peaklive, graph, lanes, self, identifying, received, frames, globally, numbered
- Use when: Graph lanes are difficult to identify, technical DBC provenance leaks into routine graph reading, or a retained trace row needs its position in the acquisition known.
- Skip when: Changing CAN payload semantics, retaining all historical frames in memory, altering recording/replay formats, or adding a manual graph-colour system.

# Needs
- Make every shown graph lane readable at a glance with a horizontal, curve-coloured signal title rather than a rotated technical Y-axis title.
- Add a restrained visual separator between adjacent graph lanes so their Y axes and data regions do not visually run together.
- Show each received CAN frame a monotonic frame number from the beginning of the acquisition, independent of the 5,000-record display buffer.
- Keep technical DBC provenance available without exposing hashes and identifier keys as the default graph title or hover text.
- Complete all product tests only after implementation is finished; after the local CI gate passes, push and follow the remote CI to its final verdict.

# Context
- GraphStackPanel creates one pyqtgraph PlotWidget per shown signal. It currently puts signal_label(signal_key) on the left AxisItem, which pyqtgraph renders vertically.
- signal_label deliberately includes message/signal plus DBC hash and CAN identifier to disambiguate sources. PlotWidget also receives a tooltip containing the complete technical signal key and trace colour.
- The graph container has zero spacing and lanes may shrink because each plot has a zero minimum height. The desired operator presentation is a compact scope-style lane: a horizontal coloured title at its top-left and a subtle separator between lanes.
- TraceBuffer has a stable record index but it counts both CAN frames and bus events. The requested visible frame number must count CAN frames only, start at 1 for a new acquisition, stay monotonic after old display records age out, and leave event rows unnumbered.
- The 5,000-record TraceBuffer remains a bounded display projection. Recording and session ingestion must remain lossless on their existing paths; the new frame number must not imply that all historical rows remain in memory.
- The existing workspace intentionally allows a dense, non-scrolling graph surface. Operators may remove shown signals when a chosen set becomes too dense; this delivery must not impose a new arbitrary lane limit.

# Acceptance criteria
- AC1: Each shown signal lane displays a concise horizontal title at the top-left using the exact colour of its curve. The title defaults to the operator-facing signal name, optionally followed by its unit, and is readable at 1024x768, 1280x720, and 1600x900.
- AC2: Left Y axes retain readable numeric ticks but no rotated technical signal title. Adjacent lanes have a subtle, theme-derived horizontal separator so axes and traces are visually distinct without reducing the plot area materially.
- AC3: The graph's default hover text never exposes the full DBC hash/identifier signal key. Full provenance remains available through an intentional detail surface with an accessible non-colour-only identity.
- AC4: The Trace table has a visible frame-number column. It begins at 1 for each acquisition or replay session, increments only for received CAN frame records, remains monotonic after the 5,000-record trace window rotates, and is blank for bus-event rows.
- AC5: Trace filters, selection, copying, paging, recording, replay, decoding, exports, session facts, graph navigation, and bounded-memory guarantees retain their current semantics.
- AC6: No product tests are run until all implementation changes are complete. Then the complete relevant test suite and local CI gate pass; only after that gate passes is the implementation pushed, and the remote CI is monitored to a recorded final pass/fail verdict.
- AC7: All changed user-facing text uses the i18n catalog, and no CAN transmit, payload interpretation, acquisition behaviour, or DBC decoding semantics are introduced or changed.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_021_peaklive_self_identifying_graph_lanes_and_durable_frame_sequence`
- Architecture decision(s): (none yet)

# References
- src/peaklive/ui/panels/graph_stack.py
- src/peaklive/ui/theme.py
- src/peaklive/analysis/dbc.py
- src/peaklive/analysis/trace.py
- src/peaklive/ui/panels/trace_view.py
- src/peaklive/ui/ingest_controller.py
- src/peaklive/domain/models.py
- tests/test_ui_workspace_refinement.py
- tests/test_trace_buffer.py
- tests/test_ui_analyst.py

# Backlog
- `item_112_render_concise_coloured_graph_lane_titles_with_subtle_lane_separation`
- `item_113_expose_an_acquisition_wide_received_frame_sequence_in_trace`
