## req_020_qualify_the_peaklive_ci_windows_executable_with_a_reproducible_functional_test_battery - Qualify the PeakLive CI Windows executable with a reproducible functional test battery
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Windows packaged-executable qualification and release evidence
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-08 14:14:11

# AI Context
- Summary: Defines the binary-first Windows qualification required to turn a CI executable into traceable release evidence without conflating automated local checks and bench-only CAN proof.
- Keywords: qualify, peaklive, windows, executable, reproducible, functional, test, battery
- Use when: Planning, implementing, or reviewing the reusable Windows test battery for a delivered PeakLive executable.
- Skip when: Modifying product functionality without packaging or Windows acceptance scope, or validating a source-run/offscreen build.

# Needs
- Turn the current manual hardware checklist into a repeatable Windows test battery for the CI-produced PeakLive.exe, with a clear split between automated release gates, guided UI checks, and bench-only CAN checks.
- Test the executable as an installed-or-copied Windows artifact, using isolated test data and explicit evidence, rather than inferring Windows behaviour from the Python/offscreen suite.
- Make every observation attributable to the supplied CI build: identifier 0.1.2+b202609071506 and SHA-256 E8E062387148A890AAB7FAE107D2A45F0F38269188CB36D789E7EF0FD28D4C21.
- Provide a developer-owned PowerShell harness, fixtures, result schema, and failure-collection procedure that can be reused for each future CI executable.

# Context
- The deliverable beside this repository is PeakLive.exe with PeakLive.build.txt. It is a self-contained Windows x64 CI artifact, not a source-run validation target.
- Existing proof covers a Linux/offscreen suite and limited PCAN passive runs on Windows 11 at 500 kbit/s. It does not constitute a complete fresh-executable, UI, reconnect, replay, export, profile, display-scale, or uninstall qualification.
- PeakLive is receive-only at the application level. Tests must never introduce frame transmission; normal receive mode is allowed only where controller ACK is safe and passive listen-only is the default bench mode.
- The repository contains representative ASC input, multiple DBCs, prior capture evidence, and the CI build metadata. The campaign must use copies of those assets and never mutate original evidence or a developer's production profile store.
- Hardware, bus topology, active traffic, driver version, and display scaling vary by bench. The harness must report unavailable prerequisites as Not run, not as Pass.

# Acceptance criteria
- AC1: A Windows qualification harness accepts an executable path, build-metadata path, isolated data root, artifact root, and optional hardware profile; it verifies the supplied CI build identifier and SHA-256 before any functional test starts.
- AC2: The automated smoke lane proves on Windows 10/11 x64 that PeakLive.exe starts without a Python installation, stays alive long enough to expose its main window, uses the isolated PEAKLIVE_DATA_DIR, writes structured logs and screenshots on failure, and terminates cleanly.
- AC3: A repeatable UI lane covers initial disconnected state, About/build identity, Help and keyboard shortcuts, window layouts at 1024x768, 1280x720, and 1600x900 at 100/125/150 percent scaling, menus, accessible names, and profile persistence/recovery without connecting to hardware.
- AC4: A fixture lane copies test ASC/TRC and DBC files into its sandbox and verifies replay, filtering, trace/inspector interaction, signal selection/graphs, A/B measurements, report, CSV export, Parquet export, cancellation-safe output, and restart persistence against the packaged executable.
- AC5: A guided PCAN lane validates passive connection at the known bitrate, live trace, recording, stop, adapter unplug/replug, degraded shutdown, recovered partial artifacts, and a sustained high-load recording. It records Windows version, driver version, adapter identity, bitrate, observed counters, and generated evidence paths.
- AC6: The release lane defines explicit pass/fail/not-run rules, per-case timeouts, a machine-readable summary, a human-readable report, log/screenshot/dump collection, and an evidence manifest keyed by executable hash. A missing adapter, inactive bus, or insufficient disk space never yields a false Pass.
- AC7: The implementation adds focused automated coverage for the harness itself and documents one operator command for automated lanes plus one command for the hardware lane. Existing application tests remain unchanged unless a reliable packaged-Windows regression requires a new fixture.
- AC8: The final verification is performed on the supplied CI executable and records the exact completed, failed, skipped, and blocked cases. No release-ready claim is made unless every mandatory non-hardware gate passes and required bench cases have recorded evidence or an explicit operator waiver.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_019_peaklive_windows_executable_qualification_kit`
- Architecture decision(s): (none yet)

# References
- docs/windows-ci-build-under-test.md
- docs/build-identity.md
- docs/windows-hardware-acceptance.md
- README.md
- scripts/build-windows.ps1
- tests
- artifacts/hardware-acceptance
- logics/external
- logics/runbook/run_001_capture_a_peaklive_freeze_with_local_diagnostics.md

# Backlog
- `item_105_create_an_isolated_powershell_qualification_harness_for_a_ci_built_peaklive_executable`
- `item_106_automate_packaged_windows_smoke_identity_ui_and_persisted_workspace_checks`
- `item_107_qualify_replay_dbc_analysis_graph_report_and_export_flows_in_the_packaged_executable`
- `item_108_run_safety_conscious_pcan_live_acquisition_recovery_and_endurance_acceptance`
