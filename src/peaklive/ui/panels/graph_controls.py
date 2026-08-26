"""The grouped, wrapping control bar above the stacked graphs.

Navigation, display options, and cursor placement are three separate concerns,
each carrying the readout it drives. Keeping them in labelled clusters that
wrap as units means a 1024-wide bench screen loses a line of height rather
than a control.
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPainter
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

#: What a readout asks for, and the least it will accept. A readout must never
#: size its cluster to the longest string it might ever hold: font metrics
#: differ per platform, and a cluster wider than the bar overflows rather than
#: wraps.
READOUT_PREFERRED_WIDTH = 210
READOUT_MINIMUM_WIDTH = 90

#: Matches the spacing the cluster row uses between its widgets.
CAPTION_SPACING = 6


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
    """Zoom, grid, follow-live, cursor, and readout controls in four clusters."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("graphControls")
        self.flow = FlowLayout(self, spacing=10)
        self._captions: list[QLabel] = []

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
        self._captions.append(caption)
        self.flow.addWidget(group)
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

    def _option(self, object_name: str, key: str) -> QCheckBox:
        box = QCheckBox(translate(key), objectName=object_name)
        box.setToolTip(translate(key))
        box.setAccessibleName(translate(key))
        box.setChecked(True)
        return box

    @property
    def groups(self) -> tuple[QWidget, ...]:
        return (self.view_group, self.display_group, self.cursor_group)

    @property
    def captions(self) -> tuple[QLabel, ...]:
        return tuple(self._captions)

    # ---- responsive behaviour ------------------------------------------

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]  # noqa: N802
        super().resizeEvent(event)
        self._adapt_to_width()

    def _adapt_to_width(self) -> None:
        """Drop the cluster captions before letting any control clip.

        A narrow bar has to give something up. The caption is the cheapest
        thing to lose: every control it labels still carries its own tooltip
        and accessible name, whereas a squeezed button loses its glyph.
        """
        if self.width() <= 0:
            return
        widest = max(
            self._uncompacted_minimum(group, caption)
            for group, caption in zip(self.groups, self._captions, strict=True)
        )
        compact = widest > self.width()
        for caption in self._captions:
            caption.setVisible(not compact)

    def _uncompacted_minimum(self, group: QWidget, caption: QLabel) -> int:
        """The width the cluster needs with its caption shown.

        Computed the same way whether or not the caption is currently
        visible, so the decision cannot oscillate between the two states.
        """
        minimum = group.minimumSizeHint().width()
        if not caption.isVisible():
            minimum += caption.sizeHint().width() + CAPTION_SPACING
        return minimum
