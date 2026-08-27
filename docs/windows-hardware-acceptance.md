# Windows Hardware Acceptance

Run this on a Windows 10/11 x64 workstation with the supported USB CAN driver
installed and a known active Classic CAN bus.

1. Run `scripts/build-windows.ps1` from PowerShell.
2. Start `dist/PeakLive.exe`; verify it opens without a Python installation.
3. Confirm the last measurement profile is displayed and the bus remains
   disconnected.
4. Select the adapter and a known bitrate, then start in passive listen-only
   mode. Verify incoming frames without a transmit action.
5. Repeat in normal receive mode only on a bus where controller ACK is safe.
6. Disconnect and reconnect the USB adapter while acquisition is active.
   Confirm visible events and a recoverable capture discontinuity.
7. Record for 60 minutes at the highest practical bus load. Check ASC segment
   rotation, event sidecars, recorder high-water mark, and absence of recorder
   overflow.
8. Open the resulting ASC and a representative TRC file. Load DBCs, inspect a
   decoded signal, and export CSV and Parquet.
9. Uninstall the test build and confirm captures/settings follow the documented
   retention policy.

Record Windows version, adapter driver version, bus bitrate, profile name,
capture paths, and any driver loss in the release evidence.

## Lifecycle acceptance on real hardware

The offscreen suite proves these paths against controllably blocking fakes.
Repeat them once against the real driver, because only the driver can produce a
genuinely unbounded call.

10. Start acquisition and confirm the bus indicator moves Connecting → Running
    while the window stays interactive throughout.
11. Stop acquisition and confirm the indicator shows Stopping, the progress
    strip appears, and the window remains interactive until it reaches Stopped.
12. Activate Start several times in quick succession, then Stop several times.
    Confirm exactly one acquisition runs and the controls never latch disabled.
13. Unplug the USB adapter mid-acquisition, then press Stop. If the driver does
    not return within the bounded interval (5 s by default), confirm the bus
    indicator reads *Shutdown degraded*, an explanatory note appears, the window
    still responds, and Start stays disabled.
14. In that degraded state, confirm the capture directory holds `.asc.partial`
    and `.peaklive-events.jsonl.partial` segments containing the frames received
    before the block. Close PeakLive and confirm it exits without a force-quit.
15. Close the window while an acquisition is running. Confirm the application
    exits within the bounded interval and leaves either a finalized `.asc` or a
    recoverable `.partial` pair.

Record, for each step, the observed indicator text, whether the window stayed
interactive, and the capture files left behind.

## Recorded preflight evidence

On 2026-08-22, the Windows runtime detected `PCAN_USBBUS1` as a Classic USB
adapter without CAN FD support. Opening and closing a passive 500 kbit/s
connection succeeded. A five-second passive receive probe observed zero frames,
so a connected active bus at its known bitrate is still required for the
load/reconnect and recording portions of this checklist.

On 2026-08-24, Windows 11 Pro 10.0.26200 detected `PCAN-USB`
(`USB\VID_0C72&PID_000C\5&21802C3&0&3`) with driver `5.1.2.20099`.
Passive probes on `PCAN_USBBUS1` showed error frames at 125, 250, and
1000 kbit/s, and valid traffic at 500 kbit/s. A 60-second passive
PeakLive acquisition at 500 kbit/s recorded 47,424 frames with clean
connect/disconnect events and no error frames in the acceptance probe.
Evidence is stored in
`artifacts/hardware-acceptance/20260824-113926-pcan-passive-500k/`.

Later on 2026-08-24, a corrected Windows hardware probe confirmed that wrong
bitrate PCAN driver error frames are surfaced as `driver_overrun` or
`error_frame` events instead of data frames. A follow-up 500 kbit/s passive
recording run was stopped by operator decision after battery constraints; it
had reached 708,245 received frames and no driver events at the last progress
update. The full 60-minute acceptance run is deferred by operator decision and
is not required for this task closeout.
