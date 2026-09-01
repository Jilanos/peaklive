"""Bounded worker shutdown for the workspace shell."""

from __future__ import annotations

from time import monotonic

from peaklive.diagnostics import logger
from peaklive.ui.dialogs import ExportDialog
from peaklive.ui.session_controller import abandon_worker


class WorkspaceShutdown:
    """Own the close path so the main-window composition stays small."""

    def closeEvent(self, event) -> None:  # type: ignore[no-untyped-def]  # noqa: N802
        """Use one global shutdown budget and retain blocked workers safely."""
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

        export_workers = []
        for dialog in self.findChildren(ExportDialog):
            dialog.cancel_export()
            if dialog._worker is not None:
                export_workers.append(dialog._worker)
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
        for worker in export_workers:
            settle(worker)
        super().closeEvent(event)
