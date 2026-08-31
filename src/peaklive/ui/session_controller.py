"""Acquisition, replay, ingestion, and session reporting for the shell."""

from __future__ import annotations

from functools import partial
from pathlib import Path

from PySide6.QtCore import QThread, QTimer
from PySide6.QtWidgets import QFileDialog

from peaklive.analysis import DbcSummary
from peaklive.analysis.profiling import PROFILER, STAGE_REPORT_REFRESH
from peaklive.domain import CanFrame
from peaklive.i18n import translate
from peaklive.services.lifecycle import AcquisitionPhase
from peaklive.services.replay_worker import ReplayWorker
from peaklive.services.worker import AcquisitionWorker

#: How long the shell waits for a worker shutdown before declaring it degraded.
SHUTDOWN_TIMEOUT_MS = 5_000

# A replay batch is deliberately handled on its own event-loop turn.  Qt can
# otherwise dispatch several queued cross-thread signals in one processEvents
# call, making the UI ingest four 512-frame batches before pointer/Stop input.
REPLAY_PRESENTATION_INTERVAL_MS = 1

#: Worker threads the shell has stopped listening to but that are still running.
#:
#: Qt aborts the process if a running QThread is destroyed, so an abandoned
#: worker has to outlive the window that started it. Membership here is the only
#: reference keeping it alive; each worker removes itself when it finally lands.
_ABANDONED_WORKERS: set[QThread] = set()


def abandon_worker(worker: QThread | None) -> None:
    """Stop caring about a worker's result without destroying it mid-flight."""
    if worker is None or worker.isFinished():
        return
    _ABANDONED_WORKERS.add(worker)
    worker.finished.connect(lambda: _ABANDONED_WORKERS.discard(worker))

#: The status line for the phases that own one. Phases absent here are narrated
#: by the worker's own status messages or by an inline session note instead.
_PHASE_STATUS: dict[AcquisitionPhase, str] = {
    AcquisitionPhase.STARTING: "acquisition.opening",
    AcquisitionPhase.STOPPING: "acquisition.stopping",
    AcquisitionPhase.FINALIZING: "acquisition.finalizing",
    AcquisitionPhase.STOPPED: "acquisition.stopped",
}


