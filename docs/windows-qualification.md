# Packaged Windows qualification

The executable-first qualification runner is `scripts/qualify-windows.ps1`.
It verifies the build metadata and SHA-256 before starting PeakLive, creates a
unique artifact root and isolated `PEAKLIVE_DATA_DIR`, runs a bounded process
smoke, and writes `summary.json`, `report.md`, and environment evidence.

From PowerShell at the repository root:

```powershell
.\scripts\qualify-windows.ps1 -Lane automated
.\scripts\qualify-windows.ps1 -Lane ui
.\scripts\qualify-windows.ps1 -Lane fixtures
.\scripts\qualify-windows.ps1 -Lane hardware
.\scripts\qualify-windows.ps1 -Lane all
```

The default executable and build metadata are the CI artifacts colocated with
the checkout (`..\PeakLive.exe` and `..\PeakLive.build.txt`). Override them
for another CI run with `-ExecutablePath` and `-BuildMetadataPath`. A mismatch
is a hard failure; the application is not launched. Each run is keyed by the
binary hash and is isolated below `artifacts/windows-qualification/<run-id>`.

`automated` is the mandatory no-hardware gate. `ui`, `fixtures`, and `hardware`
are guided lanes: each case is recorded as `NotRun` until an operator supplies
the required display, fixture, adapter, active bus, and safety preconditions.
`NotRun` is never converted to `Pass`. Hardware tests default to passive
listen-only and must not transmit frames.

For failures, preserve the complete run directory, `peaklive.log` from the
sandbox, screenshots, and any `.partial` ASC/event-sidecar files. Record the
Windows version, PCAN driver, adapter, channel, bitrate, scaling, and disk
free space alongside the generated manifest. The runner exits non-zero only
for a failed mandatory/automated case or a preflight/runner error.
