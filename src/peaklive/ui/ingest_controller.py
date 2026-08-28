"""Frame ingestion: the shared path from a worker batch to the workspace.

Acquisition and replay both land here, and they land on the same terms: every
frame reaches the bounded trace buffer, the bounded series store, the bounded
frame cache, and the session facts. What differs is the repaint. Acquisition is
already coalesced upstream by the presentation queue and repaints immediately;
replay arrives as fast as the disk allows and only marks the plots dirty, so a
capture with a thousand batches in it still repaints on a timer rather than a
thousand times.
"""

from __future__ import annotations

from threading import Lock

from PySide6.QtCore import QTimer

from peaklive.analysis import (
    DECODE_CONFLICT,
    DECODE_DECODED,
    DECODE_UNKNOWN,
    AmbiguousMessageError,
    FrameCache,
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
from peaklive.ui.panels.graph_stack import RAW_PREVIEW

# A 64-frame worker batch is efficient for recording, but rendering all of it
# at once can monopolize slower Windows UI threads.  The trace is a coalesced
# visual projection, so keep the newest slice small enough for timers and Stop
# to run between paints.
MAX_PRESENTATION_FRAMES = 8

# Replay delivers every frame - the trace, the series, and the report all have
# to see the whole capture - but the plots do not have to be redrawn once per
# batch. Redrawing every curve from scratch is the most expensive step in the
# ingest path, so replay marks the graphs dirty and one timer tick repaints
# them, no matter how many batches landed in between.
GRAPH_REFRESH_INTERVAL_MS = 50

#: The most trace rows one coalesced flush will project.
#:
#: A replay can produce rows faster than any operator can read them, and the
#: table is a bounded window on the newest records: a row that is superseded
#: before it is drawn was never seen. Capping the flush keeps the cost of the
#: display proportional to elapsed time rather than to capture size. The window
#: is made authoritative again by one bounded refresh when ingestion settles.
MAX_ROWS_PER_FLUSH = 256


class WorkspaceIngest:
    """Turns worker batches into trace rows, series samples, and session facts."""

    def _init_session_state(self) -> None:
        self._series = SeriesStore()
        self._trace = TraceBuffer()
        self._frames = FrameCache()
        self._facts = SessionFacts()

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
        self._presentation_lock = Lock()
        self._presentation_generation: int | None = None
        self._pending_presentation_frames: list[CanFrame] = []
        self._presentation_timer: QTimer | None = None

    def _begin_presentation_generation(self, generation: int) -> None:
        """Accept only the newest worker's coalesced visual projection."""
        with self._presentation_lock:
            self._presentation_generation = generation
            self._pending_presentation_frames = []
        if self._presentation_timer is None:
            self._presentation_timer = QTimer(self)
            self._presentation_timer.setInterval(16)
            self._presentation_timer.timeout.connect(self._drain_presentation_frames)
        self._presentation_timer.start()

    def _invalidate_presentation_generation(self, generation: int) -> None:
        """Discard stale rendering work so lifecycle signals are never queued behind it."""
        with self._presentation_lock:
            if self._presentation_generation != generation:
                return
            self._presentation_generation = None
            self._pending_presentation_frames = []
        if self._presentation_timer is not None:
            self._presentation_timer.stop()

    def _queue_acquisition_frames(self, generation: int, frames: list[CanFrame]) -> None:
        """Replace pending visual work from the worker thread without posting Qt events."""
        with self._presentation_lock:
            if self._presentation_generation != generation:
                return
            # A partial final batch represents the whole finite capture (the
            # offline adapter deliberately produces 32 frames), while a full
            # 64-frame batch marks an ongoing saturated acquisition.
            self._pending_presentation_frames = (
                frames[-MAX_PRESENTATION_FRAMES:] if len(frames) == 64 else frames
            )

    def _drain_presentation_frames(self) -> None:
        """Render at most one current batch per UI tick, keeping the event loop fair."""
        with self._presentation_lock:
            frames = self._pending_presentation_frames
            self._pending_presentation_frames = []
        if frames:
            self._render_frames(frames)

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
                    key = f"{signal.message_name}.{signal.signal_name}"
                    if key in self._selected_signal_names:
                        self._series.append(key, frame.timestamp, signal.value, signal.unit)
                if not self._selected_signal_names and frame.data:
                    self._series.append(RAW_PREVIEW, frame.timestamp, float(frame.data[0]))
        self._frames.extend(frames)
        if coalesce:
            self._pending_trace_records.extend(added)
        else:
            with PROFILER.stage(STAGE_TRACE_PROJECTION):
                self.trace_panel.append_records(added)
        return added

    def _render_frames(self, frames: list[CanFrame]) -> None:
        """Ingest one batch and repaint the plots immediately.

        Acquisition arrives already coalesced by the presentation queue, so the
        repaint is affordable and keeps the live plots at the operator's tick.
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
            self.dbc_panel.show_error(str(error))
            return [], DECODE_CONFLICT
        if not signals:
            return [], DECODE_UNKNOWN
        return signals, DECODE_DECODED

