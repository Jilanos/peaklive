## run_001_capture_a_peaklive_freeze_with_local_diagnostics - Capture a PeakLive freeze with local diagnostics
> Status: Draft
> Category: other
> Verified: (not yet verified)
> Related request: (none yet)
> Related backlog: (none yet)
> Related task: `task_012_deliver_a_freeze_free_self_diagnosing_peaklive_runtime`
> Reminder: Update status, category, verification, and linked refs when you edit this doc.

# Trigger
- PeakLive is unresponsive, an acquisition remains in degraded shutdown, or a UI action appears to have done nothing.

# Prerequisites
- Access to the operator account that ran PeakLive.
- The console-enabled bench build (`pyinstaller --console --name PeakLive-bench src/peaklive/app.py`) when reproducing a suspected exception.
- `py-spy` installed on the bench machine for a live process capture.

# Procedure
- Find the local log at `%LOCALAPPDATA%/PeakLive/peaklive.log`; when `PEAKLIVE_DATA_DIR` is set, use `peaklive.log` in that directory instead.
- Preserve the log and any `.partial` ASC or event-sidecar files before restarting the application.
- For a live freeze, run `py-spy dump --pid <peaklive-pid>` followed by `py-spy record --pid <peaklive-pid> --duration 15 --format speedscope -o peaklive-freeze.json`.
- If acquisition shows **Recover acquisition**, use it only to open a fresh adapter generation. The prior driver handle can remain held until its blocked call returns.
- Attach the log excerpt, py-spy output, build identifier, and capture artifacts to the investigation.

# Verification
- The log contains the session start and build identifier. An unhandled process or worker exception includes its traceback.
- The preserved recording is either a finalized ASC plus JSONL sidecar or explicitly retains its `.partial` suffix.

# Rollback
- (optional: describe how to undo this procedure)

# References
- Related request: (none yet)
- Related backlog: (none yet)
- Related task: `task_012_deliver_a_freeze_free_self_diagnosing_peaklive_runtime`
