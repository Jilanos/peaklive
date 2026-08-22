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
