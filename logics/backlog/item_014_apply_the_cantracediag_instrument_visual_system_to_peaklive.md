## item_014_apply_the_cantracediag_instrument_visual_system_to_peaklive - Apply the CanTraceDiag instrument visual system to PeakLive
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 95%
> Confidence: 90%
> Progress: 0%
> Complexity: Medium
> Theme: Visual design
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: Applies the CanTraceDiag instrument visual system to PeakLive with Qt-appropriate tokens, dense data typography, compact controls, and polished states.
- Keywords: apply, cantracediag, instrument, visual, system, peaklive
- Use when: Styling the refined PeakLive workspace, introducing design tokens, polishing state visuals, or aligning data-heavy UI with the CanTraceDiag instrument language.
- Skip when: Implementing functional DBC, acquisition, signal, or plotting behavior without changing the visual system.

# Problem
- PeakLive's current visual shell is functional but less finished than CanTraceDiag's validated instrument-style interface.
- A superficial color update would not deliver the precision, density, and state semantics operators expect.

# Scope
- In:
  - Translate the CanTraceDiag instrument visual language into Qt styling: dark scope surface, compact panels, hairline borders, small radii, data-mono typography, semantic status colors, and channel swatches.
  - Introduce reusable style tokens or constants instead of scattering hard-coded colors.
  - Polish loading, empty, warning, error, selected, disabled, and active states across DBC library, acquisition setup, signal explorer, trace, plots, and inspector.
  - Keep UI dense and operational, not marketing-like, and avoid decorative gradients or oversized hero-style composition.
  - Add focused UI smoke checks for text fit, panel visibility, accessible names, and key state classes/properties.
- Out:
  - Changing the product brand, icon, installer artwork, or non-workspace marketing assets.
  - Adding a light theme.
  - Using web CSS directly instead of an appropriate Qt stylesheet/design token implementation.

# Acceptance criteria
- AC1: The workspace uses a coherent instrument-style visual system aligned with the CanTraceDiag reference while remaining native to Qt.
- AC2: Data-heavy elements use monospaced/tabular presentation where practical and semantic colors are not the only status signal.
- AC3: Empty, loading, parse error, hardware error, conflict, selected, favorite, and shown states are visually distinct and accessible.
- AC4: UI tests or screenshots verify no obvious overlap or text clipping in the primary desktop workspace states.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: The workspace uses a coherent instrument-style visual system aligned with the CanTraceDiag reference while remaining native to Qt.
- request-AC7 -> This backlog slice. Proof: AC2: Data-heavy elements use monospaced/tabular presentation where practical and semantic colors are not the only status signal.
- request-AC8 -> This backlog slice. Proof: AC3: Empty, loading, parse error, hardware error, conflict, selected, favorite, and shown states are visually distinct and accessible.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_002_peaklive_cantracediag_grade_diagnostic_workspace`
- Architecture decision(s): (none yet)
- Request: `req_001_bring_peaklive_ux_to_cantracediag_parity`
- Primary task(s): `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta`

# Priority
- Priority: Medium - visual polish should land after the main interaction surfaces are known.
- Rationale: Set by scaffold input or defaulted for grooming.
