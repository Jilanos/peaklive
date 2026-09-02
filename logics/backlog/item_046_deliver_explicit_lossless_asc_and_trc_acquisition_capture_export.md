## item_046_deliver_explicit_lossless_asc_and_trc_acquisition_capture_export - Deliver explicit lossless ASC and TRC acquisition capture export
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Raw capture integrity and interoperability
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: deliver, explicit, lossless, asc, trc, acquisition, capture, export
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Problem
- The current export dialog writes decoded SeriesStore rows to CSV or Parquet only. Its full retained buffer option is not a complete CAN-frame export and can silently differ from the received acquisition.
- ASC recording occurs only through the profile-controlled recorder at acquisition time, is not expressed as a clear save-format choice, and no PCAN-View text TRC capture writer exists.
- A bounded display or signal buffer cannot recreate frames that were not durably captured before filtering, so the product needs a truthful integrity and failure contract.

# Scope
- In:
  - Define distinct decoded-analysis and raw-capture export concepts, labels, help, defaults, and completion/error feedback through i18n.
  - Add profile/session capture-format selection for ASC and documented PCAN-View text TRC, with a writer abstraction that is invoked before presentation projection.
  - Preserve every adapter-delivered frame in source order and implement format-appropriate frame/event representation, atomic completion, rotation, low-space, failure, cancellation, and incomplete-capture handling.
  - Make raw capture availability and integrity state explicit both during and after acquisition; state when no complete capture exists rather than offering a misleading reconstruction.
  - Retain existing CSV/Parquet signal export and make its full-retained-buffer scope unambiguous.
  - Add deterministic unit, service, and headless UI tests for exact ASC/TRC content, counts, ordering, failure states, and current export regressions.
- Out:
  - Retroactive recovery of raw frames absent from a capture that was not enabled at acquisition start.
  - Binary, compressed, proprietary, cloud, scheduled, or network capture destinations.
  - CAN FD, J1939 semantic changes, transmit functionality, or replay-parser scope beyond reading the newly produced interoperable text artifacts.

# Acceptance criteria
- AC1: The UI presents decoded CSV/Parquet export and raw ASC/TRC capture as distinct actions with accurate scope and integrity language.
- AC2: Format selection persists appropriately with the measurement profile and is validated before acquisition begins.
- AC3: ASC and TRC fixture acquisitions prove each input frame is written exactly once, in order, with correct normalized fields and no dependence on bounded UI buffers.
- AC4: Clean, rotated, cancelled, disk-full, worker-failed, and unclean capture states leave truthful final or partial artifacts and actionable UI state.
- AC5: Existing CSV/Parquet tests and all three decoded export scopes retain their documented behavior, with full retained buffer explicitly defined as decoded retained data.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: The UI presents decoded CSV/Parquet export and raw ASC/TRC capture as distinct actions with accurate scope and integrity language.
- request-AC2 -> This backlog slice. Proof: AC2: Format selection persists appropriately with the measurement profile and is validated before acquisition begins.
- request-AC3 -> This backlog slice. Proof: AC3: ASC and TRC fixture acquisitions prove each input frame is written exactly once, in order, with correct normalized fields and no dependence on bounded UI buffers.
- request-AC4 -> This backlog slice. Proof: AC4: Clean, rotated, cancelled, disk-full, worker-failed, and unclean capture states leave truthful final or partial artifacts and actionable UI state.
- request-AC5 -> This backlog slice. Proof: AC5: Existing CSV/Parquet tests and all three decoded export scopes retain their documented behavior, with full retained buffer explicitly defined as decoded retained data.
- request-AC9 -> This backlog slice. Proof: AC5: Existing CSV/Parquet tests and all three decoded export scopes retain their documented behavior, with full retained buffer explicitly defined as decoded retained data.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_012_peaklive_trustworthy_raw_captures_and_universally_reachable_workspace_controls`
- Architecture decision(s): (none yet)
- Request: `req_012_make_peaklive_lossless_capture_export_and_workspace_controls_trustworthy`
- Primary task(s): `task_013_implement_trustworthy_peaklive_capture_exports_and_universally_reachable_controls`

# Priority
- Priority: High - an operator can otherwise mistake bounded decoded exports for complete CAN evidence, risking irreversible loss of acquired frames.
- Rationale: Set by scaffold input or defaulted for grooming.
