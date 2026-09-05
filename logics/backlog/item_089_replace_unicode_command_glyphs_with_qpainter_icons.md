## item_089_replace_unicode_command_glyphs_with_qpainter_icons - Replace Unicode command glyphs with QPainter icons
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 41%
> Complexity: Medium
> Theme: P3 visual polish
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-04 11:57:42

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: replace, unicode, command, glyphs, qpainter, icons
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- Control icons depend on font glyph interpretation and can become emoji.

# Scope
- In:
  - Create a 16px QPainter icon module and replace command glyphs.
- Out:
  - External icon assets.

# Acceptance criteria
- Icons render consistently in offscreen tests and respect enabled and checked state.

# AC Traceability
- request-AC6 -> This backlog slice. Proof: Icons render consistently in offscreen tests and respect enabled and checked state.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_017_peaklive_audit_closure_and_future_ready_can_workstation_roadmap`
- Architecture decision(s): (none yet)
- Request: `req_017_close_the_september_2026_peaklive_audit_and_deliver_its_future_ready_roadmap`
- Primary task(s): `task_018_deliver_every_september_2026_audit_correction_and_future_roadmap_milestone`

# Priority
- Priority: Low - glyph rendering varies by platform
- Rationale: Set by scaffold input or defaulted for grooming.
