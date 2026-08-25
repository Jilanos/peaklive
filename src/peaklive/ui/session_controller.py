"""Acquisition, replay, ingestion, and session reporting for the shell."""

from __future__ import annotations

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
from peaklive.services.replay_worker import ReplayWorker
from peaklive.services.worker import AcquisitionWorker
from peaklive.ui.panels.graph_stack import RAW_PREVIEW


class WorkspaceSession:
    """Runs one acquisition or replay session and keeps its facts.

    Frames land in three places at once — the bounded trace buffer, the bounded
    series store, and the session facts — so the trace, the plots, and the
    report always describe the same session.
    """

    # ---- acquisition and replay ---------------------------------------

    def _start_acquisition(self) -> None:
        if self._worker and self._worker.isRunning():
            return
        self._reset_session("")
        self._worker = AcquisitionWorker(self._adapter_factory(), self.selected_profile)
        self._worker.frames_received.connect(self._render_frames)
        self._worker.status_changed.connect(self.status.showMessage)
        self._worker.event_received.connect(self._render_acquisition_event)
        self._worker.acquisition_failed.connect(self._acquisition_failed)
        self._worker.finished.connect(self._acquisition_finished)
        self.acquisition_bar.set_running(True)
        self.acquisition_bar.set_bus_state("connecting")
        self.status.showMessage(translate("acquisition.opening"))
        self._worker.start()

    def _stop_acquisition(self) -> None:
        if self._worker is not None:
            self._worker.request_stop()
            self.status.showMessage(translate("acquisition.stopping"))

    def _acquisition_failed(self, message: str) -> None:
        self.acquisition_bar.set_bus_state("bus_error")
        self.status.showMessage(translate("acquisition.failed").format(message=message))

    def _acquisition_finished(self) -> None:
        self.acquisition_bar.set_running(False)
        self.acquisition_bar.set_bus_state("stopped")
        self._worker = None
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
