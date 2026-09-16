## item_141_remove_the_redundant_profile_row_and_relocate_bus_state_to_the_workspace_header - Remove the redundant profile row and relocate bus state to the workspace header
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: Medium
> Theme: Workspace ownership and lifecycle status
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-16 15:24:02

# AI Context
- Summary: Remove the redundant profile row and relocate bus state to the workspace header.
- Keywords: remove, redundant, profile, row, relocate, bus, state, workspace, header
- Use when: Implementing or validating the responsive-stop and measurement-workspace follow-up to task_029 and task_030.
- Skip when: Changing unrelated decoding, recording formats, or data retention policies.

# Problem
- The visible AcquisitionBar row remains after configuration moved into menus, but still owns live controls and state wiring.

# Scope
- In:
  - Inventory visible row widgets against existing menu/header equivalents. Put any unique profile selector in Setup as persistent checkable choices; preserve save-as, import/export and recovery through existing appropriate menu/header actions before removing the visible row.
  - Remove the row and its layout allocation; retaining an internal compatibility controller is acceptable if it creates no visible/blank strip.
  - Move the single bus marker and localized status text next to Play/Stop in the shared header and synchronize the same lifecycle source across Graphs, Trace and Report.
  - Preserve profile persistence, setup safety gates, timeout recovery, keyboard access and status messages; test exact-once signal connections after reparenting.
- Out:
  - Duplicating lifecycle state or introducing a second set of independent acquisition controls.
  - Changing profile storage or recording configuration semantics.

# Acceptance criteria
- AC1: The Measurement profile strip is absent and its height is reclaimed for the workspace.
- AC2: Profile selection/save and all previously unique commands remain reachable with their existing persistence and lifecycle gates.
- AC3: One bus status remains visible by Play/Stop in every center view and accurately reflects running, stopping, errors and timeout without relying only on color.

# Findings

## Inventory of the removed row, and where each control went
| Removed from the strip | Where it is now |
| --- | --- |
| Measurement profile selector | Setup > Measurement profile, checkable choices driving the same combo |
| Save setup as | Setup > Save measurement setup as (already there) |
| Channel, bitrate, controller mode | Setup submenus (already there) |
| Load DBC, Open trace, Export | File menu (already there) |
| Play, Stop | Workspace header (already there) and Recording menu |
| Bus indicator | Workspace header, beside Play/Stop |
| Recover acquisition | Workspace header, shown only while the shutdown is timed out |
| Read-only channel summary | The bus indicator's tooltip |

- The `AcquisitionBar` itself survives as a hidden child of the central widget: it stays the single owner of the profile/lifecycle wiring, so nothing gains a second copy that could drift. It is no longer in the root layout, so it claims no height.
- The indicator reads as the state word alone. "Bus" and the read-only channel summary moved to its accessible name and tooltip, which is what let the one-line header keep Play, Stop, Follow live, both fits and the A/B readout at 1024x768.

# AC Traceability
- request-AC5 -> This backlog slice. Proof: AC1: The Measurement profile strip is absent and its height is reclaimed for the workspace.
- request-AC8 -> This backlog slice. Proof: AC2: Profile selection/save and all previously unique commands remain reachable with their existing persistence and lifecycle gates.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_030_peaklive_responsive_stop_and_readable_measurement_controls`
- Architecture decision(s): (none yet)
- Request: `req_032_restore_responsive_acquisition_stop_and_polish_the_measurement_workspace`
- Primary task(s): `task_031_deliver_responsive_stop_and_polished_measurement_workspace_controls`

# Priority
- Priority: Medium - duplicated setup presentation consumes graph space and separates bus state from acquisition controls.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_031_deliver_responsive_stop_and_polished_measurement_workspace_controls`

# Notes
- Task `task_031_deliver_responsive_stop_and_polished_measurement_workspace_controls` was finished via `logics-manager flow finish task` on 2026-09-16.
