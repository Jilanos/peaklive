"""Stacked signal plots with shared navigation, stable cursors, and statistics."""

from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QLabel,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from peaklive.analysis import SeriesStore
from peaklive.i18n import translate
from peaklive.ui import theme
from peaklive.ui.panels.graph_controls import GraphControlsBar
from peaklive.ui.panels.graph_navigation import AXIS_CAPTURE, ZOOM_STEP, GraphNavigation
from peaklive.ui.panels.measurement import MeasurementPanel
from peaklive.ui.widgets import StateNote

RAW_PREVIEW = "Raw byte 0"

#: Below this a plot is a strip, not a trace to read against a cursor.
PLOT_AREA_MINIMUM_HEIGHT = 180

#: Every lane reserves the same left geometry. Without it pyqtgraph sizes
#: AxisItems from their own ticks and labels, shifting time grids and cursors.
SHARED_LEFT_AXIS_WIDTH = 88


class GraphStackPanel(GraphNavigation, QWidget):
    """One plot per shown signal on a shared time axis, plus the A/B measurement.

    Cursor positions live here, not in the plots: they are placed by the
    operator, survive every incoming batch, and are restored from the profile.
    Only the very first sample seeds them, which is why a live measurement no
    longer collapses onto the newest data.
    """

    cursors_changed = Signal()
    view_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.cursor_a: float | None = None
        self.cursor_b: float | None = None
        self.follow_live = True
        self._axis_mode = AXIS_CAPTURE
        self._live_extent_end = 0.0
        self._window_chosen = False
        self._grid = True
        self._plots: dict[str, pg.PlotWidget] = {}
        self._curves: dict[str, pg.PlotDataItem] = {}
        self._cursor_lines: dict[str, tuple[pg.InfiniteLine, pg.InfiniteLine]] = {}
        self._store: SeriesStore | None = None
        self._updating_cursors = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.controls = GraphControlsBar()
        self.zoom_in_button.clicked.connect(lambda: self.zoom(1 / ZOOM_STEP))
        self.zoom_out_button.clicked.connect(lambda: self.zoom(ZOOM_STEP))
        self.fit_button.clicked.connect(self.fit)
        self.grid_checkbox.toggled.connect(self.set_grid)
        self.follow_checkbox.toggled.connect(self._follow_toggled)
        self.cursor_a_button.clicked.connect(lambda: self.place_cursor("a"))
        self.cursor_b_button.clicked.connect(lambda: self.place_cursor("b"))
        layout.addWidget(self.controls)

        # This is intentionally a single surface, not a scroll area full of
        # plot cards. A graph list makes operators scroll *between* signals,
        # repeats the time axis, and leaves light bands between the cards.
        # Stacked linked plots resize together instead, just like a scope.
        self.scroll = QWidget(objectName="graphCanvas")
        self.scroll.setMinimumHeight(PLOT_AREA_MINIMUM_HEIGHT)
        self.container = self.scroll
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        layout.addWidget(self.scroll, 1)

        self.note = StateNote(translate("graph.empty"))
        layout.addWidget(self.note)

        self.measurement = MeasurementPanel()
        layout.addWidget(self.measurement)

    # ---- construction -------------------------------------------------

    @property
    def zoom_in_button(self) -> QToolButton:
        return self.controls.zoom_in_button

    @property
    def zoom_out_button(self) -> QToolButton:
        return self.controls.zoom_out_button

    @property
    def fit_button(self) -> QToolButton:
        return self.controls.fit_button

    @property
    def cursor_a_button(self) -> QToolButton:
        return self.controls.cursor_a_button

    @property
    def cursor_b_button(self) -> QToolButton:
        return self.controls.cursor_b_button

    @property
    def grid_checkbox(self) -> QToolButton:
        return self.controls.grid_checkbox

    @property
    def follow_checkbox(self) -> QToolButton:
        return self.controls.follow_checkbox

    @property
    def window_label(self) -> QLabel:
        return self.controls.window_label

    @property
    def cursor_summary(self) -> QLabel:
        return self.controls.cursor_summary

    @property
    def plots(self) -> dict[str, pg.PlotWidget]:
        return self._plots

    @property
    def curves(self) -> dict[str, pg.PlotDataItem]:
        return self._curves

    @property
    def signal_names(self) -> tuple[str, ...]:
        return tuple(self._plots)

    def sync(self, store: SeriesStore, shown: set[str]) -> None:
        """Rebuild one plot per shown signal, keeping the cursors where they are."""
        self._store = store
        wanted = sorted(shown) or [RAW_PREVIEW]
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        self._plots.clear()
        self._curves.clear()
        self._cursor_lines.clear()
        anchor: pg.PlotWidget | None = None
        for signal_name in wanted:
            plot = pg.PlotWidget(objectName=f"livePlot_{signal_name.replace('.', '_')}")
            plot.setAccessibleName(translate("graph.plot_accessible"))
            plot.setBackground(theme.PLOT_BACKGROUND)
            plot.showGrid(x=self._grid, y=self._grid, alpha=0.25)
            plot.setLabel("left", signal_name)
            plot.getAxis("left").setWidth(SHARED_LEFT_AXIS_WIDTH)
            plot.setMinimumHeight(0)
            plot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            curve = plot.plot(pen=pg.mkPen(theme.CURVE, width=2))
            line_a = pg.InfiniteLine(
                pos=0.0, angle=90, movable=True, pen=pg.mkPen(theme.CURSOR_A)
            )
            line_b = pg.InfiniteLine(
                pos=0.0, angle=90, movable=True, pen=pg.mkPen(theme.CURSOR_B)
            )
            plot.addItem(line_a)
            plot.addItem(line_b)
            line_a.sigPositionChanged.connect(lambda line: self._cursor_dragged("a", line))
            line_b.sigPositionChanged.connect(lambda line: self._cursor_dragged("b", line))
            # The parity suite and older tests reach for these by name.
            plot._peaklive_cursor_a = line_a  # type: ignore[attr-defined]
            plot._peaklive_cursor_b = line_b  # type: ignore[attr-defined]
            if anchor is None:
                anchor = plot
            else:
                plot.setXLink(anchor)
            plot.getViewBox().sigXRangeChanged.connect(self._x_range_changed)
            self.container_layout.addWidget(plot, 1)
            self._plots[signal_name] = plot
            self._curves[signal_name] = curve
            self._cursor_lines[signal_name] = (line_a, line_b)
        # One time axis is enough when all lanes are X-linked. Hiding every
        # other axis both removes repeated labels and gives curves more room.
        for index, plot in enumerate(self._plots.values()):
            axis = plot.getAxis("bottom")
            is_bottom = index == len(self._plots) - 1
            axis.setStyle(showValues=is_bottom)
            axis.setHeight(None if is_bottom else 0)
            if is_bottom:
                plot.setLabel("bottom", translate("graph.time_axis"), units="s")
        self.anchor_plot = anchor
        self._apply_cursor_lines()
        self.refresh_data()

    # ---- data ---------------------------------------------------------

    def refresh_data(self) -> None:
        """Push the retained samples into the curves without moving the cursors."""
        store = self._store
        if store is None:
            return
        has_sample = False
        for signal_name, curve in self._curves.items():
            series = store.series(signal_name)
            if series is None or not len(series):
                curve.setData([], [])
                continue
            has_sample = True
            curve.setData(series.times, series.numeric_values)
        bounds = store.bounds()
        if bounds is not None:
            self._seed_cursors(bounds)
        extent = self.global_extent()
        if extent is not None and self.follow_live:
            self._apply_follow(extent)
        self.note.setVisible(not has_sample)
        if not has_sample:
            self.note.show_message(translate("graph.empty"), "info")
        self._refresh_window_label()
        self.refresh_measurements()

    def _seed_cursors(self, bounds: tuple[float, float]) -> None:
        """Seed unplaced cursors once; never re-pin a cursor the operator moved."""
        changed = False
        if self.cursor_a is None:
            self.cursor_a = bounds[0]
            changed = True
        if self.cursor_b is None:
            self.cursor_b = bounds[1]
            changed = True
        if changed:
            self._apply_cursor_lines()

    # ---- navigation ---------------------------------------------------

    def set_grid(self, enabled: bool) -> None:
        self._grid = enabled
        for plot in self._plots.values():
            plot.showGrid(x=enabled, y=enabled, alpha=0.25)

    # ---- cursors ------------------------------------------------------

    def place_cursor(self, which: str, position: float | None = None) -> None:
        """Place a cursor, defaulting to the centre of the visible window."""
        if position is None:
            window = self.visible_window()
            if window is None:
                return
            position = (window[0] + window[1]) / 2
        if which == "a":
            self.cursor_a = float(position)
        else:
            self.cursor_b = float(position)
        self._apply_cursor_lines()
        self.refresh_measurements()
        self.cursors_changed.emit()

    def restore_cursors(self, cursor_a: float | None, cursor_b: float | None) -> None:
        self.cursor_a = cursor_a
        self.cursor_b = cursor_b
        self._apply_cursor_lines()
        self.refresh_measurements()

    def _cursor_dragged(self, which: str, line: pg.InfiniteLine) -> None:
        if self._updating_cursors:
            return
        position = float(line.value())
        if which == "a":
            self.cursor_a = position
        else:
            self.cursor_b = position
        self._apply_cursor_lines()
        self.refresh_measurements()
        self.cursors_changed.emit()

    def _apply_cursor_lines(self) -> None:
        self._updating_cursors = True
        try:
            for line_a, line_b in self._cursor_lines.values():
                if self.cursor_a is not None:
                    line_a.setValue(self.cursor_a)
                if self.cursor_b is not None:
                    line_b.setValue(self.cursor_b)
        finally:
            self._updating_cursors = False
        self._refresh_cursor_summary()

    def _refresh_cursor_summary(self) -> None:
        if self.cursor_a is None or self.cursor_b is None:
            self.cursor_summary.setText(translate("graph.cursor_summary_empty"))
            return
        self.cursor_summary.setText(
            translate("graph.cursor_summary").format(
                cursor_a=f"{self.cursor_a:.3f}s",
                cursor_b=f"{self.cursor_b:.3f}s",
                delta=f"{abs(self.cursor_b - self.cursor_a):.3f}s",
            )
        )

    @property
    def cursor_range(self) -> tuple[float, float] | None:
        if self.cursor_a is None or self.cursor_b is None:
            return None
        return min(self.cursor_a, self.cursor_b), max(self.cursor_a, self.cursor_b)

    def refresh_measurements(self) -> None:
        self.measurement.refresh(
            self._store, tuple(self._plots), self.cursor_a, self.cursor_b
        )
