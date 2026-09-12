"""Frame ingestion: shared acquisition/replay batches into workspace state."""

from __future__ import annotations

from functools import partial

from PySide6.QtCore import QTimer

from peaklive.analysis import (
    DECODE_CONFLICT,
    DECODE_DECODED,
    DECODE_INVALID,
    DECODE_UNKNOWN,
    AmbiguousMessageError,
    FrameCache,
    HistoricalSignalStore,
    SeriesStore,
    SessionFacts,
    TraceBuffer,
    TraceRecord,
)
from peaklive.analysis.profiling import (
    PROFILER,
    STAGE_DECODE,
    STAGE_GRAPH_REFRESH,
    STAGE_SERIES_PROJECTION,
    STAGE_TRACE_PROJECTION,
)
from peaklive.domain import BusEvent, CanFrame
from peaklive.i18n import translate
from peaklive.services.signal_decode_worker import (
    DecodedSeries,
    SignalDecodeWorker,
    SourceSignalDecodeWorker,
    decode_series,
)
from peaklive.ui.live_handoff import LiveFrameHandoff
from peaklive.ui.panels.graph_stack import RAW_PREVIEW

GRAPH_REFRESH_INTERVAL_MS = 50

MAX_ROWS_PER_FLUSH = 256

class WorkspaceIngest:
    """Turns worker batches into trace rows, series samples, and session facts."""

    def _init_session_state(self) -> None:
        self._series = SeriesStore()
        self._trace = TraceBuffer()
        self._frames = FrameCache()
        self._history = HistoricalSignalStore()
        self._historical_view_ready = False
        self._facts = SessionFacts()
        self._replay_source_path = None
        self._signal_decode_worker: SignalDecodeWorker | SourceSignalDecodeWorker | None = None
        self._signal_decode_generation = 0
        self._signal_decode_queue: list[str] = []
        # A sustained conflict raises once per frame; the operator only needs
        # to see it once per arbitration ID for the session, not once per frame.
        self._reported_dbc_conflicts: set[tuple[int, bool]] = set()

    # ---- on-demand signal decoding -------------------------------------

    def _request_signal_backfill(self, signal_name: str) -> None:
        if signal_name == RAW_PREVIEW:
            return
        series = self._series.series(signal_name)
        if series is not None and len(series):
            return
        if self._historical_view_ready:
            bounds = self._history.signal_bounds(signal_name)
            if bounds is not None:
                samples = self._history.exact(signal_name, *bounds, limit=20_000)
                if samples:
                    self._series.replace(signal_name, samples)
                    self._sync_graphs()
                return
        if not len(self._frames) and not self._replay_source_path:
            self._report_signal_unavailable(signal_name)
            return
        self._signal_decode_queue.append(signal_name)
        self._pump_signal_backfill()

    def _pump_signal_backfill(self) -> None:
        if self._signal_decode_worker is not None:
            return
        while self._signal_decode_queue:
            signal_name = self._signal_decode_queue.pop(0)
            if signal_name not in self._selected_signal_names:
                continue
            self._signal_decode_generation += 1
            generation = self._signal_decode_generation
            if self._historical_view_ready and self._replay_source_path is not None:
                worker = SourceSignalDecodeWorker(
                    self._catalog,
                    self._replay_source_path,
                    self._history.path,
                    signal_name,
                    generation,
                )
                worker.failed.connect(partial(self._signal_backfill_failed, generation))
                worker.progressed.connect(partial(self._signal_backfill_progressed, generation))
            else:
                worker = SignalDecodeWorker(
                    self._catalog,
                    self._frames.snapshot(),
                    signal_name,
                    self._frames.ingested,
                    truncated=self._frames.truncated,
                    generation=generation,
                )
            worker.completed.connect(partial(self._signal_backfill_completed, generation))
            worker.finished.connect(partial(self._signal_backfill_finished, generation))
            self._signal_decode_worker = worker
            self.status.showMessage(
                translate("signals.deriving").format(signal=signal_name)
            )
            worker.start()
            return

    def _cancel_signal_backfill(self, signal_name: str | None = None) -> None:
        self._signal_decode_queue = [
            queued for queued in self._signal_decode_queue if queued != signal_name
        ]
        worker = self._signal_decode_worker
        if worker is None:
            return
        if signal_name is not None and worker.signal_name != signal_name:
            return
        worker.request_cancel()
        self._signal_decode_generation += 1

    def _signal_backfill_completed(self, generation: int, decoded: DecodedSeries) -> None:
        if generation != self._signal_decode_generation:
            return
        if decoded.signal_name not in self._selected_signal_names:
            return
        if decoded.source_count is None:
            samples = decoded.samples + decode_series(
                self._catalog, self._frames.frames_after(decoded.ingested), decoded.signal_name
            )
        else:
            samples = decoded.samples
        if not samples:
            self._report_signal_unavailable(decoded.signal_name)
            return
        self._series.replace(decoded.signal_name, samples, decoded.unit)
        self._sync_graphs()
        self.status.showMessage(
            translate("signals.derived").format(
                signal=decoded.signal_name, count=decoded.source_count or len(samples)
            )
        )
        if decoded.truncated:
            self.session_note.show_message(
                translate("signals.truncated").format(
                    signal=decoded.signal_name, dropped=self._frames.dropped
                ),
                "warning",
            )

    def _signal_backfill_failed(
        self, generation: int, message: str, worker_generation: int
    ) -> None:
        if generation != self._signal_decode_generation or worker_generation != generation:
            return
        self.session_note.show_message(
            translate("signals.reconstruct_failed").format(message=message), "error"
        )

    def _signal_backfill_progressed(
        self, generation: int, count: int, _total: int, worker_generation: int
    ) -> None:
        if generation != self._signal_decode_generation or worker_generation != generation:
            return
        self.status.showMessage(
            translate("signals.reconstructing").format(count=count)
        )

    def _signal_backfill_finished(self, generation: int) -> None:
        worker = self._signal_decode_worker
        if worker is None or worker.generation != generation:
            return
        self._signal_decode_worker = None
        self._pump_signal_backfill()

    def _report_signal_unavailable(self, signal_name: str) -> None:
        """Say plainly that the loaded session holds nothing for this signal."""
        self.session_note.show_message(
            translate("signals.unavailable").format(signal=signal_name), "info"
        )

    def _set_historical_view_ready(self, ready: bool) -> None:
        self._historical_view_ready = ready
        self._sync_graphs()

    # ---- coalesced graph refresh ---------------------------------------

    def _init_graph_refresh(self) -> None:
        self._graph_dirty = False
        self._trace_resampled = False
        self._pending_trace_records: list[TraceRecord] = []
        self._graph_refresh_timer = QTimer(self)
        self._graph_refresh_timer.setInterval(GRAPH_REFRESH_INTERVAL_MS)
        self._graph_refresh_timer.timeout.connect(self._flush_presentation)

    def _mark_graphs_dirty(self) -> None:
        """Ask for a repaint without performing one per ingested batch."""
        self._graph_dirty = True
        if not self._graph_refresh_timer.isActive():
            self._graph_refresh_timer.start()

    def _flush_presentation(self) -> None:
        """Project one tick's worth of pending trace rows and plot data."""
        pending = self._pending_trace_records
        if not pending and not self._graph_dirty:
            self._graph_refresh_timer.stop()
            return
        if pending:
            self._pending_trace_records = []
            self._trace_resampled = self._trace_resampled or len(pending) > MAX_ROWS_PER_FLUSH
            with PROFILER.stage(STAGE_TRACE_PROJECTION):
                self.trace_panel.append_records(pending[-MAX_ROWS_PER_FLUSH:])
            # A table projection and a full curve refresh can independently be
            # bounded, but combining them in one event-loop turn exceeds the
            # interaction budget on Windows runners.  Leave the already-dirty
            # graph for the next timer tick so Stop and pointer input get a
            # chance to run between the two presentation operations.
            return
        self._flush_graph_refresh()

    def _flush_graph_refresh(self) -> None:
        """Repaint the plots once, if anything has changed since the last one."""
        if not self._graph_dirty:
            return
        self._graph_dirty = False
        with PROFILER.stage(STAGE_GRAPH_REFRESH):
            self.graph_panel.refresh_data()

    def _settle_presentation(self) -> None:
        """Make the trace window authoritative once ingestion has stopped.

        A capped flush can leave the table showing a sampled tail. Re-rendering
        from the bounded buffer costs at most one capacity's worth of rows and
        restores exactly the window the operator would have read.
        """
        pending = self._pending_trace_records
        self._pending_trace_records = []
        resampled = self._trace_resampled or len(pending) > MAX_ROWS_PER_FLUSH
        self._trace_resampled = False
        self._graph_dirty = True
        self._graph_refresh_timer.stop()
        with PROFILER.stage(STAGE_TRACE_PROJECTION):
            if resampled:
                self.trace_panel.refresh()
            elif pending:
                self.trace_panel.append_records(pending)
        self._flush_graph_refresh()

    # ---- presentation queue --------------------------------------------

    def _init_presentation_queue(self) -> None:
        self._live_handoff = LiveFrameHandoff(self, self._render_frames)

    def _begin_presentation_generation(self, generation: int) -> None:
        self._live_handoff.begin(generation)

    def _invalidate_presentation_generation(self, generation: int) -> None:
        self._live_handoff.invalidate(generation)

    def _queue_acquisition_frames(self, generation: int, frames: list[CanFrame]) -> None:
        self._live_handoff.queue(generation, frames)

    def _presentation_queue_pending(self) -> bool:
        return self._live_handoff.pending()

    def _drain_presentation_frames(self) -> None:
        self._live_handoff.drain()

    def _ingest_frames(
        self, frames: list[CanFrame], *, coalesce: bool = False
    ) -> list[TraceRecord]:
        """Decode one batch into the trace, the series, and the session facts.

        This is the whole ingest path minus the display: replay and acquisition
        share it, and neither may skip a frame here. Only the projection that
        follows is allowed to be coalesced, and only when the caller says the
        batches are arriving faster than a display can usefully follow.
        """
        if frames:
            self.acquisition_bar.set_bus_state("running")
        added = []
        historical: list[tuple[str, float, object, str | None]] = []
        for frame in frames:
            with PROFILER.stage(STAGE_DECODE):
                signals, status = self._decode(frame)
            message_name = signals[0].message_name if signals else ""
            with PROFILER.stage(STAGE_TRACE_PROJECTION):
                added.append(
                    self._trace.add_frame(
                        frame,
                        message_name=message_name,
                        decode_status=status,
                        signals=signals,
                    )
                )
                self._facts.record_frame(frame, decoded=status == DECODE_DECODED)
            with PROFILER.stage(STAGE_SERIES_PROJECTION):
                for signal in signals:
                    # Persisted selections are provenance-qualified.  Keep a
                    # legacy display-name selection usable until the next
                    # catalog reconciliation, rather than silently leaving a
                    # live graph empty in an already-open workspace.
                    key = signal.signal_key
                    if key not in self._selected_signal_names:
                        key = signal.display_name
                    if key in self._selected_signal_names:
                        self._series.append(key, frame.timestamp, signal.value, signal.unit)
                        historical.append((key, frame.timestamp, signal.value, signal.unit))
                if not self._selected_signal_names and frame.data:
                    self._series.append(RAW_PREVIEW, frame.timestamp, float(frame.data[0]))
        self._frames.extend(frames)
        self._history.append_many(historical)
        if coalesce:
            self._pending_trace_records.extend(added)
        else:
            with PROFILER.stage(STAGE_TRACE_PROJECTION):
                self.trace_panel.append_records(added)
        return added

    def _render_frames(self, frames: list[CanFrame]) -> None:
        """Ingest every queued frame and repaint the plots immediately.

        The presentation queue accumulates whatever arrived since the last UI
        tick without dropping any of it, so this always sees every frame; only
        the cadence of the repaint is coalesced, by the 16ms presentation timer
        upstream, not by discarding frames here.
        """
        self._ingest_frames(frames)
        self._graph_dirty = True
        self._flush_graph_refresh()

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
            # A sustained conflict raises for every matching frame; the
            # restyle it drives is only worth showing once per identifier.
            if frame.identifier_key not in self._reported_dbc_conflicts:
                self._reported_dbc_conflicts.add(frame.identifier_key)
                self.dbc_panel.show_error(str(error))
            return [], DECODE_CONFLICT
        except (ValueError, TypeError, KeyError):
            self._facts.record_anomaly("decode_invalid")
            return [], DECODE_INVALID
        if not signals:
            return [], DECODE_UNKNOWN
        return signals, DECODE_DECODED
