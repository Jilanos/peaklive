"""Code-drawn header icons with one shared sizing and stroke contract.

The header used to reuse text pictograms - a play triangle for both Start and
Follow live, arrows whose apparent size depended on whatever font the platform
resolved. These are painted from vector paths at whatever size and device
pixel ratio the caller asks for, so every action reads at the same weight and
stays crisp at 100, 150 and 200 percent scaling without shipping any raster
artwork.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPoint, QPointF, QRect, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QIconEngine, QPainter, QPen, QPixmap

from peaklive.ui import theme

#: The shared sizing contract (item_142 AC2): one square box for every header
#: action and one icon canvas inside it, so no glyph's apparent size depends
#: on the font the platform happens to resolve.
BUTTON_BOX = 28
ICON_CANVAS = 16
#: Stroke weight, in canvas units, scaled with whatever size is requested.
STROKE = 1.7

Draw = Callable[[QPainter, QRectF, QColor], None]


def _point(rect: QRectF, x: float, y: float) -> QPointF:
    return QPointF(rect.x() + x * rect.width(), rect.y() + y * rect.height())


def _stroke(painter: QPainter, rect: QRectF, colour: QColor) -> None:
    pen = QPen(colour)
    pen.setWidthF(STROKE * rect.width() / ICON_CANVAS)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)


def _fill(painter: QPainter, colour: QColor) -> None:
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(colour)


def _arrow_head(painter: QPainter, rect: QRectF, tip, back, side: float) -> None:
    """A small open chevron at `tip`, opening back towards `back`."""
    painter.drawPolyline([_point(rect, *back), _point(rect, *tip), _point(rect, *side)])


def _draw_play(painter: QPainter, rect: QRectF, colour: QColor) -> None:
    _fill(painter, colour)
    painter.drawPolygon(
        [_point(rect, 0.28, 0.16), _point(rect, 0.28, 0.84), _point(rect, 0.82, 0.50)]
    )


def _draw_stop(painter: QPainter, rect: QRectF, colour: QColor) -> None:
    _fill(painter, colour)
    painter.drawRoundedRect(
        QRectF(_point(rect, 0.26, 0.26), _point(rect, 0.74, 0.74)),
        rect.width() * 0.06,
        rect.width() * 0.06,
    )


def _draw_follow_live(painter: QPainter, rect: QRectF, colour: QColor) -> None:
    """A trace pinned to its newest sample - never a second play triangle."""
    _stroke(painter, rect, colour)
    painter.drawPolyline(
        [
            _point(rect, 0.12, 0.70),
            _point(rect, 0.33, 0.46),
            _point(rect, 0.50, 0.60),
            _point(rect, 0.70, 0.26),
        ]
    )
    painter.drawLine(_point(rect, 0.88, 0.12), _point(rect, 0.88, 0.88))
    _fill(painter, colour)
    painter.drawEllipse(_point(rect, 0.70, 0.26), rect.width() * 0.09, rect.width() * 0.09)


def _draw_fit_xy(painter: QPainter, rect: QRectF, colour: QColor) -> None:
    """Both axes stretched to the data: arrows out on X and on Y."""
    _stroke(painter, rect, colour)
    painter.drawLine(_point(rect, 0.10, 0.50), _point(rect, 0.90, 0.50))
    painter.drawLine(_point(rect, 0.50, 0.10), _point(rect, 0.50, 0.90))
    _arrow_head(painter, rect, (0.10, 0.50), (0.28, 0.36), (0.28, 0.64))
    _arrow_head(painter, rect, (0.90, 0.50), (0.72, 0.36), (0.72, 0.64))
    _arrow_head(painter, rect, (0.50, 0.10), (0.36, 0.28), (0.64, 0.28))
    _arrow_head(painter, rect, (0.50, 0.90), (0.36, 0.72), (0.64, 0.72))


def _draw_fit_y(painter: QPainter, rect: QRectF, colour: QColor) -> None:
    """Only the amplitude axis moves: the time window's edges stay put."""
    _stroke(painter, rect, colour)
    painter.drawLine(_point(rect, 0.14, 0.12), _point(rect, 0.86, 0.12))
    painter.drawLine(_point(rect, 0.14, 0.88), _point(rect, 0.86, 0.88))
    painter.drawLine(_point(rect, 0.50, 0.22), _point(rect, 0.50, 0.78))
    _arrow_head(painter, rect, (0.50, 0.22), (0.36, 0.40), (0.64, 0.40))
    _arrow_head(painter, rect, (0.50, 0.78), (0.36, 0.60), (0.64, 0.60))


def _draw_measurement_values(painter: QPainter, rect: QRectF, colour: QColor) -> None:
    _stroke(painter, rect, colour)
    for y in (0.24, 0.50, 0.76):
        painter.drawLine(_point(rect, 0.14, y), _point(rect, 0.86, y))


def _cursor_drawer(letter: str) -> Draw:
    def draw(painter: QPainter, rect: QRectF, colour: QColor) -> None:
        _stroke(painter, rect, colour)
        painter.drawLine(_point(rect, 0.24, 0.08), _point(rect, 0.24, 0.92))
        font = painter.font()
        font.setPixelSize(max(int(rect.height() * 0.70), 6))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(colour))
        painter.drawText(
            QRectF(_point(rect, 0.34, 0.04), _point(rect, 1.0, 0.96)),
            Qt.AlignmentFlag.AlignCenter,
            letter,
        )

    return draw


DRAWERS: dict[str, Draw] = {
    "play": _draw_play,
    "stop": _draw_stop,
    "follow_live": _draw_follow_live,
    "fit_xy": _draw_fit_xy,
    "fit_y": _draw_fit_y,
    "measurement_values": _draw_measurement_values,
    "cursor_a": _cursor_drawer("A"),
    "cursor_b": _cursor_drawer("B"),
}


class _VectorIconEngine(QIconEngine):
    """Paints one icon from its vector path at whatever size Qt asks for."""

    def __init__(self, draw: Draw, colour: str, disabled: str) -> None:
        super().__init__()
        self._draw = draw
        self._colour = colour
        self._disabled = disabled

    def clone(self) -> QIconEngine:
        return _VectorIconEngine(self._draw, self._colour, self._disabled)

    def paint(self, painter: QPainter, rect: QRect, mode, state) -> None:
        del state
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        colour = self._disabled if mode == QIcon.Mode.Disabled else self._colour
        self._draw(painter, QRectF(rect), QColor(colour))
        painter.restore()

    def pixmap(self, size: QSize, mode, state) -> QPixmap:
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        self.paint(painter, QRect(QPoint(0, 0), size), mode, state)
        painter.end()
        return pixmap


def header_icon(name: str) -> QIcon:
    """The named header icon, drawn in the shared control foreground."""
    return QIcon(_VectorIconEngine(DRAWERS[name], theme.TEXT, theme.DISABLED_TEXT))


def apply_header_icon(button, name: str) -> None:
    """Give `button` the named icon and the shared box/canvas contract.

    The text it replaces was never the control's name - the accessible name
    and tooltip carry that - so dropping it costs nothing and buys a row that
    fits every required control at the supported bench widths.
    """
    button.setIcon(header_icon(name))
    button.setIconSize(QSize(ICON_CANVAS, ICON_CANVAS))
    button.setText("")
    button.setProperty("headerIcon", True)
    button.setFixedSize(BUTTON_BOX, BUTTON_BOX)
