"""The grouped, wrapping control bar above the stacked graphs.

Navigation, display options, and cursor placement are three separate concerns,
each carrying the readout it drives. Keeping them in labelled clusters that
wrap as units means a 1024-wide bench screen loses a line of height rather
than a control.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from peaklive.i18n import translate
from peaklive.ui.flow_layout import FlowLayout

#: Wide enough for the longest readout, narrow enough that a cluster carrying
#: one still fits a 1024 px bench screen.
READOUT_MINIMUM_WIDTH = 160


class GraphControlsBar(QWidget):
    """Zoom, grid, follow-live, cursor, and readout controls in four clusters."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("graphControls")
        self.flow = FlowLayout(self, spacing=10)

        self.view_group, view_row = self._group("graph.group_view", "graphViewGroup")
        self.zoom_in_button = self._nav("zoomInButton", "graph.zoom_in", "+")
        self.zoom_out_button = self._nav("zoomOutButton", "graph.zoom_out", "−")
        self.fit_button = self._nav("fitButton", "graph.fit", "⤢")
        for button in (self.zoom_in_button, self.zoom_out_button, self.fit_button):
            view_row.addWidget(button)
        self.window_label = self._readout("windowReadout", "graph.window_empty")
        view_row.addWidget(self.window_label)

        self.display_group, display_row = self._group("graph.group_display", "graphDisplayGroup")
        self.grid_checkbox = self._option("gridCheckbox", "graph.grid")
        self.follow_checkbox = self._option("followCheckbox", "graph.follow")
        display_row.addWidget(self.grid_checkbox)
        display_row.addWidget(self.follow_checkbox)

        self.cursor_group, cursor_row = self._group("graph.group_cursors", "graphCursorGroup")
        self.cursor_a_button = self._nav("cursorAButton", "graph.cursor_a", "A")
        self.cursor_b_button = self._nav("cursorBButton", "graph.cursor_b", "B")
        cursor_row.addWidget(self.cursor_a_button)
        cursor_row.addWidget(self.cursor_b_button)
        self.cursor_summary = self._readout("cursorSummary", "graph.cursor_summary_empty")
        cursor_row.addWidget(self.cursor_summary)

    # ---- construction -------------------------------------------------

    def _group(self, title_key: str, object_name: str) -> tuple[QWidget, QHBoxLayout]:
        """One labelled cluster that the flow layout moves as a single item."""
        group = QWidget(self, objectName=object_name)
        group.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        row = QHBoxLayout(group)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        caption = QLabel(translate(title_key).upper(), objectName="controlGroupLabel")
        caption.setAccessibleName(translate(title_key))
        row.addWidget(caption)
        self.flow.addWidget(group)
        return group, row

    def _nav(self, object_name: str, key: str, glyph: str) -> QToolButton:
        button = QToolButton(objectName=object_name)
        button.setProperty("navButton", True)
        button.setText(glyph)
        button.setAccessibleName(translate(key))
        button.setToolTip(translate(key))
        return button

    def _readout(self, object_name: str, key: str) -> QLabel:
        """A live value stays with the controls that change it."""
        readout = QLabel(translate(key), objectName=object_name)
        readout.setMinimumWidth(READOUT_MINIMUM_WIDTH)
        return readout

    def _option(self, object_name: str, key: str) -> QCheckBox:
        box = QCheckBox(translate(key), objectName=object_name)
        box.setToolTip(translate(key))
        box.setAccessibleName(translate(key))
        box.setChecked(True)
        return box

    @property
    def groups(self) -> tuple[QWidget, ...]:
        return (self.view_group, self.display_group, self.cursor_group)
