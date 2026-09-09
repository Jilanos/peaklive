## item_112_render_concise_coloured_graph_lane_titles_with_subtle_lane_separation - Render concise coloured graph-lane titles with subtle lane separation
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 90%
> Complexity: Medium
> Theme: Graph lane readability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-09 18:47:28

# AI Context
- Summary: Replaces the rotated, hash-qualified left-axis plot title with a concise, curve-coloured horizontal lane header and a subtle inter-lane separator, keeping the full DBC identity reachable only through the header's own tooltip/accessible name.
- Keywords: render, concise, coloured, graph, lane, titles, subtle, separation
- Use when: Changing how a graph lane's identity, colour, or separator is presented, or auditing that the plot's default hover text never leaks DBC provenance.
- Skip when: Changing decoded values, curve colours themselves, axis fitting/navigation semantics, or the number of lanes a workspace may show.

# Problem
- Each PlotWidget assigns a long provenance-qualified signal label to its left Y AxisItem, which pyqtgraph rotates vertically and which becomes illegible when several lanes are compacted.
- The PlotWidget-wide tooltip exposes an internal DBC hash, frame identifier, and signal key when the operator hovers the axis region.
- Zero spacing between stacked plots leaves no quiet visual boundary between adjacent axes and traces.

# Scope
- In:
  - Replace the left-axis title with a compact horizontal lane header rendered inside or immediately above each plot lane.
  - Derive the visible header from the operator-facing signal name and optional unit; colour it with the lane's deterministic curve colour.
  - Keep Y tick labels and shared X navigation intact, while applying a subtle theme-derived separator between adjacent lanes.
  - Replace the broad technical PlotWidget tooltip with a concise operator tooltip and preserve full signal provenance in an intentional accessible detail surface.
  - Cover title text, title/curve colour equality, separator geometry, hidden bottom axes, compact viewport behaviour, and preservation of navigation/cursor semantics after implementation is complete.
- Out:
  - Manual trace-colour assignment or per-profile curve palettes.
  - Changing decoded values, units, sample retention, cursor calculations, or axis fitting semantics.
  - Adding a vertical scroll area or restricting the number of simultaneously shown lanes.

# Acceptance criteria
- AC1: A shown lane has one horizontal, curve-coloured title containing its concise operator identity and optional unit; no rotated technical title is rendered on the left axis.
- AC2: Adjacent lanes have a visible but restrained separator and retain legible Y ticks at the supported workspace sizes.
- AC3: Hovering the graph does not disclose a raw DBC hash or identifier key by default; detailed provenance remains intentionally reachable and accessible.
- AC4: Shared X links, follow-live, fit actions, A/B lines, measurements, downsampling, and plot accessibility retain their current behaviour.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: A shown lane has one horizontal, curve-coloured title containing its concise operator identity and optional unit; no rotated technical title is rendered on the left axis.
- request-AC2 -> This backlog slice. Proof: AC2: Adjacent lanes have a visible but restrained separator and retain legible Y ticks at the supported workspace sizes.
- request-AC3 -> This backlog slice. Proof: AC3: Hovering the graph does not disclose a raw DBC hash or identifier key by default; detailed provenance remains intentionally reachable and accessible.
- request-AC5 -> This backlog slice. Proof: AC4: Shared X links, follow-live, fit actions, A/B lines, measurements, downsampling, and plot accessibility retain their current behaviour.
- request-AC7 -> This backlog slice. Proof: AC4: Shared X links, follow-live, fit actions, A/B lines, measurements, downsampling, and plot accessibility retain their current behaviour.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_021_peaklive_self_identifying_graph_lanes_and_durable_frame_sequence`
- Architecture decision(s): (none yet)
- Request: `req_022_make_peaklive_graph_lanes_self_identifying_and_received_frames_globally_numbered`
- Primary task(s): `task_022_deliver_readable_graph_lanes_and_a_global_received_frame_sequence`

# Priority
- Priority: High - unreadable vertical technical labels prevent an operator from identifying active signals during live diagnosis.
- Rationale: Set by scaffold input or defaulted for grooming.
