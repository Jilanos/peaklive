"""The bounded, non-blocking wind-down of one acquisition generation.

Stop is the one lifecycle step an operator watches, so it is the one that
must never be allowed to block the event loop. Everything here settles in
bounded slices across event-loop turns - the queued live frames, then the
historical writer's own queue - and reports success only once the samples the
session accepted are durably written.
"""

from __future__ import annotations

from time import monotonic

from PySide6.QtCore import QTimer

from peaklive.i18n import translate
from peaklive.services.history_writer import QUEUE_STALL_TIMEOUT_S
from peaklive.services.lifecycle import AcquisitionPhase
from peaklive.ui.session_controller import HISTORY_DRAIN_TIMEOUT_S

SHUTDOWN_TIMEOUT_MS = 5_000
#: How often the wind-down settles one bounded slice of queued live frames.
#: It matches the live presentation cadence, so the event loop paints and
#: accepts input between slices instead of only after all of them.
FINALIZE_POLL_MS = 16


class WorkspaceStopFinalization:
    """Owns Stop, the shutdown bound, and the settle that follows the worker."""

    def _init_stop_finalization(self) -> None:
        self._finalizing_generation: int | None = None
        self._finalizing_total = 0
        self._finalizing_recovered = False
        self._finalizing_deadline = 0.0
        self._finalizing_mark: tuple[int, int] = (0, 0)
        self._finalize_timer = QTimer(self)
        self._finalize_timer.setInterval(FINALIZE_POLL_MS)
        self._finalize_timer.timeout.connect(self._finalize_step)

    def _stop_acquisition(self) -> None:
        """Ask the worker to wind down and put a bound on how long that may take."""
        if self._worker is None or not self._lifecycle.can_stop:
            return
        self._lifecycle.advance(self._lifecycle.generation, AcquisitionPhase.STOPPING)
        self._show_lifecycle_phase()
        self._shutdown_timer.start(self._shutdown_timeout_ms)
        self._worker.request_stop()

    def _acquisition_finished(self, generation: int) -> None:
        """Retire one generation's worker. A stale finish is dropped on the floor."""
        if generation != self._lifecycle.generation:
            return
        self._shutdown_timer.stop()
        self._finalizing_recovered = self._lifecycle.phase is AcquisitionPhase.TIMED_OUT
        self._worker = None
        self._begin_finalization(generation)
        self._show_lifecycle_phase()
        self._finalize_step()

    def _shutdown_timed_out(self) -> None:
        """Refuse to wait any longer for a driver that has not come back."""
        if self._worker is None or self._lifecycle.settled:
            return
        if not self._lifecycle.advance(self._lifecycle.generation, AcquisitionPhase.TIMED_OUT):
            return
        self._end_work()
        self._show_lifecycle_phase()
        self.session_note.show_message(
            translate("acquisition.shutdown_timeout").format(
                seconds=self._shutdown_timeout_ms // 1000
            ),
            "warning",
        )

    # ---- bounded, non-blocking wind-down --------------------------------

    def _presentation_ready(self) -> bool:
        """Whether ingesting another live slice can avoid blocking on persistence.

        `HistoryWriter.submit` is the one place ingestion waits, and it waits
        on the GUI thread. Declining the tick instead leaves the frames in the
        bounded handoff queue - which already applies its own producer-side
        backpressure - so the event loop keeps painting and accepting input
        while the writer catches up.
        """
        writer = self._history_writer
        if writer is None or self._history_failed or writer.has_room():
            self._history_backpressure_since = None
            return True
        now = monotonic()
        if self._history_backpressure_since is None:
            self._history_backpressure_since = now
            return False
        if now - self._history_backpressure_since < QUEUE_STALL_TIMEOUT_S:
            return False
        # The same stall budget `submit()` applies, minus its blocking wait: a
        # writer that has not drained for this long is failed explicitly rather
        # than deferring the presentation queue forever.
        self._history_backpressure_since = None
        self._fail_history(
            translate("trace.history_queue_stalled").format(seconds=int(QUEUE_STALL_TIMEOUT_S))
        )
        return True

    def _begin_finalization(self, generation: int) -> None:
        """Open the post-worker settle: accepted frames out, history durable."""
        self._finalizing_generation = generation
        self._note_finalization_progress()

    def _cancel_finalization(self) -> None:
        self._finalize_timer.stop()
        self._finalizing_generation = None
        self._finalizing_total = 0

    def _note_finalization_progress(self) -> None:
        """Re-arm the stall bound, which measures no progress rather than duration.

        A large session on a slow disk legitimately takes longer than the
        bound to save, and cutting it off would discard history the operator
        accepted. What is never legitimate is making no progress at all, so
        the deadline moves whenever a frame slice or a write batch settles.
        """
        self._finalizing_mark = (self._presentation_queue_depth(), self._history_batches_settled)
        self._finalizing_deadline = monotonic() + HISTORY_DRAIN_TIMEOUT_S

    def _finalize_step(self) -> None:
        """Settle one bounded slice of the wind-down, then yield to the event loop.

        Draining the whole presentation queue inside the `finished` slot was
        the reported freeze: every queued slice cost a full curve repaint and
        could block up to `HistoryWriter`'s whole backpressure budget, with no
        paint or input processed for the duration. One slice per tick costs
        the same total work and keeps the GUI answering throughout, and a
        wind-down with nothing left to settle still finishes in this first
        call rather than waiting out a tick.
        """
        generation = self._finalizing_generation
        if generation is None or generation != self._lifecycle.generation:
            self._cancel_finalization()
            return
        if self._presentation_queue_pending():
            if self._presentation_ready():
                # Uncoalesced, like the live path: each slice projects its own
                # bounded set of rows here rather than leaving one table
                # re-render the size of the whole queue for the final turn.
                self._ingest_frames(self._take_presentation_frames())
        elif self._history_failed or self._history_fully_drained():
            self._complete_finalization(generation)
            return
        self._show_finalization_progress()
        self._finalize_timer.start()
        if (
            self._presentation_queue_depth(),
            self._history_batches_settled,
        ) != self._finalizing_mark:
            self._note_finalization_progress()
            return
        if monotonic() < self._finalizing_deadline:
            return
        self._fail_history(
            translate("trace.history_drain_timeout").format(seconds=int(HISTORY_DRAIN_TIMEOUT_S))
        )
        self._complete_finalization(generation)

    def _complete_finalization(self, generation: int) -> None:
        """Close the wind-down: project what is left, then retire the generation.

        Invalidating the generation stops the live presentation timer, so the
        settled projection is the last one: the final samples stay where the
        operator can read them, and nothing keeps moving the viewport.
        """
        self._cancel_finalization()
        self._settle_presentation()
        self._invalidate_presentation_generation(generation)
        # A stopped session has no future to reserve, so the axis settles on
        # what it actually holds - but only if Follow is still on, because a
        # viewport the operator chose by hand outranks this (item_144).
        self.graph_panel.show_full_extent()
        self._end_work()
        if self._finalizing_recovered:
            self._lifecycle.advance(generation, AcquisitionPhase.STOPPED)
            self.session_note.show_message(translate("acquisition.shutdown_recovered"), "info")
        self._show_lifecycle_phase()

    def _show_finalization_progress(self) -> None:
        """Keep an explicit, honest saving indicator in front of the operator.

        Determinate while a known number of queued frames is still being
        settled, indeterminate while the historical writer drains; never a
        percentage the wind-down has not actually reached, and never removed
        before persistence has genuinely finished.
        """
        pending = self._presentation_queue_depth()
        self.progress.setVisible(True)
        self.progress.setTextVisible(True)
        if pending:
            self._finalizing_total = max(self._finalizing_total, pending)
            self.progress.setRange(0, self._finalizing_total)
            self.progress.setValue(self._finalizing_total - pending)
            self.progress.setFormat(translate("acquisition.finalizing_frames"))
            return
        self.progress.setRange(0, 0)
        self.progress.setFormat(
            translate(
                "acquisition.finalizing_driver"
                if self._worker is not None
                else "acquisition.finalizing_history"
            )
        )
