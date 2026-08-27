"""item_031 - DBC catalog mutations stay off the UI critical path.

Parsing is gated by a threading Event so a test can hold the worker inside
`DbcCatalog.load` for as long as it likes. That stands in for the real trigger:
a large or slow-to-read DBC file.
"""

from pathlib import Path
from threading import Event

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFileDialog

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis import DbcCatalog
from peaklive.services.dbc_worker import CatalogOperation, CatalogOperationKind
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow

VEHICLE_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 291 VehicleStatus: 8 ECU
 SG_ Speed : 0|16@1+ (0.1,0) [0|250] "km/h" ECU
'''

BODY_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 292 BodyStatus: 8 ECU
 SG_ DoorOpen : 0|1@1+ (1,0) [0|1] "" ECU
'''


class EventLoopProbe:
    """Counts UI-thread timer ticks, so 'still responsive' is a measurement."""

    def __init__(self) -> None:
        self.ticks = 0
        self._timer = QTimer()
        self._timer.setInterval(5)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self) -> None:
        self.ticks += 1

    def stop(self) -> None:
        self._timer.stop()

    def observe(self, qtbot, ticks: int = 3) -> None:
        target = self.ticks + ticks
        qtbot.waitUntil(lambda: self.ticks >= target, timeout=3_000)


def _write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _window(qtbot, tmp_path, show: bool = False):
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    if show:
        window.show()
    return window


def _gate_parsing(monkeypatch) -> Event:
    """Hold every DBC parse until the returned gate is set."""
    gate = Event()
    original = DbcCatalog.load

    def gated(self, path):
        gate.wait(timeout=10.0)
        return original(self, path)

    monkeypatch.setattr(DbcCatalog, "load", gated)
    return gate


def _load(window, *paths: Path) -> None:
    window._queue_catalog_operation(
        CatalogOperation(kind=CatalogOperationKind.LOAD, paths=paths)
    )


# --------------------------------------------------------------------------
# AC1 - responsiveness under delayed parsing and derived-data preparation
# --------------------------------------------------------------------------


def test_loading_a_slow_dbc_keeps_the_window_interactive(qtbot, tmp_path, monkeypatch):
    window = _window(qtbot, tmp_path, show=True)
    gate = _gate_parsing(monkeypatch)
    probe = EventLoopProbe()

    _load(window, _write(tmp_path, "vehicle.dbc", VEHICLE_DBC))

    assert window.progress.isVisible()
    probe.observe(qtbot)
    assert not window._catalog.definitions  # nothing committed while parsing

    gate.set()
    qtbot.waitUntil(lambda: len(window._catalog.definitions) == 1)
    probe.stop()
    assert not window.progress.isVisible()
    assert window.dbc_library.topLevelItemCount() == 1


