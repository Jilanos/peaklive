"""The one-line Graphs/Trace header: view, fit, lifecycle, and cursor actions.

The controls it lays out are still owned and wired by their original panels
(`GraphControlsBar`, `AcquisitionBar`) - this bar only reparents their widgets
into one row, the same pattern the workspace mode selector already used, so
no control gains a second, drifting copy of itself.
"""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QWidget


class WorkspaceHeaderBar(QWidget):
    """A single, never-wrapping row above the graph/trace/report stack."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, objectName="workspaceHeaderBar")
        self.row = QHBoxLayout(self)
        self.row.setContentsMargins(0, 0, 0, 0)
        self.row.setSpacing(2)

    def add(self, widget: QWidget) -> QWidget:
        self.row.addWidget(widget)
        return widget
