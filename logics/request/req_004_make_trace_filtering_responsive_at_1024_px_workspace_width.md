## req_004_make_trace_filtering_responsive_at_1024_px_workspace_width - Make trace filtering responsive at 1024 px workspace width
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: Windows integration testing exposed a trace filter header whose 1104 px minimum width leaves only about 402 px for the central workspace at a 1024 px viewport. The trace workspace must remain usable without changing trace-filter semantics or the existing graph-control work.
> Confidence: 85%
> Complexity: M
> Theme: Workspace responsiveness
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-08-26 18:18:06

# AI Context
- Summary: Keep the Trace workspace operable at the 1024 px desktop baseline by allowing its filter controls to adapt rather than imposing an oversized minimum width.
- Keywords: trace, filters, responsive, 1024, minimum width, workspace
- Use when: A narrow desktop workspace is constrained by the Trace filter header rather than by the trace table's available content.
- Skip when: The change would alter which records match filters, their persisted settings, or the graph-toolbar layout already delivered by item_028.

# Priority

Medium — a verified 1024 px usability defect blocks a supported desktop baseline, but acquisition and data integrity remain unaffected.

# Needs
- Make the primary Trace filter controls responsive so the central workspace remains usable at a 1024 px-wide desktop viewport.
- Preserve the display-only filtering model, active-filter chips, keyboard focus, and persisted Trace filter settings.

# Context
- The Windows offscreen integration run of the workspace visual-usability wave measured `TracePanel.minimumSizeHint().width()` at 1104 px.
- At a 1024 px viewport, that minimum forces the center workspace to roughly 402 px after the surrounding layout is allocated, making the Trace area unusable.
- `TraceFilterBar` currently puts its label, three primary line edits, frame/event toggles, More filters, Columns, and Clear filters in one horizontal header.
- The issue was observed while qualifying the rebuilt Windows executable; it was intentionally excluded from item_028, which scoped graph controls rather than the Trace filter header.

# Acceptance criteria
- AC1: At a 1024x768 workspace with Signals and Inspector in their normal expanded state, the Trace panel no longer imposes a minimum width greater than the available center column and remains visibly usable.
- AC2: The primary filter controls adapt through a deliberate compact or wrapping layout without clipped controls, overlapping text, or horizontal overflow.
- AC3: All existing Trace filter fields, frame/event toggles, More filters behavior, Columns action, Clear filters action, active chips, and Ctrl+F focus remain available and accessible.
- AC4: Filtering remains display-only: the matching logic, stored Trace settings, record buffer, acquisition behavior, and decode behavior are unchanged.
- AC5: Headless offscreen regression coverage exercises the 1024 px layout and preserves the existing Trace filtering behavior.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)

# References
- `src/peaklive/ui/panels/trace_view.py`
- `src/peaklive/ui/panels/trace_filters.py`
- `src/peaklive/ui/workspace_center.py`
- `src/peaklive/ui/main_window.py`
- `tests/test_ui.py`
- `tests/test_ui_analyst.py`
- `docs/windows-hardware-acceptance.md`

# Backlog
- none
