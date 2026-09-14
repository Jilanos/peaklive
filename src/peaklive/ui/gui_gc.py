"""Reclaim Python cycles on the GUI thread while Qt workers are alive.

Automatic CPython GC runs in whichever thread crosses an allocation threshold.
Collecting Qt wrappers there can invert Qt's QObject mutex and Python's GIL:
the GUI waits in QAction destruction while the parser waits to acquire the GIL
from a QObject destructor (req_031, reproduced from CI run 34858021301).
Reference counting is unchanged; only cyclic collection moves to a GUI timer.
"""

from __future__ import annotations

import gc
from functools import partial

from PySide6.QtCore import QObject, QThread, QTimer, Slot
from PySide6.QtWidgets import QApplication

COLLECTION_INTERVAL_MS = 1000


def _restore_automatic_gc(was_enabled: bool, *_args: object) -> None:
    if was_enabled:
        gc.enable()


class GuiGarbageCollector(QObject):
    """One threshold-aware collection scheduler for the QApplication lifetime."""

    def __init__(self, app: QApplication) -> None:
        super().__init__(app)
        was_enabled = gc.isenabled()
        gc.disable()
        # No closure over this QObject: application destruction must release
        # the scheduler and restore the embedding process's previous policy.
        app.destroyed.connect(partial(_restore_automatic_gc, was_enabled))
        self.timer = QTimer(self)
        self.timer.setInterval(COLLECTION_INTERVAL_MS)
        self.timer.timeout.connect(self.collect)
        self.timer.start()

    @Slot()
    def collect(self) -> None:
        if QThread.currentThread() != self.thread():
            raise RuntimeError("Cyclic collection must run on the GUI thread")
        counts, thresholds = gc.get_count(), gc.get_threshold()
        if thresholds[0] == 0 or counts[0] < thresholds[0]:
            return
        generation = 0
        if counts[1] >= thresholds[1]:
            generation = 1
            if counts[2] >= thresholds[2]:
                generation = 2
        gc.collect(generation)


def ensure_gui_garbage_collection() -> GuiGarbageCollector:
    """Install before starting window workers; multiple windows share it."""
    app = QApplication.instance()
    if app is None or QThread.currentThread() != app.thread():
        raise RuntimeError("A QApplication on the GUI thread is required")
    collector = getattr(app, "_peaklive_garbage_collector", None)
    if collector is None:
        collector = GuiGarbageCollector(app)
        app._peaklive_garbage_collector = collector
    return collector
