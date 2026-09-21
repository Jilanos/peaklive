"""On-demand signal reconstruction: decode a newly selected signal from history/source."""

from __future__ import annotations

from functools import partial

from peaklive.services.signal_decode_worker import (
    DecodedSeries,
    SignalDecodeWorker,
    SourceSignalDecodeWorker,
    decode_series,
)
from peaklive.ui.panels.graph_stack import RAW_PREVIEW


class WorkspaceSignalBackfill:
    """Reconstructs a signal's full series when it is selected after ingestion."""

    def _init_signal_backfill_state(self) -> None:
        self._signal_decode_worker: SignalDecodeWorker | SourceSignalDecodeWorker | None = None
        self._signal_decode_generation = 0
        self._signal_decode_queue: list[str] = []

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
            # Eligible for full-source reconstruction once this session's
            # replay has finished parsing its source, even if the
            # background history writer (item_133) has not yet settled
            # every batch: SourceSignalDecodeWorker reads the source file
            # directly rather than the history store, so it does not need
            # to wait for that - only `_historical_view_ready` (used above
            # to answer instantly from an already-settled store) does.
            if self._replay_source_path is not None and self._replay_worker is None:
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
            self._set_status("signals.deriving", signal=signal_name)
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
        self._set_status(
            "signals.derived",
            signal=decoded.signal_name,
            count=decoded.source_count or len(samples),
        )
        if decoded.truncated:
            self.session_note.show_key(
                "signals.truncated",
                "warning",
                signal=decoded.signal_name,
                dropped=self._frames.dropped,
            )

    def _signal_backfill_failed(
        self, generation: int, message: str, worker_generation: int
    ) -> None:
        if generation != self._signal_decode_generation or worker_generation != generation:
            return
        self.session_note.show_key("signals.reconstruct_failed", "error", message=message)

    def _signal_backfill_progressed(
        self, generation: int, count: int, _total: int, worker_generation: int
    ) -> None:
        if generation != self._signal_decode_generation or worker_generation != generation:
            return
        self._set_status("signals.reconstructing", count=count)

    def _signal_backfill_finished(self, generation: int) -> None:
        worker = self._signal_decode_worker
        if worker is None or worker.generation != generation:
            return
        self._signal_decode_worker = None
        self._pump_signal_backfill()

    def _report_signal_unavailable(self, signal_name: str) -> None:
        """Say plainly that the loaded session holds nothing for this signal."""
        self.session_note.show_key("signals.unavailable", "info", signal=signal_name)

    def _set_historical_view_ready(self, ready: bool) -> None:
        self._historical_view_ready = ready
        self._sync_graphs()
