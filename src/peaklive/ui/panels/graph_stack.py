"""Stacked signal plots with shared navigation, stable cursors, and statistics."""

from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from peaklive.analysis import SeriesStore
from peaklive.i18n import translate
from peaklive.ui import theme
from peaklive.ui.panels.measurement import MeasurementPanel
from peaklive.ui.widgets import StateNote

RAW_PREVIEW = "Raw byte 0"
ZOOM_STEP = 1.6


class GraphStackPanel(QWidget):
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
        self._grid = True
        self._plots: dict[str, pg.PlotWidget] = {}
        self._curves: dict[str, pg.PlotDataItem] = {}
        self._cursor_lines: dict[str, tuple[pg.InfiniteLine, pg.InfiniteLine]] = {}
        self._store: SeriesStore | None = None
        self._updating_cursors = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        nav = QHBoxLayout()
        self.zoom_in_button = self._nav("zoomInButton", "graph.zoom_in", "+")
        self.zoom_in_button.clicked.connect(lambda: self.zoom(1 / ZOOM_STEP))
        nav.addWidget(self.zoom_in_button)
        self.zoom_out_button = self._nav("zoomOutButton", "graph.zoom_out", "−")
        self.zoom_out_button.clicked.connect(lambda: self.zoom(ZOOM_STEP))
        nav.addWidget(self.zoom_out_button)
        self.fit_button = self._nav("fitButton", "graph.fit", "⤢")
        self.fit_button.clicked.connect(self.fit)
        nav.addWidget(self.fit_button)

        self.grid_checkbox = QCheckBox(translate("graph.grid"), objectName="gridCheckbox")
        self.grid_checkbox.setToolTip(translate("graph.grid"))
        self.grid_checkbox.setChecked(True)
        self.grid_checkbox.toggled.connect(self.set_grid)
        nav.addWidget(self.grid_checkbox)

        self.follow_checkbox = QCheckBox(translate("graph.follow"), objectName="followCheckbox")
        self.follow_checkbox.setToolTip(translate("graph.follow"))
        self.follow_checkbox.setChecked(True)
        self.follow_checkbox.toggled.connect(self._follow_toggled)
        nav.addWidget(self.follow_checkbox)

        self.cursor_a_button = self._nav("cursorAButton", "graph.cursor_a", "A")
        self.cursor_a_button.clicked.connect(lambda: self.place_cursor("a"))
        nav.addWidget(self.cursor_a_button)
        self.cursor_b_button = self._nav("cursorBButton", "graph.cursor_b", "B")
        self.cursor_b_button.clicked.connect(lambda: self.place_cursor("b"))
        nav.addWidget(self.cursor_b_button)

        self.window_label = QLabel(translate("graph.window_empty"), objectName="windowReadout")
        nav.addWidget(self.window_label)
        self.cursor_summary = QLabel(
            translate("graph.cursor_summary_empty"), objectName="cursorSummary"
        )
        nav.addWidget(self.cursor_summary, 1)
        layout.addLayout(nav)

        self.scroll = QScrollArea(objectName="graphScroll")
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll, 1)

        self.note = StateNote(translate("graph.empty"))
        layout.addWidget(self.note)

        self.measurement = MeasurementPanel()
        layout.addWidget(self.measurement)

    # ---- construction -------------------------------------------------

    def _nav(self, object_name: str, key: str, glyph: str) -> QToolButton:
        button = QToolButton(objectName=object_name)
        button.setProperty("navButton", True)
        button.setText(glyph)
        button.setAccessibleName(translate(key))
        button.setToolTip(translate(key))
        return button

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
            plot.setLabel("bottom", translate("graph.time_axis"), units="s")
            plot.setTitle(signal_name)
            plot.setMinimumHeight(170)
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
            self.container_layout.addWidget(plot)
            self._plots[signal_name] = plot
            self._curves[signal_name] = curve
            self._cursor_lines[signal_name] = (line_a, line_b)
        self.container_layout.addStretch(1)
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
            if self.follow_live:
                self._apply_follow(bounds)
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

    def _apply_follow(self, bounds: tuple[float, float]) -> None:
        anchor = getattr(self, "anchor_plot", None)
        if anchor is None:
            return
        view = anchor.getViewBox()
        current = view.viewRange()[0]
        span = current[1] - current[0]
        full = bounds[1] - bounds[0]
        if span <= 0 or span >= full:
            view.setXRange(bounds[0], bounds[1], padding=0.02)
            return
        view.setXRange(bounds[1] - span, bounds[1], padding=0)

    # ---- navigation ---------------------------------------------------

    def set_grid(self, enabled: bool) -> None:
        self._grid = enabled
        for plot in self._plots.values():
            plot.showGrid(x=enabled, y=enabled, alpha=0.25)

    def zoom(self, factor: float) -> None:
        anchor = getattr(self, "anchor_plot", None)
        if anchor is None:
            return
        self.set_follow_live(False)
        view = anchor.getViewBox()
        low, high = view.viewRange()[0]
        center = (low + high) / 2
        span = max((high - low) * factor, 1e-6)
        view.setXRange(center - span / 2, center + span / 2, padding=0)

    def fit(self) -> None:
        anchor = getattr(self, "anchor_plot", None)
        store = self._store
        if anchor is None or store is None:
            return
        bounds = store.bounds()
        if bounds is None:
            return
        anchor.getViewBox().setXRange(bounds[0], bounds[1], padding=0.02)
        self._refresh_window_label()

    def set_follow_live(self, enabled: bool) -> None:
        if self.follow_live == enabled:
            return
        self.follow_live = enabled
        self.follow_checkbox.blockSignals(True)
        self.follow_checkbox.setChecked(enabled)
        self.follow_checkbox.blockSignals(False)

    def _follow_toggled(self, enabled: bool) -> None:
        self.follow_live = enabled
        if enabled:
            self.refresh_data()

    def visible_window(self) -> tuple[float, float] | None:
        anchor = getattr(self, "anchor_plot", None)
        if anchor is None:
            return None
        low, high = anchor.getViewBox().viewRange()[0]
        return float(low), float(high)

    def _x_range_changed(self) -> None:
        self._refresh_window_label()
        self.view_changed.emit()

    def _refresh_window_label(self) -> None:
        store = self._store
        window = self.visible_window()
        if store is None or window is None or store.bounds() is None:
            self.window_label.setText(translate("graph.window_empty"))
            return
        low, high = window
        full_low, full_high = store.bounds()  # type: ignore[misc]
        full_span = full_high - full_low
        span = high - low
        zoom = full_span / span if span > 0 and full_span > 0 else 1.0
        self.window_label.setText(
            translate("graph.window").format(
                start=f"{low:.3f}s", end=f"{high:.3f}s", zoom=f"{zoom:.1f}"
            )
        )

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
