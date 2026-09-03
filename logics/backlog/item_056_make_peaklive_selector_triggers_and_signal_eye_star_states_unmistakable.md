## item_056_make_peaklive_selector_triggers_and_signal_eye_star_states_unmistakable - Make PeakLive selector triggers and signal eye-star states unmistakable
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Dark-theme control and icon state clarity
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: peaklive, selector, triggers, signal, eye, star, states, unmistakable
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- A white rectangle at the right of combo boxes does not communicate a drop-down action in the dark theme.
- The selected favorite uses the same cyan family as visibility state, while the desired selected favorite needs a decisive bright yellow.
- The checked and unchecked eye/star states are too similar for rapid signal selection.

# Scope
- In:
  - Implement and render-verify an intuitive, high-contrast combo trigger across all application QComboBox states and popups.
  - Keep the inactive favorite star unchanged and change only its selected presentation to bright saturated yellow.
  - Strengthen selected/unselected differentiation for both visibility eye and favorite star without relying on colour alone.
  - Preserve the existing tree interaction model, keyboard operation, screen-reader state, filters, and persisted shown/favorite selections.
  - Add focused rendered contrast/state tests for selectors and signal actions.
- Out:
  - Changing DBC/message/signal tree hierarchy or action-column layout.
  - Changing the meaning of shown or favorite state, DBC enablement, decoding, or profile storage.
  - Rebranding unrelated controls.

# Acceptance criteria
- AC1: At each application combo box, including channel, measurement profile, Graphs only, and Trace only, the right-side trigger is a recognizable high-contrast drop-down symbol with coherent normal, hover, focus, disabled, and popup states; no unexplained white rectangle is visible on the supported desktop platform.
- AC5: An unselected favorite star keeps its current muted visual treatment. A selected favorite star is filled or otherwise selected in a bright, saturated yellow with materially higher contrast. The shown/hidden eye likewise has a clearly stronger checked/unchecked distinction through shape fill, colour, and/or contrast, without relying on colour alone.
- AC6: Eye and favorite actions keep their current click, keyboard, tooltip, accessible-name/state, filtering, and profile-persistence behavior; their state remains unambiguous in normal, hover, focus, and disabled rendering.
- AC7: Focused offscreen/rendered UI regression tests prove combo trigger contrast, removed-control absence, enlarged fit glyph geometry, one-row containment, simultaneous complete A/B timestamps, absent window/no-sample text, Follow live placement, eye/star state contrast, and preserved graph/signal workflows.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: At each application combo box, including channel, measurement profile, Graphs only, and Trace only, the right-side trigger is a recognizable high-contrast drop-down symbol with coherent normal, hover, focus, disabled, and popup states; no unexplained white rectangle is visible on the supported desktop platform.
- request-AC5 -> This backlog slice. Proof: AC5: An unselected favorite star keeps its current muted visual treatment. A selected favorite star is filled or otherwise selected in a bright, saturated yellow with materially higher contrast. The shown/hidden eye likewise has a clearly stronger checked/unchecked distinction through shape fill, colour, and/or contrast, without relying on colour alone.
- request-AC6 -> This backlog slice. Proof: AC6: Eye and favorite actions keep their current click, keyboard, tooltip, accessible-name/state, filtering, and profile-persistence behavior; their state remains unambiguous in normal, hover, focus, and disabled rendering.
- request-AC7 -> This backlog slice. Proof: AC7: Focused offscreen/rendered UI regression tests prove combo trigger contrast, removed-control absence, enlarged fit glyph geometry, one-row containment, simultaneous complete A/B timestamps, absent window/no-sample text, Follow live placement, eye/star state contrast, and preserved graph/signal workflows.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_016_peaklive_compact_graph_controls_and_unmistakable_signal_states`
- Architecture decision(s): (none yet)
- Request: `req_016_compact_peaklive_graph_controls_and_unmistakable_signal_states`
- Primary task(s): `task_017_implement_compact_graph_controls_and_unmistakable_signal_states`

# Priority
- Priority: High - ambiguous selectors and weak shown/favorite states make common configuration and signal-selection actions unreliable.
- Rationale: Set by scaffold input or defaulted for grooming.
