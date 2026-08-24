## item_012_bring_the_signal_explorer_to_cantracediag_parity - Bring the signal explorer to CanTraceDiag parity
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 95%
> Confidence: 90%
> Progress: 70%
> Complexity: High
> Theme: Signal explorer UX
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-08-24 14:35:25

# AI Context
- Summary: Reworks the signal panel into a CanTraceDiag-style DBC/message-grouped explorer with search, favorites, shown filtering, and clickable plot selection.
- Keywords: bring, signal, explorer, cantracediag, parity
- Use when: Implementing signal grouping, dense catalog navigation, favorites, shown/displayed filters, signal add/remove interactions, or explorer persistence.
- Skip when: Changing DBC parsing semantics, acquisition hardware modes, graph cursor mechanics, or visual tokens outside the signal explorer surface.

# Problem
- PeakLive's current signal list is flat and cannot efficiently navigate a dense multi-DBC catalog.
- Operators expect CanTraceDiag-style DBC grouping, favorites, shown filters, and clickable signal rows.

# Scope
- In:
  - Group signals under their original DBC, with message-level grouping where it improves dense navigation.
  - Provide dropdown or searchable navigation for large catalogs and keep active/relevant DBCs easy to reach.
  - Add favorites and shown/displayed filters that intersect with text search.
  - Make signal rows clickable to add/remove plotted signals and show channel/color assignment.
  - Keep selected signals visible under the shown filter even when their DBC group is collapsed.
  - Persist favorites, shown signals, expansion state, and selected plotted signals in the profile.
- Out:
  - Changing the decoder's semantic interpretation of DBC signals.
  - Deleting a DBC from disk when removed from the UI library.
  - Creating a mobile-only UI separate from the desktop workspace.

# Acceptance criteria
- AC1: Signals are grouped by original DBC and message, with accessible expand/collapse state.
- AC2: Favorites, shown-only, and text filters combine predictably and produce a clear empty state.
- AC3: Clicking a signal adds/removes it from plots without disrupting unrelated signals, favorites, or DBC state.
- AC4: The explorer remains compact with at least six imported DBCs and no horizontal overflow at supported desktop sizes.
- AC5: Tests cover grouping, dropdown/search navigation, favorites, shown filtering, signal add/remove, and persistence.

# AC Traceability
- request-AC4 -> This backlog slice. Proof: AC1: Signals are grouped by original DBC and message, with accessible expand/collapse state.
- request-AC6 -> This backlog slice. Proof: AC2: Favorites, shown-only, and text filters combine predictably and produce a clear empty state.
- request-AC7 -> This backlog slice. Proof: AC3: Clicking a signal adds/removes it from plots without disrupting unrelated signals, favorites, or DBC state.
- request-AC8 -> This backlog slice. Proof: AC4: The explorer remains compact with at least six imported DBCs and no horizontal overflow at supported desktop sizes.
- request-AC9 -> This backlog slice. Proof: AC5: Tests cover grouping, dropdown/search navigation, favorites, shown filtering, signal add/remove, and persistence.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_002_peaklive_cantracediag_grade_diagnostic_workspace`
- Architecture decision(s): (none yet)
- Request: `req_001_bring_peaklive_ux_to_cantracediag_parity`
- Primary task(s): `task_002_deliver_the_peaklive_cantracediag_ux_parity_delta`

# Priority
- Priority: High - signal navigation drives DBC, plot, and inspector usefulness.
- Rationale: Set by scaffold input or defaulted for grooming.
