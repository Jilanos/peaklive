"""Bounded worker shutdown for the workspace shell."""

from __future__ import annotations

from time import monotonic

from PySide6.QtWidgets import QMessageBox

from peaklive.diagnostics import logger
from peaklive.services.export_worker import ExportWorker
from peaklive.ui.worker_lifecycle import abandon_worker


class WorkspaceShutdown:
    """Own the close path so the main-window composition stays small."""

    def _track_export_worker(self, worker: ExportWorker) -> None:
        """Own a started export worker at window level, independent of its dialog."""
        self._export_workers.append(worker)

    def _untrack_export_worker(self, worker: ExportWorker) -> None:
        if worker in self._export_workers:
            self._export_workers.remove(worker)

    def _confirm_force_close_during_export(self) -> bool:
        """Ask before closing while an export is still writing to disk."""
        choice = QMessageBox.question(
            self,
            "Export in progress",
            "An export is still writing to disk. Closing now will cancel it and "
            "remove the incomplete file.\n\nForce close anyway?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return choice == QMessageBox.StandardButton.Yes

    def closeEvent(self, event) -> None:  # type: ignore[no-untyped-def]  # noqa: N802
        """Use one global shutdown budget and retain blocked workers safely."""
        running_exports = [worker for worker in self._export_workers if worker.isRunning()]
        if running_exports and not self._confirm_force_close_during_export():
            event.ignore()
            return
        # A debounced edit still waiting out its window must not be lost to
        # a close that lands before the timer would otherwise have fired.
        self._flush_save()
        self._shutdown_timer.stop()
        deadline = monotonic() + self._shutdown_timeout_ms / 1000

        def settle(worker) -> None:  # type: ignore[no-untyped-def]
            if worker is None or not worker.isRunning():
                return
            remaining_ms = max(0, int((deadline - monotonic()) * 1000))
            worker.wait(remaining_ms)
            if worker.isRunning():
                logger().warning("worker still alive at exit: %s", type(worker).__name__)
            abandon_worker(worker)

        for worker in running_exports:
            worker.request_stop()
        if self._worker is not None and self._worker.isRunning():
            self._worker.request_stop()
            settle(self._worker)
        self._lifecycle.reset()
        abandon_worker(self._worker)
        self._worker = None
        self._cancel_catalog_operation()
        if self._catalog_worker is not None:
            settle(self._catalog_worker)
            self._catalog_worker = None
        self._cancel_signal_backfill()
        if self._signal_decode_worker is not None:
            settle(self._signal_decode_worker)
            self._signal_decode_worker = None
        if self._replay_worker is not None and self._replay_worker.isRunning():
            self._replay_worker.request_stop()
            settle(self._replay_worker)
        for worker in running_exports:
            settle(worker)
        super().closeEvent(event)
