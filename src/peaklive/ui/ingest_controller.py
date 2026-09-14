"""Frame ingestion: shared acquisition/replay batches into workspace state."""

from __future__ import annotations

import sqlite3
from itertools import groupby

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
        self._history_failed = False
        self._history_failure_message: str | None = None
        self._init_signal_backfill_state()
        # A sustained conflict raises once per frame; the operator only needs
        # to see it once per arbitration ID for the session, not once per frame.
        self._reported_dbc_conflicts: set[tuple[int, bool]] = set()

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
        # Once a persistence failure is recorded, this session's store is
        # presumed poisoned until the next reset/reopen: retrying the same
        # write would only repeat the same exception, and a retry that
        # happened to half-succeed could double-count an already-accepted
        # batch. Trace/series projection above is unaffected, so inspection
        # of already-ingested and newly-arriving frames keeps working.
        if not self._history_failed:
            try:
                self._history.append_many(historical)
            except sqlite3.Error as error:
                self._fail_history(str(error))
        if coalesce:
            self._pending_trace_records.extend(added)
        else:
            with PROFILER.stage(STAGE_TRACE_PROJECTION):
                self.trace_panel.append_records(added)
        return added

    def _ingest_replay_records(self, records: list[object]) -> bool:
        """Ingest one ordered replay batch, preserving source frame/event order.

        Returns whether historical persistence failed while processing this
        batch, so the caller can put the replay generation into an explicit
        failed terminal state instead of continuing to accept records.
        """
        ingested_frames = False
        for is_event, group in groupby(records, key=lambda record: isinstance(record, BusEvent)):
            if is_event:
                for event in group:
                    self._render_replay_event(event)
            else:
                self._ingest_frames(list(group), coalesce=True)
                ingested_frames = True
        if ingested_frames:
            self._mark_graphs_dirty()
        return self._history_failed

    def _render_frames(self, frames: list[CanFrame]) -> None:
        """Ingest every queued frame and repaint the plots immediately.

        The presentation queue accumulates whatever arrived since the last UI
        tick without dropping any of it, so this always sees every frame; only
        the cadence of the repaint is coalesced, by the 16ms presentation timer
        upstream, not by discarding frames here.
        """
        self._ingest_frames(frames)
        if self._history_failed:
            self._acquisition_history_failed(self._history_failure_message or "")
            return
        self._graph_dirty = True
        self._flush_graph_refresh()

    def _reset_history_store(self) -> None:
        """Clear historical storage for a new session, replacing a poisoned store.

        A store that already failed once may no longer accept `clear()`
        either (a still-broken backing file); discarding it for a fresh
        temporary store is what actually guarantees the next open succeeds,
        rather than depending on whatever caused the failure having cleared.
        """
        if not self._history_failed:
            try:
                self._history.clear()
                return
            except sqlite3.Error:
                pass
        self._history.close()
        self._history = HistoricalSignalStore()
        self._history_failed = False
        self._history_failure_message = None

    def _fail_history(self, message: str) -> None:
        """Record one terminal historical-persistence failure, exactly once.

        The store is presumed poisoned for the rest of this session: further
        writes are skipped (see `_ingest_frames`) rather than retried, and the
        overview is marked incomplete so a stale/partial history is never
        mistaken for a complete one. The caller (replay or acquisition) is
        responsible for stopping further source consumption.
        """
        if self._history_failed:
            return
        self._history_failed = True
        self._history_failure_message = message
        self._historical_view_ready = False
        self.session_note.show_message(
            translate("trace.history_failed").format(message=message), "error"
        )

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
