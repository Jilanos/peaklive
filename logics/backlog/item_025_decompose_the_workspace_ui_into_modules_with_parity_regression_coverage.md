## item_025_decompose_the_workspace_ui_into_modules_with_parity_regression_coverage - Decompose the workspace UI into modules with parity regression coverage
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 95%
> Complexity: High
> Theme: UI architecture
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-25 11:43:05

# AI Context
- Summary: Splits the 863-line src/peaklive/ui/main_window.py into focused panel modules with the main window reduced to composition and wiring, extracts the inline stylesheet into shared tokens, routes every user-visible string through i18n, and pins the delivered req_001 parity behaviors behind a regression suite so the split cannot silently drop them.
- Keywords: ui decomposition, module split, stylesheet tokens, i18n coverage, parity regression suite
- Use when: Moving UI code out of main_window.py, defining the panel module boundaries or stylesheet tokens, extending en.json, or writing the parity regression suite.
- Skip when: Introducing a UI framework, MVVM library or DI container, changing domain models or the adapter and recorder contracts, and adding any transmit capability while restructuring.

# Problem
- src/peaklive/ui/main_window.py holds the top bar, DBC library, signal explorer, graph stack, trace table, inspector, and the inline stylesheet in one 863-line module, and this request adds filtering, columns, measurement, export, report, and feedback on top of it.
- Recent controls carry English string literals rather than i18n keys, so the i18n layer no longer reflects the real UI surface.

# Scope
- In:
  - Split the main window into focused modules covering at minimum the acquisition bar, DBC library, signal explorer, graph stack, trace view, inspector, report, and stylesheet tokens.
  - Reduce the main window to composition, wiring, and profile persistence.
  - Extract the inline stylesheet into a token module shared by every panel.
  - Route every user-visible string through the i18n layer and extend en.json accordingly.
  - Keep the existing domain and service boundaries and the receive-only guarantee unchanged.
  - Add regression coverage that pins the delivered req_001 parity behaviors so the decomposition cannot silently drop them.
  - Update docs/architecture.md and docs/cantracediag-ux-delta.md to describe the resulting module map and the closed delta.
- Out:
  - Introducing a UI framework, MVVM library, or dependency-injection container.
  - Changing the domain models, adapter boundary, or recorder contract.
  - Adding any transmit capability while restructuring.

# Acceptance criteria
- AC1: No single UI module exceeds a stated line budget, and the main window contains composition and wiring only.
- AC2: The stylesheet lives in a token module used by every panel, with no inline stylesheet left in the main window.
- AC3: Every user-visible string resolves through the i18n layer, and en.json covers the full UI surface.
- AC4: A regression suite pins the req_001 parity behaviors and passes before and after the decomposition.
- AC5: The domain boundary test still passes and no transmit path exists anywhere in the UI layer.
- AC6: docs/architecture.md and docs/cantracediag-ux-delta.md describe the module map and record the closed delta with test evidence.

# AC Traceability
- request-AC11 -> This backlog slice. Proof: AC1: No single UI module exceeds a stated line budget, and the main window contains composition and wiring only.
- request-AC12 -> This backlog slice. Proof: AC2: The stylesheet lives in a token module used by every panel, with no inline stylesheet left in the main window.
- request-AC13 -> This backlog slice. Proof: AC3: Every user-visible string resolves through the i18n layer, and en.json covers the full UI surface.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_003_peaklive_analyst_measurement_and_reporting_workspace`
- Architecture decision(s): (none yet)
- Request: `req_002_complete_the_peaklive_analyst_workspace_to_cantracediag_parity`
- Primary task(s): `task_003_deliver_the_peaklive_analyst_workspace_parity_wave`

# Priority
- Priority: High - the monolithic main window is the root cause that makes each parity gap compound.
- Rationale: Set by scaffold input or defaulted for grooming.
