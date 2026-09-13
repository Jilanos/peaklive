"""Per-lane presentation: a coloured in-plot title overlay and a lane separator.

Replaces pyqtgraph's rotated left-axis title, which becomes illegible once a
few lanes are stacked and which used to carry the full DBC-hash-qualified
signal key into the plot's default hover text. The concise title lives here;
the full technical identity stays reachable through this widget's own tooltip
and accessible name, not through the plot's default hover text.

The title used to be a QLabel in its own layout row above the PlotWidget,
costing every lane a fixed band of height. It is now a small overlay widget
anchored to the drawable ViewBox's own screen geometry (item_128): it carries
no layout height and no autorange padding, tracks the ViewBox's pixel rect
across resize and axis-width changes, and stays put during pan/zoom because
that rect does not move for those gestures - only the data mapping inside it
does. `Qt.WA_TransparentForMouseEvents` lets pan/zoom/cursor-drag gestures
started under the title reach the plot underneath unchanged.
"""

from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from peaklive.analysis import SeriesStore
from peaklive.analysis.dbc import signal_display_title, signal_label
from peaklive.ui import theme

#: A restrained boundary between stacked lanes (item_112 AC2): visible enough
#: to separate adjacent axes/traces, subtle enough not to read as a divider.
LANE_SEPARATOR_STYLE = f"border-bottom: 1px solid {theme.BORDER_SUBTLE};"

#: Inset from the ViewBox's own top-left corner (item_128 AC1): enough to
#: clear the Y-axis ticks and read as inside the plot, not a floating chip.
TITLE_OVERLAY_MARGIN = 4

#: The overlay elides rather than grows past this fraction of the ViewBox
#: width, so a long or duplicate signal name never crowds out the plot itself.
TITLE_OVERLAY_MAX_WIDTH_FRACTION = 0.6

TITLE_OVERLAY_STYLE = (
    "background-color: rgba(8, 13, 19, 0.55);"
    " border-radius: 3px;"
    " padding: 1px 4px;"
    " font-weight: 700;"
)


def lane_identity(store: SeriesStore | None, signal_name: str) -> tuple[str, str]:
    """Return `(title, detail)`: the concise operator title and full technical id.

    `title` defaults to the operator-facing signal name, plus its unit once a
    sample has been decoded and the store knows one. `detail` is the full
    DBC-hash-qualified identity, kept for the lane header's own tooltip.
    """
    title = signal_display_title(signal_name)
    series = store.series(signal_name) if store is not None else None
    if series is not None and series.unit:
        title = f"{title} ({series.unit})"
    return title, signal_label(signal_name)


def build_lane(
    *,
    object_name: str,
    colour: str,
    title: str,
    detail: str,
    plot: pg.PlotWidget,
    is_last: bool,
) -> tuple[QWidget, QLabel]:
    """Wrap `plot` with a coloured in-plot title overlay; return `(lane, header)`.

    `title` is the concise, operator-facing text shown by default; `detail`
    is the full technical identity (DBC hash, frame id) exposed only through
    this header's own tooltip and accessible name - an intentional surface an
    operator reaches deliberately, not the plot's ambient hover text.

    `header` is parented to `plot` itself and positioned by `anchor_lane_title`
    rather than laid out, so it never claims layout height or autorange
    padding; `lane` wraps only `plot`, unchanged in every other respect.
    """
    header = QLabel(title, parent=plot, objectName=f"laneHeader_{object_name}")
    header.setStyleSheet(f"color: {colour};" + TITLE_OVERLAY_STYLE)
    header.setToolTip(detail)
    header.setAccessibleName(detail)
    header.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    header.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    header.raise_()

    lane = QWidget(objectName=f"lane_{object_name}")
    layout = QVBoxLayout(lane)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.addWidget(plot, 1)
    if not is_last:
        lane.setStyleSheet(LANE_SEPARATOR_STYLE)

    anchor_lane_title(plot, header, title)
    view_box = plot.getViewBox()
    if view_box is not None:
        view_box.sigResized.connect(lambda: anchor_lane_title(plot, header, title))
    return lane, header


def anchor_lane_title(plot: pg.PlotWidget, header: QLabel, title: str) -> None:
    """Pin `header` inside the top-left of `plot`'s drawable ViewBox.

    Reads the ViewBox's current screen rect (its pixel geometry within
    `plot`, which pan/zoom never change - only resize and axis-width layout
    do) and places `header` `TITLE_OVERLAY_MARGIN` inside it, eliding `title`
    to stay within a bounded fraction of the ViewBox's own width.
    """
    view_box = plot.getViewBox()
    if view_box is None:
        return
    rect = plot.mapFromScene(view_box.sceneBoundingRect()).boundingRect()
    if rect.width() <= 0 or rect.height() <= 0:
        return
    max_width = max(int(rect.width() * TITLE_OVERLAY_MAX_WIDTH_FRACTION), 0)
    elided = header.fontMetrics().elidedText(title, Qt.TextElideMode.ElideRight, max_width)
    header.setText(elided)
    header.adjustSize()
    x = int(rect.left()) + TITLE_OVERLAY_MARGIN
    y = int(rect.top()) + TITLE_OVERLAY_MARGIN
    header.move(x, y)
