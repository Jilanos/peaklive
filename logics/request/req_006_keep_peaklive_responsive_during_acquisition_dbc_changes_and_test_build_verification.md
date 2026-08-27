## req_006_keep_peaklive_responsive_during_acquisition_dbc_changes_and_test_build_verification - Keep PeakLive responsive during acquisition, DBC changes, and test-build verification
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Responsive runtime reliability and build identity
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.

# AI Context
- Summary: (unfilled: replace before this doc is used)
- Keywords: peaklive, responsive, during, acquisition, dbc, changes, test, build, verification
- Use when: (unfilled: replace before this doc is used)
- Skip when: (unfilled: replace before this doc is used)

# Needs
- Keep the desktop application interactive while an acquisition starts or stops, including when the CAN driver open or close operation is slow or does not return promptly.
- Prevent DBC additions, removals, enablement changes, parsing, catalog refreshes, and dependent workspace updates from making the Windows application appear unresponsive.
- Provide a discreet, trustworthy in-application version identifier so an operator can confirm which packaged executable is under test.

# Context
- PeakLive is a PySide6 Windows desktop CAN workstation. Acquisition runs in AcquisitionWorker, while the current worker finally block calls adapter disconnect and recording finalization before emitting its finished signal.
- The UI currently asks a worker to stop without a bounded completion contract; window close waits briefly for active workers. A driver call that blocks indefinitely can therefore leave the application unable to reach a clean usable state.
- DBC loading, parsing, catalog mutation, profile persistence, and panel/explorer/graph refresh currently execute synchronously from the UI path. Large, malformed, slow-network, or repeated DBC operations can starve event processing.
- The canonical package version is currently declared in pyproject.toml and duplicated in peaklive.__version__; the PyInstaller executable is named PeakLive without an operator-facing build identity.
- The product must preserve complete recording semantics, receive-only CAN behavior, deterministic DBC conflict handling, and profile persistence while introducing responsive lifecycle boundaries.
- The delivery must be testable headlessly with fake or controllably blocking adapters and synthetic DBC fixtures, plus a documented Windows packaged-executable smoke check.

# Acceptance criteria
- AC1: Starting acquisition immediately gives visible in-progress feedback and keeps the Qt event loop responsive; a slow, failed, or blocking adapter connect cannot freeze the window or require force-closing the application.
- AC2: Stopping acquisition immediately gives visible stopping feedback and keeps the Qt event loop responsive while receive, driver disconnect, recorder flush, and finalization complete; the normal success path completes exactly once and restores usable controls.
- AC3: If shutdown cannot complete within a documented bounded interval, the UI exposes an actionable degraded or timed-out state, preserves recoverable recording evidence, avoids an unbounded UI-thread wait, and permits a safe user-controlled next action or application exit.
- AC4: Repeated Start/Stop activation, close-window during each lifecycle phase, connect failure, receive failure, disconnect failure, and recording finalization failure have deterministic state transitions with no orphan worker, duplicate finalization, crash, or permanently disabled controls.
- AC5: Adding one or more DBC files, removing a DBC, enabling or disabling a DBC, resolving conflicts, and rebuilding affected signal/graph views do not block the UI event loop; progress, cancellation where work has not committed, and per-file errors are visible.
- AC6: DBC operations preserve atomic observable state: an unsuccessful, cancelled, or stale asynchronous operation does not partially corrupt the catalog, persisted profile paths, selected signals, conflicts, or rendered workspace; deterministic ordering and existing decode behavior remain intact.
- AC7: Focused automated tests reproduce deliberately slow and failing adapter/DBC operations, assert that UI events continue to be processed, and cover lifecycle timeout/recovery, repeated actions, cancellation, and catalog consistency.
- AC8: The application displays a subtle but readable version/build identifier in a stable UI location and in About information; it is available without a network connection and does not obstruct normal diagnostic work.
- AC9: The displayed identifier comes from one authoritative build-version source, is consistent with package metadata and the Windows packaged executable, and distinguishes rebuilds intended for operator testing according to the documented release/build convention.
- AC10: Automated tests and a packaged Windows smoke procedure verify the visible version/build identifier and record which executable was tested.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_006_peaklive_responsive_runtime_and_identifiable_builds`
- Architecture decision(s): (none yet)

# References
- src/peaklive/services/worker.py
- src/peaklive/services/acquisition.py
- src/peaklive/ui/session_controller.py
- src/peaklive/ui/catalog_controller.py
- src/peaklive/ui/panels/dbc_library.py
- src/peaklive/ui/main_window.py
- src/peaklive/__init__.py
- src/peaklive/app.py
- pyproject.toml
- peaklive.spec
- tests/test_worker.py
- tests/test_ui.py
- tests/test_pcan_adapter.py

# Backlog
- `item_030_make_acquisition_lifecycle_operations_responsive_and_bounded`
- `item_031_move_dbc_catalog_mutations_off_the_ui_critical_path`
- `item_032_expose_a_trustworthy_in_application_build_identifier`