class WorkspaceSession:
    """Runs one acquisition or replay session and keeps its facts.

    Frames land in three places at once — the bounded trace buffer, the bounded
    series store, and the session facts — so the trace, the plots, and the
    report always describe the same session.
    """

    # ---- acquisition and replay ---------------------------------------

    def _start_acquisition(self) -> None:
        """Open a new acquisition generation, or explain why it is refused."""
        if not self._lifecycle.can_start:
            if self._lifecycle.phase is AcquisitionPhase.TIMED_OUT:
                self.session_note.show_message(translate("acquisition.start_blocked"), "warning")
            return
        generation = self._lifecycle.begin()
        self._reset_session("")
        self._begin_presentation_generation(generation)
        worker = AcquisitionWorker(
            self._adapter_factory(),
            self.selected_profile,
            generation,
            self._queue_acquisition_frames,
        )
        worker.status_changed.connect(self.status.showMessage)
        worker.event_received.connect(self._render_acquisition_event)
        worker.acquisition_failed.connect(self._acquisition_failed)
        worker.phase_changed.connect(partial(self._worker_phase_changed, generation))
        worker.finished.connect(partial(self._acquisition_finished, generation))
        self._worker = worker
        self._show_lifecycle_phase()
        worker.start()

    def _stop_acquisition(self) -> None:
        """Ask the worker to wind down and put a bound on how long that may take."""
        if self._worker is None or not self._lifecycle.can_stop:
            return
        self._lifecycle.advance(self._lifecycle.generation, AcquisitionPhase.STOPPING)
        self._invalidate_presentation_generation(self._lifecycle.generation)
        self._show_lifecycle_phase()
        self._shutdown_timer.start(self._shutdown_timeout_ms)
        self._worker.request_stop()

    def _worker_phase_changed(self, generation: int, phase: str) -> None:
        """Adopt a worker phase, ignoring one from an abandoned generation."""
        if not self._lifecycle.advance(generation, AcquisitionPhase(phase)):
            return
        self._show_lifecycle_phase()

    def _acquisition_failed(self, message: str) -> None:
        self.acquisition_bar.set_bus_state("bus_error")
        self.status.showMessage(translate("acquisition.failed").format(message=message))

    def _acquisition_finished(self, generation: int) -> None:
        """Retire one generation's worker. A stale finish is dropped on the floor."""
        if generation != self._lifecycle.generation:
            return
        recovered = self._lifecycle.phase is AcquisitionPhase.TIMED_OUT
        self._shutdown_timer.stop()
        self._invalidate_presentation_generation(generation)
        self._worker = None
        self._end_work()
        if recovered:
            # The worker was declared degraded and then landed anyway; settle it
            # so Start becomes available again.
            self._lifecycle.advance(generation, AcquisitionPhase.STOPPED)
            self.session_note.show_message(translate("acquisition.shutdown_recovered"), "info")
        self._show_lifecycle_phase()

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

    def _show_lifecycle_phase(self) -> None:
        """Reflect the current phase in the bar, the status line, and progress."""
        phase = self._lifecycle.phase
        self.acquisition_bar.set_lifecycle_phase(phase)
        message = _PHASE_STATUS.get(phase)
        if message is not None:
            self.status.showMessage(translate(message))
        if phase in {AcquisitionPhase.STOPPING, AcquisitionPhase.FINALIZING}:
            self.progress.setVisible(True)
        elif phase is not AcquisitionPhase.RUNNING:
            self._end_work()

    def _choose_trace(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self, translate("trace.open_dialog"), "", translate("trace.open_filter")
        )
        if selected:
            self._open_trace(Path(selected))

    def _open_trace(self, path: Path) -> None:
        previous = self._replay_worker
        if previous is not None and previous.isRunning():
            previous.request_stop()
            abandon_worker(previous)
        self._clear_pending_replay_batches()
        self._pending_replay_finish_generation: int | None = None
        generation = getattr(self, "_replay_generation", 0) + 1
        self._replay_generation = generation
        self._reset_session(path.name)
        self._replay_worker = ReplayWorker(path)
        self._pending_replay_batches: list[tuple[int, ReplayWorker, list[CanFrame]]] = []
        self._replay_presentation_timer = QTimer(self)
        self._replay_presentation_timer.setSingleShot(True)
        self._replay_presentation_timer.setInterval(REPLAY_PRESENTATION_INTERVAL_MS)
        self._replay_presentation_timer.timeout.connect(self._drain_replay_batch)
        self._replay_worker.frames_received.connect(
            partial(self._replay_frames_for_generation, generation, self._replay_worker)
        )
        self._replay_worker.event_received.connect(
            partial(self._replay_event_for_generation, generation)
        )
        self._replay_worker.replay_failed.connect(
            partial(self._replay_failed_for_generation, generation)
        )
        self._replay_worker.progressed.connect(
            partial(self._replay_progressed, generation)
        )
        self._replay_worker.finished.connect(partial(self._replay_finished, generation))
        self._begin_work(translate("trace.opening").format(name=path.name))
        self._replay_worker.start()

    def _replay_event_for_generation(self, generation: int, event: object) -> None:
        if generation == getattr(self, "_replay_generation", 0):
            self._render_replay_event(event)

    def _replay_frames_for_generation(
        self, generation: int, worker: ReplayWorker, frames: list[CanFrame]
    ) -> None:
        if generation != getattr(self, "_replay_generation", 0):
            return
        self._pending_replay_batches.append((generation, worker, frames))
        if not self._replay_presentation_timer.isActive():
            self._replay_presentation_timer.start()

    def _drain_replay_batch(self) -> None:
        """Ingest one worker batch, then yield before accepting the next one."""
        if not self._pending_replay_batches:
            return
        generation, worker, frames = self._pending_replay_batches.pop(0)
        if generation == getattr(self, "_replay_generation", 0):
            self._ingest_frames(frames, coalesce=True)
            self._mark_graphs_dirty()
        # Acknowledge only after this batch was processed: this keeps at most
        # MAX_PENDING_BATCHES in the worker/UI hand-off path.
        worker.batch_rendered()
        if self._pending_replay_batches:
            self._replay_presentation_timer.start()
        elif getattr(self, "_pending_replay_finish_generation", None) == generation:
            self._pending_replay_finish_generation = None
            self._complete_replay(generation)

    def _clear_pending_replay_batches(self) -> None:
        timer = getattr(self, "_replay_presentation_timer", None)
        if timer is not None:
            timer.stop()
        self._pending_replay_batches = []

    def _replay_progressed(self, generation: int, done: int, total: int) -> None:
        """Show determinate parse progress for the current replay only."""
        if generation != getattr(self, "_replay_generation", 0):
            return
        self.progress.setRange(0, total)
        self.progress.setValue(done)

    def _replay_failed_for_generation(self, generation: int, message: str) -> None:
        if generation == getattr(self, "_replay_generation", 0):
            self._acquisition_failed(message)

    def _replay_finished(self, generation: int) -> None:
        if generation != getattr(self, "_replay_generation", 0):
            return
        if self._pending_replay_batches or self._replay_presentation_timer.isActive():
            self._pending_replay_finish_generation = generation
            return
        self._complete_replay(generation)

    def _complete_replay(self, generation: int) -> None:
        """Finalize only after the queued UI projection has consumed every batch."""
        if generation != getattr(self, "_replay_generation", 0):
            return
        self.status.showMessage(translate("trace.replay_done"))
        self._clear_pending_replay_batches()
        self._replay_worker = None
        self._end_work()
        self._settle_presentation()
        # A finished capture is read as a whole, not as its last few seconds.
        self.graph_panel.show_full_extent()
        self._refresh_report()

    def _reset_session(self, source: str) -> None:
        """Clear every retained projection and adopt the new session's axis.

        A named source is a capture, whose extent is whatever it turns out to
        hold; an unnamed one is live acquisition, whose extent starts at zero
        and grows with the session.
        """
        self.session_note.clear_message()
        self.graph_panel.begin_session(live=not source)
        self._cancel_signal_backfill()
        self._series.clear()
        self._trace.clear()
        self._frames.clear()
        self._facts.reset(source)
        self.inspector.clear()
        self.trace_panel.refresh()
        self._sync_graphs()
        self._refresh_report()

    def _begin_work(self, message: str) -> None:
        self.progress.setVisible(True)
        self.status.showMessage(message)

    def _end_work(self) -> None:
        self.progress.setVisible(False)
        self.progress.setRange(0, 0)

    # ---- report --------------------------------------------------------

    def _dbc_summaries(self) -> tuple[DbcSummary, ...]:
        resolutions = self._catalog.resolutions
        summaries = []
        for definition in self._catalog.definitions:
            resolved = tuple(
                arbitration_id
                for arbitration_id, content_hash in resolutions.items()
                if content_hash == definition.content_hash
            )
            summaries.append(
                DbcSummary(
                    definition.path.name,
                    definition.short_hash,
                    self._catalog.is_enabled(definition.content_hash),
                    sum(len(message.signals) for message in definition.database.messages),
                    resolved,
                )
            )
        return tuple(summaries)

    def _refresh_report(self) -> None:
        with PROFILER.stage(STAGE_REPORT_REFRESH):
            self.report_panel.show_report(self._facts.report(self._dbc_summaries()))

    def _export_report(self) -> None:
        self._refresh_report()
        selected, _ = QFileDialog.getSaveFileName(
            self,
            translate("report.export_dialog"),
            "peaklive-report.txt",
            translate("report.export_filter"),
        )
        if not selected:
            return
        path = Path(selected)
        try:
            path.write_text(self.report_panel.text, encoding="utf-8")
        except OSError as error:
            self.report_panel.note.show_message(str(error), "error")
            return
        self.status.showMessage(translate("report.exported").format(name=path.name))
