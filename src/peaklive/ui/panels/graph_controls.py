"""The compact, single-row command bar above the stacked graphs."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from peaklive.i18n import translate
#: What a readout asks for, and the least it will accept. A readout must never
#: size its cluster to the longest string it might ever hold: font metrics
#: differ per platform, and a cluster wider than the bar overflows rather than
#: wraps.
READOUT_PREFERRED_WIDTH = 150
READOUT_MINIMUM_WIDTH = 64


class ElidingLabel(QLabel):
    """A readout that shortens its text to the width it was given.

    `text()` keeps the full value - the shortening happens at paint time - so
    callers and tests still read what the readout means, and the tooltip
    carries the untruncated string.
    """

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setToolTip(text)

    def setText(self, text: str) -> None:  # noqa: N802 - Qt override
        super().setText(text)
        self.setToolTip(text)

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override
        hint = super().sizeHint()
        return QSize(min(hint.width(), READOUT_PREFERRED_WIDTH), hint.height())

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - Qt override
        return QSize(READOUT_MINIMUM_WIDTH, super().minimumSizeHint().height())

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]  # noqa: N802
        painter = QPainter(self)
        painter.setPen(self.palette().color(self.foregroundRole()))
        elided = self.fontMetrics().elidedText(
            self.text(), Qt.TextElideMode.ElideRight, self.width()
        )
        painter.drawText(self.rect(), int(self.alignment()), elided)
        painter.end()


class GraphControlsBar(QWidget):
    """One dense toolbar for graph navigation, display, cursor, and view mode.

    It deliberately never wraps: wrapping turns a measurement workspace into
    two unrelated headers. Textual state elides in place, while each compact
    action retains an accessible name and tooltip.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("graphControls")
        self.row = QHBoxLayout(self)
        self.row.setContentsMargins(0, 0, 0, 0)
        self.row.setSpacing(4)

        self.mode_selector = QComboBox(objectName="workspaceModeSelector")
        self.mode_selector.setAccessibleName(translate("workspace.mode_accessible"))
        self.mode_selector.setToolTip(translate("workspace.mode_accessible"))
        self.mode_selector.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.mode_selector.setMinimumContentsLength(8)
        self.row.addWidget(self.mode_selector)

        self.view_group, view_row = self._group("graphViewGroup")
        self.zoom_in_button = self._nav("zoomInButton", "graph.zoom_in", "+")
        self.zoom_out_button = self._nav("zoomOutButton", "graph.zoom_out", "−")
        self.fit_button = self._nav("fitButton", "graph.fit", "⤢")
        for button in (self.zoom_in_button, self.zoom_out_button, self.fit_button):
            view_row.addWidget(button)
        self.window_label = self._readout("windowReadout", "graph.window_empty")
        view_row.addWidget(self.window_label)

        self.display_group, display_row = self._group("graphDisplayGroup")
        self.grid_checkbox = self._toggle("gridCheckbox", "graph.grid", "▦")
        self.follow_checkbox = self._toggle("followCheckbox", "graph.follow", "▶")
        display_row.addWidget(self.grid_checkbox)
        display_row.addWidget(self.follow_checkbox)

        self.cursor_group, cursor_row = self._group("graphCursorGroup")
        self.cursor_a_button = self._nav("cursorAButton", "graph.cursor_a", "A")
        self.cursor_b_button = self._nav("cursorBButton", "graph.cursor_b", "B")
        cursor_row.addWidget(self.cursor_a_button)
        cursor_row.addWidget(self.cursor_b_button)
        self.cursor_summary = self._readout("cursorSummary", "graph.cursor_summary_empty")
        cursor_row.addWidget(self.cursor_summary)

    # ---- construction -------------------------------------------------

    def _group(self, object_name: str) -> tuple[QWidget, QHBoxLayout]:
        """One compact cluster in the fixed single-row toolbar."""
        group = QWidget(self, objectName=object_name)
        group.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        row = QHBoxLayout(group)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(3)
        self.row.addWidget(group)
        return group, row

    def _nav(self, object_name: str, key: str, glyph: str) -> QToolButton:
        button = QToolButton(objectName=object_name)
        button.setProperty("navButton", True)
        button.setText(glyph)
        button.setAccessibleName(translate(key))
        button.setToolTip(translate(key))
        return button

    def _readout(self, object_name: str, key: str) -> ElidingLabel:
        """A live value stays with the controls that change it."""
        readout = ElidingLabel(translate(key))
        readout.setObjectName(object_name)
        return readout

    def _toggle(self, object_name: str, key: str, glyph: str) -> QToolButton:
        button = self._nav(object_name, key, glyph)
        button.setCheckable(True)
        button.setChecked(True)
        return button

    @property
    def groups(self) -> tuple[QWidget, ...]:
        return (self.view_group, self.display_group, self.cursor_group)
