## item_142_unify_graph_header_action_order_and_icon_proportions - Unify graph header action order and icon proportions
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 95%
> Complexity: Medium
> Theme: Header interaction and visual consistency
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-16 14:38:21

# AI Context
- Summary: Unify graph header action order and icon proportions.
- Keywords: unify, graph, header, action, order, icon, proportions
- Use when: Implementing or validating the responsive-stop and measurement-workspace follow-up to task_029 and task_030.
- Skip when: Changing unrelated decoding, recording formats, or data retention policies.

# Problem
- Fit precedes lifecycle controls, Follow live duplicates a play glyph, and differing button/font conventions create inconsistent apparent icon sizes.
- Overflow reparenting can disrupt ordering and must honor the requested one-line primary controls.

# Scope
- In:
  - Use the request AC6 order and group gaps: view; acquisition/status; follow/fit; cursors/readouts. Keep Play/Stop adjacent, both Fits adjacent and A/B adjacent; retain existing action semantics and shortcuts.
  - Replace font-dependent pictograms with reusable Qt/vector icons: play triangle, stop square, a distinct live-follow/time-tracking symbol, fit-both-axes and vertical-fit symbols, and cursor markers labeled A/B.
  - Use a shared 28 logical-pixel box, 16 logical-pixel icon canvas, centered artwork, consistent stroke weight and padding as the initial sizing specification; retain red Stop only when stoppable and a clearly checked Follow state.
  - Keep all seven requested controls directly on one row at supported window sizes; allocate center-panel minimum width accordingly, elide secondary text or defer secondary commands first, and preserve full readouts via accessible tooltips when needed.
  - Preserve canonical group order when overflow restores controls; below supported geometry provide accessible fallback without a second row or overlapping controls.
  - Review screenshots at the specified window sizes and 100/150/200 percent scaling, including enabled, disabled, checked and keyboard-focus states; record any platform-specific validation gap.
- Out:
  - Raster image generation, decorative animation or a new icon dependency without need.
  - New zoom/follow modes or changes to cursor and fit mathematics.

# Acceptance criteria
- AC1: Layout order matches request AC6 and remains stable after repeated narrow/wide resize and center-view changes.
- AC2: All seven requested controls remain on one line at supported geometry with coherent icon size/padding and no overlap or clipping.
- AC3: Play and Follow live, and Fit XY and Fit Y, are visibly distinct with localized explanatory tooltips, accessible names and keyboard focus.
- AC4: Automated layout/action assertions and recorded visual review demonstrate the result across supported sizes/scaling.

# Findings

## Delivered
- `src/peaklive/ui/icons.py` draws every header action from vector paths through a `QIconEngine`, so an icon is repainted at whatever size and device pixel ratio is asked for rather than scaled from artwork. `apply_header_icon` applies the shared contract: a 28 logical-pixel button box, a 16 logical-pixel icon canvas, a single stroke weight, and no text (the accessible name and tooltip already carry the name).
- Follow live is a trace pinned to its newest sample, no longer a second play triangle. Fit XY is arrows out on both axes; Fit Y is a vertical double arrow between two fixed time edges. Cursor A and B are a cursor line carrying their own letter.
- The header now registers controls in the request's documented order, and a control returning from the overflow menu is re-inserted by its canonical rank instead of appended - the defect that let a resize permute the row. Three one-pixel rules separate the four groups.

## Width priority when the row cannot hold everything
- The four-step order is: fold the deferrable commands (measurement values, then the view selector); drop the group rules; shorten elidable prose; shorten the A/B/delta reading. The seven documented commands are never folded.
- This supersedes the earlier no-elide assertion for the reading (item_055 AC3, item_129). At 1024x768 with both side panels expanded the centre column can be given at most 654 px - the side panels' own Qt minimums (228 and 110) bound it - which leaves the header 538 px against a 544 px demand. The reading therefore shortens by a few pixels there, with its untruncated value in `text()` and in its tooltip, exactly the fallback this slice's scope names. It is shown in full at 1280x720 and 1600x900.

## Visual review
- Offscreen Qt, dark theme, 1024x768 / 1280x720 / 1600x900, and 100 / 150 / 200 percent scaling. All seven commands stay on one line at every viewport with no overlap and nothing past the row edge. At 200 percent the icons are repainted rather than upscaled, with no visible softening.
- States reviewed: Play enabled and disabled, Stop enabled with its red active treatment while running and disabled otherwise, Follow live checked and unchecked, and the keyboard focus ring on each action.
- Platform gap: the review ran on Linux with the offscreen platform plugin. Native Windows rendering at those scalings is not covered here, and the repository's existing Windows offscreen layout quarantine still applies.

# AC Traceability
- request-AC6 -> This backlog slice. Proof: AC1: Layout order matches request AC6 and remains stable after repeated narrow/wide resize and center-view changes.
- request-AC7 -> This backlog slice. Proof: AC2: All seven requested controls remain on one line at supported geometry with coherent icon size/padding and no overlap or clipping.
- request-AC8 -> This backlog slice. Proof: AC3: Play and Follow live, and Fit XY and Fit Y, are visibly distinct with localized explanatory tooltips, accessible names and keyboard focus.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_030_peaklive_responsive_stop_and_readable_measurement_controls`
- Architecture decision(s): (none yet)
- Request: `req_032_restore_responsive_acquisition_stop_and_polish_the_measurement_workspace`
- Primary task(s): `task_031_deliver_responsive_stop_and_polished_measurement_workspace_controls`

# Priority
- Priority: Medium - current glyphs and ordering make acquisition and navigation actions difficult to distinguish.
- Rationale: Set by scaffold input or defaulted for grooming.
