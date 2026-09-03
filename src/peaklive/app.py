"""Application entry point."""

from __future__ import annotations

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from peaklive.diagnostics import install_exception_hooks
from peaklive.resources import application_icon_path
from peaklive.ui import MainWindow


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


def main() -> int:
    install_exception_hooks()
    app = QApplication(sys.argv)
    apply_application_identity(app)
    window = MainWindow()
    window.show()
    return app.exec()
