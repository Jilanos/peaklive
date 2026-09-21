"""Application entry point."""

from __future__ import annotations

import sys

from PySide6.QtGui import QColor, QIcon, QPalette
from PySide6.QtWidgets import QApplication

from peaklive.diagnostics import install_exception_hooks
from peaklive.i18n import set_locale
from peaklive.resources import application_icon_path
from peaklive.services.ui_settings import UiSettingsStore
from peaklive.ui import MainWindow
from peaklive.ui.qt_translations import apply_qt_translations
from peaklive.ui.theme import BACKGROUND, CONTROL_HOVER, POPUP_SURFACE, SURFACE_DEEP, TEXT
from peaklive.ui.worker_lifecycle import drain_abandoned_workers_at_exit


def apply_application_identity(app: QApplication) -> QIcon:
    """Name and badge the application before any window exists.

    Taskbars and window managers read the icon from the application object at
    the moment a window is first mapped, so this has to happen before
    ``MainWindow`` is constructed rather than after it is shown.
    """
    app.setApplicationName("PeakLive")
    app.setDesktopFileName("PeakLive")
    icon = QIcon(str(application_icon_path()))
    app.setWindowIcon(icon)
    return icon


def apply_application_theme(app: QApplication) -> None:
    """Install one Fusion palette before dialogs or windows are constructed."""
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BACKGROUND))
    palette.setColor(QPalette.ColorRole.Base, QColor(SURFACE_DEEP))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(POPUP_SURFACE))
    palette.setColor(QPalette.ColorRole.Button, QColor(CONTROL_HOVER))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(POPUP_SURFACE))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#1f6feb"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)


def main() -> int:
    install_exception_hooks()
    # The interface language has to be live before any widget, dialog or
    # standard-button text is constructed, so it is read ahead of the
    # QApplication rather than inside the window.
    ui_settings = UiSettingsStore()
    set_locale(ui_settings.load().locale)
    app = QApplication(sys.argv)
    apply_qt_translations(ui_settings.load().locale)
    apply_application_theme(app)
    apply_application_identity(app)
    # Every window's own closeEvent already applies its shutdown budget; this
    # is the one further, final chance before the interpreter tears down
    # whatever a stuck driver left running in the abandoned-worker set.
    app.aboutToQuit.connect(drain_abandoned_workers_at_exit)
    window = MainWindow(ui_settings=ui_settings)
    window.show()
    return app.exec()
