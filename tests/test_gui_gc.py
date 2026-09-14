"""Qt cycles must be reclaimed by the GUI thread, never parser allocations."""

import gc
import os
import subprocess
import sys
from threading import Thread, get_ident

import pytest
from PySide6.QtCore import QObject, Qt

from peaklive.adapters import FakeCanAdapter
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow
from peaklive.ui.gui_gc import ensure_gui_garbage_collection


def test_worker_allocations_leave_qt_cycles_for_the_gui_thread(qtbot, tmp_path):
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    gc.collect()
    previous_thresholds = gc.get_threshold()
    destroyed_on = []
    allocations = []
    try:
        gc.set_threshold(100, 10, 10)
        obj = QObject()
        obj.destroyed.connect(
            lambda: destroyed_on.append(get_ident()), Qt.ConnectionType.DirectConnection
        )
        cycle = [obj]
        cycle.append(cycle)
        del obj, cycle

        # Joining keeps the GUI timer out of the experiment while allocation
        # in a parser-like thread crosses Python's automatic GC threshold.
        worker = Thread(target=lambda: allocations.extend([] for _ in range(1000)))
        worker.start()
        worker.join(timeout=5)
        assert not worker.is_alive()
        assert destroyed_on == []

        qtbot.waitUntil(lambda: bool(destroyed_on), timeout=3000)
        assert destroyed_on == [get_ident()]
    finally:
        gc.set_threshold(*previous_thresholds)


def test_windows_share_the_application_collection_timer(qtbot, tmp_path):
    first = MainWindow(ProfileStore(tmp_path / "first"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(first)
    collector = ensure_gui_garbage_collection()
    second = MainWindow(ProfileStore(tmp_path / "second"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(second)

    assert ensure_gui_garbage_collection() is collector
    first.close()
    assert collector.timer.isActive()
    assert not gc.isenabled()


@pytest.mark.parametrize(
    "counts, expected", [((0, 0, 0), []), ((101, 0, 0), [0]),
                         ((101, 11, 0), [1]), ((101, 11, 11), [2])]
)
def test_collection_respects_the_generation_thresholds(qapp, monkeypatch, counts, expected):
    collector = ensure_gui_garbage_collection()
    collected = []
    monkeypatch.setattr(gc, "get_threshold", lambda: (100, 10, 10))
    monkeypatch.setattr(gc, "get_count", lambda: counts)
    monkeypatch.setattr(gc, "collect", collected.append)

    collector.collect()

    assert collected == expected


@pytest.mark.parametrize("was_enabled", [True, False])
def test_application_destruction_restores_the_previous_gc_policy(was_enabled):
    # QApplication destruction must be exercised outside pytest-qt's shared
    # application, so this test cannot destroy the other tests' event loop.
    result = subprocess.run(
        [sys.executable, "-c", f"""
import gc
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication
from peaklive.ui.gui_gc import ensure_gui_garbage_collection
app = QApplication([])
gc.{'enable' if was_enabled else 'disable'}()
ensure_gui_garbage_collection()
assert not gc.isenabled()
app.deleteLater()
QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
assert gc.isenabled() is {was_enabled}
"""],
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
