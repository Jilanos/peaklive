"""Acquisition, replay, ingestion, and session reporting for the shell."""
from __future__ import annotations  # noqa: I001
from functools import partial
from pathlib import Path
from time import monotonic
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFileDialog
from peaklive.analysis import DbcSummary
from peaklive.analysis.profiling import PROFILER, STAGE_REPORT_REFRESH
from peaklive.i18n import translate
from peaklive.services.lifecycle import AcquisitionPhase
from peaklive.services.replay_worker import ReplayWorker
from peaklive.services.worker import AcquisitionWorker
from peaklive.ui.worker_lifecycle import abandon_worker
SHUTDOWN_TIMEOUT_MS = 5_000
#: How often to re-check whether the background history writer has drained
#: while finalizing a completed replay.
HISTORY_DRAIN_POLL_MS = 20
#: Bound on how long that finalization waits before giving up rather than
#: polling forever - a working writer with a bounded queue and no ingestion
#: still adding to it drains in a handful of ticks; anything this slow is
#: itself worth surfacing rather than silently never finishing.
HISTORY_DRAIN_TIMEOUT_S = 30.0
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
    def _start_acquisition(self) -> None:
        """Open a new acquisition generation, or explain why it is refused."""
        if self._replay_worker is not None and self._replay_worker.isRunning():
            self.session_note.show_message(
                translate("acquisition.start_blocked_by_replay"), "warning"
            )
            return
        if not self._lifecycle.can_start:
            if self._lifecycle.phase is AcquisitionPhase.TIMED_OUT:
                self.session_note.show_message(translate("acquisition.start_blocked"), "warning")
            return
        generation = self._lifecycle.begin()
        self._reset_session("")
        self._begin_presentation_generation(generation)
        worker = AcquisitionWorker(
            self._adapter_factory(),
            self.selected_profile.duplicate(self.selected_profile.name),
            generation,
            self._queue_acquisition_frames,
        )
        worker.status_changed.connect(self.status.showMessage)
        worker.event_received.connect(self._render_acquisition_event)
        worker.acquisition_failed.connect(self._acquisition_failed)
        worker.recording_reserved.connect(self._recording_reserved)
        worker.phase_changed.connect(partial(self._worker_phase_changed, generation))
        worker.finished.connect(partial(self._acquisition_finished, generation))
        self._worker = worker
        self._show_lifecycle_phase()
        worker.start()
    def _recording_reserved(self, next_iteration: int) -> None:
        """Persist the next collision-safe iteration the worker just claimed.
        The worker reserved against its own profile snapshot, not the shared
        one the UI edits, so the advanced count is applied here - on the UI
        thread, to the real profile - before the ordinary save path persists it.
        """
        self.selected_profile.recording.iteration = next_iteration
        self._save()
    def _recover_timed_out_acquisition(self) -> None:
        """Abandon a stuck generation and start with a fresh adapter instance."""
        if self._lifecycle.phase is not AcquisitionPhase.TIMED_OUT:
            return
        previous = self._worker
        if previous is not None:
            previous.request_stop()
            abandon_worker(previous)
        self._worker = None
        self._lifecycle.recover_timed_out()
        self.session_note.show_message(translate("acquisition.recovering_driver"), "warning")
        self._show_lifecycle_phase()
        self._start_acquisition()
    def _stop_acquisition(self) -> None:
        """Ask the worker to wind down and put a bound on how long that may take."""
        if self._worker is None or not self._lifecycle.can_stop:
            return
        self._lifecycle.advance(self._lifecycle.generation, AcquisitionPhase.STOPPING)
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
    def _acquisition_history_failed(self, message: str) -> None:
        """Wind live acquisition down after historical persistence failed once.

        `_fail_history` already showed the detailed session note; this stops
        the worker so it is not left recording into a store that just proved
        it cannot persist samples.
        """
        self._acquisition_failed(message)
        self._stop_acquisition()
    def _acquisition_finished(self, generation: int) -> None:
        """Retire one generation's worker. A stale finish is dropped on the floor."""
        if generation != self._lifecycle.generation:
            return
        recovered = self._lifecycle.phase is AcquisitionPhase.TIMED_OUT
        self._shutdown_timer.stop()
        self._settle_acquisition_generation(generation)
        self._invalidate_presentation_generation(generation)
        self._worker = None
        self._end_work()
        if recovered:
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
        self._sync_setup_menu_enabled()
        message = _PHASE_STATUS.get(phase)
        if message is not None:
            self.status.showMessage(translate(message))
        if phase in {AcquisitionPhase.STOPPING, AcquisitionPhase.FINALIZING}:
            self.progress.setVisible(True)
        elif phase is not AcquisitionPhase.RUNNING:
            self._end_work()
        self._update_mode_availability()
    def _settle_acquisition_generation(self, generation: int) -> None:
        del generation
        while self._presentation_queue_pending():
            self._drain_presentation_frames()
    def _update_mode_availability(self) -> None:
        """Grey out Start and Open Trace while the other session mode is running.
        Live and replay must never ingest into the same buffers at once,
        so the action that would start the mode not already running is
        disabled outright rather than relying only on the runtime refusal.
        """
        replay_active = self._replay_worker is not None and self._replay_worker.isRunning()
        acquisition_active = self._worker is not None and self._worker.isRunning()
        self.start_action.setEnabled(not replay_active)
        self.stop_action.setEnabled(acquisition_active)
        self.open_trace_action.setEnabled(not acquisition_active)
    def _choose_trace(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self, translate("trace.open_dialog"), "", translate("trace.open_filter")
        )
        if selected:
            self._open_trace(Path(selected))
    def _open_trace(self, path: Path) -> None:
        if self._worker is not None and self._worker.isRunning():
            self.session_note.show_message(
                translate("trace.open_blocked_by_acquisition"), "warning"
            )
            return
        previous = self._replay_worker
        if previous is not None and previous.isRunning():
            previous.request_stop()
            abandon_worker(previous)
        self._clear_pending_replay_batches()
        generation = self._replay_generation + 1
        self._replay_generation = generation
        self._reset_session(path.name)
        self._replay_source_path = path
        self._replay_worker = ReplayWorker(path)
        self._pending_replay_batches = []
        self._replay_source_completed_generation = None
        self._replay_worker.records_received.connect(
            partial(self._replay_records_for_generation, generation, self._replay_worker)
        )
        self._replay_worker.replay_failed.connect(
            partial(self._replay_failed_for_generation, generation)
        )
        self._replay_worker.replay_completed.connect(
            partial(self._replay_completed_for_generation, generation)
        )
        self._replay_worker.progressed.connect(partial(self._replay_progressed, generation))
        self._replay_worker.finished.connect(partial(self._replay_finished, generation))
        self._begin_work(translate("trace.opening").format(name=path.name))
        self._replay_worker.start()
        self._update_mode_availability()
    def _replay_records_for_generation(
        self, generation: int, worker: ReplayWorker, records: list[object]
    ) -> None:
        if generation != getattr(self, "_replay_generation", 0):
            return
        self._pending_replay_batches.append((generation, worker, records))
        if not self._replay_presentation_timer.isActive():
            self._replay_presentation_timer.start()
    def _drain_replay_batch(self) -> None:
        """Ingest one worker batch, then yield before accepting the next one.

        A historical-persistence failure discovered while ingesting (either
        synchronously, or asynchronously once the background writer reports
        it) is handled entirely inside `_fail_history`: it stops and abandons
        the worker and routes through `_replay_failed_for_generation` itself,
        which also empties `_pending_replay_batches`. So by the time this
        resumes below, a fresh failure already looks like an ordinary empty,
        not-yet-succeeded queue - `_replay_ready_to_complete` correctly
        declines to complete it.
        """
        if not self._pending_replay_batches:
            return
        generation, worker, records = self._pending_replay_batches.pop(0)
        if generation == getattr(self, "_replay_generation", 0):
            self._ingest_replay_records(records)
        worker.batch_rendered()
        if self._pending_replay_batches:
            self._replay_presentation_timer.start()
        elif self._replay_ready_to_complete(generation, worker):
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
    def _replay_completed_for_generation(self, generation: int) -> None:
        if generation != getattr(self, "_replay_generation", 0):
            return
        self._replay_source_completed_generation = generation
        if self._pending_replay_batches or self._replay_presentation_timer.isActive():
            return
        self._complete_replay(generation)
    def _replay_ready_to_complete(self, generation: int, worker: ReplayWorker) -> bool:
        if generation != getattr(self, "_replay_generation", 0):
            return False
        if self._pending_replay_batches or self._replay_presentation_timer.isActive():
            return False
        if getattr(self, "_replay_source_completed_generation", None) == generation:
            return True
        return worker.succeeded and worker.pending_batch_count == 0
    def _replay_failed_for_generation(self, generation: int, message: str) -> None:
        if generation != getattr(self, "_replay_generation", 0):
            return
        if getattr(self, "_replay_failed_generation", None) == generation:
            # Already failed once (e.g. a history-persistence failure that
            # then requested the worker stop): a cancellation notice cascading
            # from that request-to-stop must not overwrite the real cause.
            return
        self._replay_failed_generation = generation
        self.acquisition_bar.set_bus_state("stopped")
        self.status.showMessage(translate("trace.replay_failed").format(message=message))
        self._clear_pending_replay_batches()
        self._replay_source_completed_generation = None
        self._replay_worker = None
        self._end_work()
        self._update_mode_availability()
    def _replay_finished(self, generation: int) -> None:
        if generation != getattr(self, "_replay_generation", 0):
            return
        if getattr(self, "_replay_failed_generation", None) == generation:
            return
        worker = self._replay_worker
        if worker is not None and not worker.succeeded:
            self._replay_failed_generation = generation
            self._end_work()
            self._update_mode_availability()
        elif worker is not None:
            QTimer.singleShot(0, partial(self._complete_replay_if_ready, generation, worker))
    def _complete_replay_if_ready(self, generation: int, worker: ReplayWorker) -> None:
        if self._replay_ready_to_complete(generation, worker):
            self._complete_replay(generation)
    def _complete_replay(self, generation: int) -> None:
        """Finalize decoding, then wait for the background writer to settle."""
        if generation != getattr(self, "_replay_generation", 0):
            return
        self.status.showMessage(translate("trace.replay_done"))
        self._clear_pending_replay_batches()
        self._replay_worker = None
        self._end_work()
        self._update_mode_availability()
        self._settle_presentation()
        # The report reads in-memory facts, not SQL, so it is accurate now;
        # only the historical view/full extent wait for the writer below.
        self._refresh_report()
        self._finish_historical_readiness(generation)
    def _finish_historical_readiness(self, generation: int, deadline: float | None = None) -> None:
        if generation != getattr(self, "_replay_generation", 0):
            return
        if self._history_writer is None:
            return  # window closed/shut down since this was scheduled
        if self._history_failed:
            # _fail_history already reacted; there is nothing left to settle.
            return
        if deadline is None:
            deadline = monotonic() + HISTORY_DRAIN_TIMEOUT_S
        if not self._history_fully_drained():
            if monotonic() >= deadline:
                self._fail_history(
                    translate("trace.history_drain_timeout").format(
                        seconds=int(HISTORY_DRAIN_TIMEOUT_S)
                    )
                )
                return
            QTimer.singleShot(
                HISTORY_DRAIN_POLL_MS,
                partial(self._finish_historical_readiness, generation, deadline),
            )
            return
        self._set_historical_view_ready(True)
        self.graph_panel.show_full_extent()
    def _reset_session(self, source: str) -> None:
        """Clear every retained projection and adopt the new session's axis.
        A named source is a capture, whose extent is whatever it turns out to
        hold; an unnamed one is live acquisition, whose extent starts at zero
        and grows with the session.
        """
        self.session_note.clear_message()
        if not source:
            self._replay_source_path = None
        self.graph_panel.cancel_history_refresh()
        self.graph_panel.begin_session(live=not source)
        self._cancel_signal_backfill()
        self._reported_dbc_conflicts.clear()
        self._series.clear()
        self._trace.clear()
        self._frames.clear()
        self._reset_history_store()
        self._historical_view_ready = False
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
    def _dbc_summaries(self) -> tuple[DbcSummary, ...]:
        resolutions = self._catalog.resolutions
        summaries = []
        for definition in self._catalog.definitions:
            resolved = tuple(
                frame_key
                for frame_key, content_hash in resolutions.items()
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
