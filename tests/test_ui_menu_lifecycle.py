"""Dynamic menu rebuilds must retire their previous Qt objects."""

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QMenu

from peaklive.adapters import FakeCanAdapter
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow


def _counts(window):
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    return tuple(len(window.findChildren(kind)) for kind in (QAction, QActionGroup, QMenu))


def test_setup_refreshes_do_not_accumulate_action_groups(qtbot, tmp_path):
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    before = _counts(window)

    for _ in range(20):
        window._sync_setup_menu_enabled()

    assert _counts(window) == before


def test_catalog_refreshes_do_not_accumulate_actions_or_submenus(qtbot, tmp_path):
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    dbc = tmp_path / "vehicle.dbc"
    dbc.write_text(
        'VERSION ""\nNS_ :\nBS_:\nBU_: ECU\nBO_ 291 Vehicle: 8 ECU\n'
        ' SG_ Speed : 0|16@1+ (0.1,0) [0|250] "km/h" ECU\n',
        encoding="utf-8",
    )
    window._load_dbc_path(dbc)
    view = window._catalog.view()
    before = _counts(window)

    for _ in range(20):
        window._refresh_dbc_menu(view)

    assert _counts(window) == before