def test_removing_a_dbc_keeps_the_window_interactive(qtbot, tmp_path, monkeypatch):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_write(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    content_hash = window._catalog.definitions[0].content_hash
    probe = EventLoopProbe()

    window._remove_dbc(content_hash)
    probe.observe(qtbot)

    qtbot.waitUntil(lambda: not window._catalog.definitions)
    probe.stop()
    assert window.dbc_library.topLevelItemCount() == 0


def test_the_file_dialog_path_queues_a_background_load(qtbot, tmp_path, monkeypatch):
    window = _window(qtbot, tmp_path)
    chosen = _write(tmp_path, "vehicle.dbc", VEHICLE_DBC)
    monkeypatch.setattr(
        QFileDialog, "getOpenFileNames", staticmethod(lambda *a, **k: ([str(chosen)], ""))
    )

    window._choose_dbc()

    qtbot.waitUntil(lambda: len(window._catalog.definitions) == 1)
    assert str(chosen) in window.selected_profile.dbc_paths


# --------------------------------------------------------------------------
# AC2 - progress, per-file errors, and cancellation before commit
# --------------------------------------------------------------------------


def test_progress_names_the_operation_and_the_file(qtbot, tmp_path, monkeypatch):
    window = _window(qtbot, tmp_path)
    gate = _gate_parsing(monkeypatch)
    messages: list[str] = []
    window.status.messageChanged.connect(messages.append)

    _load(window, _write(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    gate.set()
    qtbot.waitUntil(lambda: len(window._catalog.definitions) == 1)

    assert any("vehicle.dbc" in message for message in messages)


def test_cancelling_before_commit_leaves_the_catalog_and_profile_unchanged(
    qtbot, tmp_path, monkeypatch
):
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_write(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    before_paths = list(window.selected_profile.dbc_paths)
    before_hashes = [d.content_hash for d in window._catalog.definitions]
    gate = _gate_parsing(monkeypatch)

    _load(window, _write(tmp_path, "body.dbc", BODY_DBC))
    window._cancel_catalog_operation()
    gate.set()
    qtbot.waitUntil(lambda: window._catalog_worker is None)

    assert [d.content_hash for d in window._catalog.definitions] == before_hashes
    assert window.selected_profile.dbc_paths == before_paths
    assert window.dbc_library.topLevelItemCount() == 1


def test_a_malformed_file_is_reported_without_losing_the_good_one(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    broken = _write(tmp_path, "broken.dbc", "this is not a DBC file")
    good = _write(tmp_path, "body.dbc", BODY_DBC)

    _load(window, broken, good)
    qtbot.waitUntil(lambda: len(window._catalog.definitions) == 1)

    assert "Cannot load broken.dbc" in window.dbc_panel.note.text()
    assert window.dbc_panel.note.level == "error"
    assert window.selected_profile.dbc_paths == [str(good)]


# --------------------------------------------------------------------------
# AC3 - atomic commits and consistent dependent state
# --------------------------------------------------------------------------


def test_rapid_consecutive_operations_are_serialized_and_end_consistent(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    vehicle = _write(tmp_path, "vehicle.dbc", VEHICLE_DBC)
    body = _write(tmp_path, "body.dbc", BODY_DBC)

    # Queued back to back, with no waiting in between.
    _load(window, vehicle)
    _load(window, body)
    qtbot.waitUntil(lambda: len(window._catalog.definitions) == 2, timeout=5_000)
    first_hash = window._catalog.definitions[0].content_hash

    window._dbc_enabled_changed(first_hash, False)
    window._dbc_enabled_changed(first_hash, True)
    window._remove_dbc(first_hash)
    qtbot.waitUntil(lambda: len(window._catalog.definitions) == 1, timeout=5_000)
    qtbot.waitUntil(lambda: window._catalog_worker is None)

    # Catalog, profile, and panel all describe the same single remaining DBC.
    assert window._catalog.definitions[0].path == body
    assert window.selected_profile.dbc_paths == [str(body)]
    assert window.dbc_library.topLevelItemCount() == 1
    assert not window.selected_profile.trace_filters["disabled_dbc_hashes"]


def test_removing_drops_selected_signals_but_disabling_keeps_them(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    vehicle = _write(tmp_path, "vehicle.dbc", VEHICLE_DBC)
    window._load_dbc_path(vehicle)
    content_hash = window._catalog.definitions[0].content_hash
    window._selected_signal_names = {"VehicleStatus.Speed"}

    window._dbc_enabled_changed(content_hash, False)
    qtbot.waitUntil(lambda: not window._catalog.is_enabled(content_hash))

    # Disabling is reversible, so the operator's plot selection survives it.
    assert "VehicleStatus.Speed" in window._selected_signal_names

    window._dbc_enabled_changed(content_hash, True)
    qtbot.waitUntil(lambda: window._catalog.is_enabled(content_hash))
    window._remove_dbc(content_hash)
    qtbot.waitUntil(lambda: not window._catalog.definitions)

    assert "VehicleStatus.Speed" not in window._selected_signal_names
    assert window.selected_profile.displayed_signals == []


def test_a_superseded_operation_result_is_not_committed(qtbot, tmp_path, monkeypatch):
    window = _window(qtbot, tmp_path)
    gate = _gate_parsing(monkeypatch)
    _load(window, _write(tmp_path, "vehicle.dbc", VEHICLE_DBC))

    # Switching profiles abandons the in-flight operation entirely.
    window._load_profile_dbcs()
    gate.set()
    qtbot.waitUntil(lambda: window._catalog_worker is None)

    assert not window._catalog.definitions
    assert window.dbc_library.topLevelItemCount() == 0


def test_conflict_resolution_commits_off_the_ui_thread(qtbot, tmp_path):
    conflicting = '''VERSION ""
NS_ :
BS_:
BU_: GW
BO_ 291 VehicleStatus: 8 GW
 SG_ Speed : 0|8@1+ (1,0) [0|255] "km/h" GW
'''
    window = _window(qtbot, tmp_path)
    window._load_dbc_path(_write(tmp_path, "vehicle.dbc", VEHICLE_DBC))
    window._load_dbc_path(_write(tmp_path, "gateway.dbc", conflicting))
    content_hash = window._catalog.definitions[0].content_hash

    window._resolve_conflict(291, content_hash)
    qtbot.waitUntil(lambda: window._catalog.resolutions.get(291) == content_hash)
    qtbot.waitUntil(lambda: window._catalog_worker is None)

    assert window.selected_profile.trace_filters["dbc_conflict_resolutions"] == {
        "291": content_hash
    }
