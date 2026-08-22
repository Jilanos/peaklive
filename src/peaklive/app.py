"""Application entry point."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from peaklive.ui import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("PeakLive")
    window = MainWindow()
    window.show()
    return app.exec()
