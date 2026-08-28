## req_007_prevent_ui_freeze_when_stopping_busy_can_acquisition - Prevent the UI from freezing when stopping a busy CAN acquisition
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: A controlled 20,000-frame burst showed unbounded queued UI frame updates delaying Stop from 0.5 s to 7.7 s and starving the UI timer for about 18 s.
> Confidence: 95
> Complexity: M
> Theme: Acquisition responsiveness
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-08-28 09:46:31

# AI Context
- Summary: Preserve lossless acquisition and recording while ensuring a busy bus cannot starve the GUI event loop or delay Stop.
- Keywords: CAN, acquisition, stop, GUI, Qt, queued signals, backpressure, responsiveness
- Use when: A burst of incoming CAN frames makes PeakLive slow or unresponsive during or immediately after Stop.
- Skip when: The failure is an adapter open/close error without a backlog of queued frame-rendering work.

# Priority

High — an active bus can make the desktop application unresponsive for more than 20 seconds, blocking safe operator control.

# Needs
- Keep all received frames durably recorded while bounding presentation work sent to the GUI thread.
- Make Stop actionable promptly on a busy bus and ensure the GUI event loop remains responsive throughout shutdown.
- Prevent obsolete queued visual updates from delaying the terminal lifecycle state after Stop.

# Context
- On the live PCAN-connected system, stopping acquisition left the application unresponsive for at least 20 seconds.
- The acquisition worker emits `frames_received` to the GUI thread for every 64-frame batch. The receiving slot decodes, appends to the trace table, and refreshes graphs synchronously; there is no coalescing or bounded UI-delivery queue.
- A controlled offscreen reproduction with a 20,000-frame burst, without opening physical hardware, requested Stop at 0.5 s. The GUI processed that callback only at 7.7 s, its 10 ms responsiveness timer ticked twice in about 18 s, and the lifecycle remained `stopping`.
- The existing shutdown timeout cannot help while its GUI-thread timer is itself starved by queued rendering events.
- The PCAN driver's native `Uninitialize` call remains a secondary diagnostic risk, but the queued-frame backlog independently reproduces the reported symptom.

# Acceptance criteria
- AC1: Under a deterministic high-rate burst, the GUI processes a Stop request within a bounded interval and continues servicing a responsiveness timer while acquisition stops.
- AC2: Frames handed to the acquisition worker continue to be recorded losslessly; only stale or coalesced presentation work may be dropped or superseded.
- AC3: Once Stop is requested, queued visual frame updates from that generation cannot indefinitely delay the stopped, failed, or degraded lifecycle state.
- AC4: Normal-rate acquisition, display-only filtering, trace selection, graphs, recording, and PCAN adapter semantics remain unchanged.
- AC5: Headless regression coverage reproduces the burst condition and proves the timing bound without requiring connected hardware.

# Scope

In scope: worker-to-GUI frame delivery, lifecycle priority during Stop, and deterministic high-rate regression coverage.

Out of scope: changing CAN bitrate/controller mode, dropping acquired or recorded frames, transmitting frames, and redesigning the workspace.

# Risks and dependencies

- The fix must distinguish lossless capture from a bounded visual projection; UI throttling must never throttle the recorder.
- Qt queued-signal ordering can place a worker's terminal signal behind a large backlog of frame signals.
- Native PCAN shutdown behavior should remain covered by the existing bounded-shutdown tests, but no physical bus is required for the regression.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)

# References
- `src/peaklive/services/worker.py`
- `src/peaklive/ui/session_controller.py`
- `src/peaklive/services/acquisition.py`
- `src/peaklive/adapters/pcan.py`
- `tests/test_ui_lifecycle.py`

# Backlog
- `item_034_prevent_the_ui_from_freezing_when_stopping_a_busy_can_acquisition`
