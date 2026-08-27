"""Acquisition, replay, ingestion, and session reporting for the shell."""

from __future__ import annotations

from functools import partial
from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from peaklive.analysis import (
    DECODE_CONFLICT,
    DECODE_DECODED,
    DECODE_UNKNOWN,
    AmbiguousMessageError,
    DbcSummary,
)
from peaklive.domain import BusEvent, CanFrame
from peaklive.i18n import translate
from peaklive.services.lifecycle import AcquisitionPhase
from peaklive.services.replay_worker import ReplayWorker
from peaklive.services.worker import AcquisitionWorker
from peaklive.ui.panels.graph_stack import RAW_PREVIEW

#: How long the shell waits for a worker shutdown before declaring it degraded.
SHUTDOWN_TIMEOUT_MS = 5_000

#: Workers the shell has stopped listening to but that are still running.
#:
#: Qt aborts the process if a running QThread is destroyed, so an abandoned
#: worker has to outlive the window that started it. Membership here is the only
#: reference keeping it alive; each worker removes itself when it finally lands.
_ABANDONED_WORKERS: set[AcquisitionWorker] = set()


def abandon_worker(worker: AcquisitionWorker) -> None:
    """Stop caring about a worker's result without destroying it mid-flight."""
    if worker.isFinished():
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
        worker = AcquisitionWorker(self._adapter_factory(), self.selected_profile, generation)
        worker.frames_received.connect(self._render_frames)
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
        if self._replay_worker is not None and self._replay_worker.isRunning():
            self._replay_worker.request_stop()
            self._replay_worker.wait(1_000)
        self._reset_session(path.name)
        self._replay_worker = ReplayWorker(path)
        self._replay_worker.frames_received.connect(self._render_frames)
        self._replay_worker.event_received.connect(self._render_replay_event)
        self._replay_worker.replay_failed.connect(self._acquisition_failed)
        self._replay_worker.finished.connect(self._replay_finished)
        self._begin_work(translate("trace.opening").format(name=path.name))
        self._replay_worker.start()

    def _replay_finished(self) -> None:
        self.status.showMessage(translate("trace.replay_done"))
        self._replay_worker = None
        self._end_work()
        self._refresh_report()

    def _reset_session(self, source: str) -> None:
        self.session_note.clear_message()
        self._series.clear()
        self._trace.clear()
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

    # ---- ingestion -----------------------------------------------------

    def _render_frames(self, frames: list[CanFrame]) -> None:
        if frames:
            self.acquisition_bar.set_bus_state("running")
        added = []
        for frame in frames:
            signals, status = self._decode(frame)
            message_name = signals[0].message_name if signals else ""
            added.append(
                self._trace.add_frame(
                    frame,
                    message_name=message_name,
                    decode_status=status,
                    signals=signals,
                )
            )
            self._facts.record_frame(frame, decoded=status == DECODE_DECODED)
            for signal in signals:
                key = f"{signal.message_name}.{signal.signal_name}"
                if key in self._selected_signal_names:
                    self._series.append(key, frame.timestamp, signal.value, signal.unit)
            if not self._selected_signal_names and frame.data:
                self._series.append(RAW_PREVIEW, frame.timestamp, float(frame.data[0]))
        self.trace_panel.append_records(added)
        self.graph_panel.refresh_data()

    def _render_acquisition_event(self, event: object) -> None:
        if not isinstance(event, BusEvent):
            return
        record = self._trace.add_event(event)
        self._facts.record_event(event)
        if event.kind == "recording_warning":
            # A disk warning must outlive the next incoming frame.
            self.session_note.show_message(event.message, "warning")
        if event.kind in {"error_frame", "bus_error"}:
            self.acquisition_bar.set_bus_state("bus_error")
        elif event.kind == "bus_off":
            self.acquisition_bar.set_bus_state("bus_off")
        elif event.kind == "reconnecting":
            self.acquisition_bar.set_bus_state("reconnecting")
        self.trace_panel.append_records([record])

    def _render_replay_event(self, event: object) -> None:
        if not isinstance(event, BusEvent):
            return
        record = self._trace.add_event(event)
        self._facts.record_event(event)
        self.status.showMessage(
            translate("trace.replay_event").format(kind=event.kind, message=event.message)
        )
        self.trace_panel.append_records([record])

    def _decode(self, frame: CanFrame):
        try:
            signals = self._catalog.decode(frame)
        except AmbiguousMessageError as error:
            self._facts.record_anomaly("dbc_conflict")
            self.dbc_panel.show_error(str(error))
            return [], DECODE_CONFLICT
        if not signals:
            return [], DECODE_UNKNOWN
        return signals, DECODE_DECODED

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
