"""Per-lane presentation: a coloured horizontal title and an inter-lane separator.

Replaces pyqtgraph's rotated left-axis title, which becomes illegible once a
few lanes are stacked and which used to carry the full DBC-hash-qualified
signal key into the plot's default hover text. The concise title lives here;
the full technical identity stays reachable through this widget's own tooltip
and accessible name, not through the plot's default hover text.
"""

from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from peaklive.analysis import SeriesStore
from peaklive.analysis.dbc import signal_display_title, signal_label
from peaklive.ui import theme

#: A restrained boundary between stacked lanes (item_112 AC2): visible enough
#: to separate adjacent axes/traces, subtle enough not to read as a divider.
LANE_SEPARATOR_STYLE = f"border-bottom: 1px solid {theme.BORDER_SUBTLE};"


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
    """Wrap `plot` with a coloured lane header; return `(lane, header)`.

    `title` is the concise, operator-facing text shown by default; `detail`
    is the full technical identity (DBC hash, frame id) exposed only through
    this header's own tooltip and accessible name - an intentional surface an
    operator reaches deliberately, not the plot's ambient hover text.
    """
    header = QLabel(title, objectName=f"laneHeader_{object_name}")
    header.setStyleSheet(f"color: {colour}; font-weight: 700; padding: 2px 4px;")
    header.setToolTip(detail)
    header.setAccessibleName(detail)

    lane = QWidget(objectName=f"lane_{object_name}")
    layout = QVBoxLayout(lane)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.addWidget(header)
    layout.addWidget(plot, 1)
    if not is_last:
        lane.setStyleSheet(LANE_SEPARATOR_STYLE)
    return lane, header
