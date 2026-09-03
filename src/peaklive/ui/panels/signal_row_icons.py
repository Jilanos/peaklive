"""Eye/star pictograms for the Signals tree's shown/favorite action cells.

Qt's own tree-branch decoration only ever attaches to a tree's first logical
column, so the signal name - which carries the DBC/message indentation and
expand affordance - has to stay column 0. Replacing the checkbox squares in
the trailing shown/favorite columns with pictograms therefore happens as a
paint-only delegate: the underlying `Qt.ItemIsUserCheckable` / `checkState()`
model is untouched, so mouse click and keyboard Space keep toggling exactly
as they did before - only what gets drawn changes (item_054 AC3).
"""

from __future__ import annotations

import math

from PySide6.QtCore import QEvent, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem, QTreeWidget

from peaklive.ui import theme

EYE = "eye"
STAR = "star"


class BranchAffordanceTree(QTreeWidget):
    """A tree that paints its own expand/collapse chevrons.

    Qt's `::branch` stylesheet sub-control turns out not to render a custom
    shape once the tree has a visible header (verified empirically: the same
    rule paints a clean triangle with the header hidden, and a flat,
    low-contrast box once it is shown) - a Fusion-style quirk this app cannot
    route around from the stylesheet alone. Overriding `drawBranches` paints
    the affordance directly instead, independent of that quirk, and adds a
    hover state the native indicator never exposed either (item_054 AC2).
    """

    def __init__(self, parent=None, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.setMouseTracking(True)
        self._hover_row: int = -1

    def viewportEvent(self, event) -> bool:  # noqa: N802 - Qt override
        if event.type() in (QEvent.Type.MouseMove, QEvent.Type.Enter):
            index = self.indexAt(event.position().toPoint())
            row = index.row() if index.isValid() else -1
            if row != self._hover_row:
                self._hover_row = row
                self.viewport().update()
        elif event.type() == QEvent.Type.Leave and self._hover_row != -1:
            self._hover_row = -1
            self.viewport().update()
        return super().viewportEvent(event)

    def drawBranches(self, painter, rect, index) -> None:  # noqa: N802 - Qt override
        item = self.itemFromIndex(index)
        if item is None or item.childCount() == 0:
            return
        if not self.isEnabled():
            colour = QColor(theme.DISABLED_TEXT)
        elif index.row() == self._hover_row:
            colour = QColor(theme.FOCUS_RING)
        else:
            colour = QColor(theme.TEXT_BODY)
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(colour)
        cx = rect.right() - rect.height() / 2
        cy = rect.center().y()
        if item.isExpanded():
            points = QPolygonF(
                [QPointF(cx - 4, cy - 2.5), QPointF(cx + 4, cy - 2.5), QPointF(cx, cy + 3.5)]
            )
        else:
            points = QPolygonF(
                [QPointF(cx - 2.5, cy - 4), QPointF(cx - 2.5, cy + 4), QPointF(cx + 3.5, cy)]
            )
        painter.drawPolygon(points)
        painter.restore()


class RowActionDelegate(QStyledItemDelegate):
    """Paints a compact eye or star pictogram instead of a checkbox square."""

    def __init__(self, kind: str, key_role: int, parent=None) -> None:
        super().__init__(parent)
        self._kind = kind
        self._key_role = key_role

    def paint(self, painter, option, index) -> None:  # noqa: N802 - Qt override
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.features &= ~QStyleOptionViewItem.ViewItemFeature.HasCheckIndicator
        opt.text = ""
        style = opt.widget.style() if opt.widget is not None else self.parent().style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, opt.widget)

        name_index = index.siblingAtColumn(0)
        if not name_index.data(self._key_role):
            return  # DBC and message rows carry no shown/favorite action.
        # PySide6 hands the raw stored int back from a QModelIndex, not the
        # Qt.CheckState wrapper item.checkState() returns - comparing it to
        # the enum member directly is always False without this cast.
        raw_state = index.data(Qt.ItemDataRole.CheckStateRole)
        checked = raw_state is not None and Qt.CheckState(raw_state) == Qt.CheckState.Checked
        colour = QColor(theme.ROW_ACTION_ACTIVE if checked else theme.ROW_ACTION_MUTED)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = option.rect
        size = max(8, min(rect.width(), rect.height()) - 12)
        centre = rect.center()
        if self._kind == EYE:
            _paint_eye(painter, centre.x(), centre.y(), size, colour, checked)
        else:
            _paint_star(painter, centre.x(), centre.y(), size, colour, checked)
        painter.restore()


def _paint_eye(
    painter: QPainter, cx: float, cy: float, size: float, colour: QColor, filled: bool
) -> None:
    painter.setPen(QPen(colour, 1.6))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    eye_rect = QRectF(cx - size / 2, cy - size / 3, size, size * 2 / 3)
    painter.drawEllipse(eye_rect)
    pupil = size * 0.28
    painter.setBrush(colour if filled else Qt.BrushStyle.NoBrush)
    painter.drawEllipse(QRectF(cx - pupil / 2, cy - pupil / 2, pupil, pupil))


def _paint_star(
    painter: QPainter, cx: float, cy: float, size: float, colour: QColor, filled: bool
) -> None:
    painter.setPen(QPen(colour, 1.4))
    painter.setBrush(colour if filled else Qt.BrushStyle.NoBrush)
    painter.drawPolygon(_star_points(cx, cy, size / 2, size / 4.4))


def _star_points(cx: float, cy: float, outer: float, inner: float) -> QPolygonF:
    points = []
    for index in range(10):
        radius = outer if index % 2 == 0 else inner
        angle = math.pi / 2 + index * math.pi / 5
        points.append(QPointF(cx + radius * math.cos(angle), cy - radius * math.sin(angle)))
    return QPolygonF(points)
