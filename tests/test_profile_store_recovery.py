"""item_058 coverage: a corrupt profile store must not crash startup."""

from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from peaklive.adapters import FakeCanAdapter
from peaklive.domain import ControllerMode
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow


def test_main_window_starts_from_defaults_and_warns_on_a_corrupt_store(
    qapp, qtbot, tmp_path, monkeypatch
):
    store = ProfileStore(tmp_path)
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_text("{not valid json", encoding="utf-8")
    warnings: list[tuple] = []
    monkeypatch.setattr(
        QMessageBox, "warning", lambda *args, **kwargs: warnings.append((args, kwargs))
    )

    window = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)

    assert window.selected_profile.name == "Default measurement"
    assert window.selected_profile.controller_mode is ControllerMode.PASSIVE_LISTEN_ONLY
    assert len(warnings) == 1


def test_main_window_starts_quietly_when_the_store_is_valid(qapp, qtbot, tmp_path, monkeypatch):
    store = ProfileStore(tmp_path)
    warnings: list[tuple] = []
    monkeypatch.setattr(
        QMessageBox, "warning", lambda *args, **kwargs: warnings.append((args, kwargs))
    )

    window = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)

    assert warnings == []
