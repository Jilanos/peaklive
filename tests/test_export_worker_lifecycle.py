"""item_061 coverage: export workers must outlive their dialog.

A running QThread parented to its ExportDialog is destroyed the moment the
dialog (or the owning window) is torn down, which aborts the process mid
export. The window must own export workers independently, wait visibly and
ask before closing over a running export, and never force-destroy the thread.
"""

from __future__ import annotations

from threading import Event

from PySide6.QtWidgets import QMessageBox

from peaklive.adapters import FakeCanAdapter
from peaklive.domain import CanFrame
from peaklive.services import export_worker as export_worker_module
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow
from peaklive.ui.dialogs.export import SCOPE_ALL
from peaklive.ui.worker_lifecycle import _ABANDONED_WORKERS


def _window(qtbot, tmp_path) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    for index in range(10):
        window._render_frames([CanFrame(float(index), 0x100, bytes([index]))])
    return window


def _held_export(window, tmp_path, qtbot, monkeypatch, gate: Event):
    """Start a real async export and block it mid-write until `gate` is set."""
    real_export_csv = export_worker_module.export_csv

    def blocking_export_csv(path, rows):
        gate.wait(timeout=10.0)
        return real_export_csv(path, rows)

    monkeypatch.setattr(export_worker_module, "export_csv", blocking_export_csv)

    dialog = window._open_export_dialog()
    qtbot.addWidget(dialog)
    dialog.scope_selector.setCurrentIndex(dialog.scope_selector.findData(SCOPE_ALL))
    dialog.set_destination(tmp_path / "held.csv")

    assert dialog.run_export(blocking=False) == 0
    qtbot.waitUntil(lambda: len(window._export_workers) == 1)
    return dialog, window._export_workers[0]


def test_a_started_export_worker_is_not_parented_to_its_dialog(qtbot, tmp_path, monkeypatch):
    window = _window(qtbot, tmp_path)
    gate = Event()
    gate.set()
    dialog, worker = _held_export(window, tmp_path, qtbot, monkeypatch, gate)

    assert worker.parent() is None
    qtbot.waitUntil(lambda: worker not in window._export_workers)


def test_declining_force_close_keeps_the_window_open_and_the_export_running(
    qtbot, tmp_path, monkeypatch
):
    window = _window(qtbot, tmp_path)
    gate = Event()
    dialog, worker = _held_export(window, tmp_path, qtbot, monkeypatch, gate)
    assert worker.isRunning()

    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.No)

    assert not window.close()
    assert worker.isRunning()
    assert window._export_workers == [worker]

    gate.set()
    qtbot.waitUntil(lambda: worker not in window._export_workers)


def test_forcing_close_during_an_export_never_destroys_the_running_thread(
    qtbot, tmp_path, monkeypatch
):
    window = _window(qtbot, tmp_path)
    gate = Event()
    dialog, worker = _held_export(window, tmp_path, qtbot, monkeypatch, gate)
    assert worker.isRunning()

    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)

    # A bounded close must return promptly rather than block on the worker.
    assert window.close()
    # Abandoned, but still referenced: destroying a running QThread aborts Qt.
    assert worker in _ABANDONED_WORKERS
    assert worker.isRunning()

    gate.set()
    qtbot.waitUntil(lambda: worker not in _ABANDONED_WORKERS, timeout=5_000)
    # The stop request reached the stream before it wrote anything.
    assert not (tmp_path / "held.csv").exists()
