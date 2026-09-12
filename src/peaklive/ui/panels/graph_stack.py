from __future__ import annotations  # noqa: I001
from collections import OrderedDict
import pyqtgraph as pg
from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QLabel, QSizePolicy, QToolButton, QVBoxLayout, QWidget
from peaklive.analysis import HistoricalSignalStore, SeriesStore
from peaklive.i18n import translate
from peaklive.services.history_worker import HistoryViewportWorker
from peaklive.ui import theme
from peaklive.ui.panels.graph_controls import GraphControlsBar
from peaklive.ui.panels.graph_history import curve_points, viewport
from peaklive.ui.panels.graph_lane_header import build_lane, lane_identity
from peaklive.ui.panels.graph_navigation import AXIS_CAPTURE, GraphNavigation
from peaklive.ui.panels.measurement import MeasurementPanel
from peaklive.ui.widgets import StateNote
from peaklive.ui.worker_lifecycle import abandon_worker
RAW_PREVIEW, PLOT_AREA_MINIMUM_HEIGHT, SHARED_LEFT_AXIS_WIDTH, MEASUREMENT_REFRESH_INTERVAL_MS = "Raw byte 0", 180, 88, 250  # noqa: E501
class GraphStackPanel(GraphNavigation, QWidget):
    cursors_changed = Signal()
    view_changed = Signal()
    measurement_visibility_changed = Signal(bool)
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.cursor_a: float | None = None
        self.cursor_b: float | None = None
        self.follow_live = True
        self._axis_mode = AXIS_CAPTURE
        self._live_extent_end = 0.0
        self._window_chosen = False
        self._applying_range = False
        self._plots: dict[str, pg.PlotWidget] = {}
        self._lane_headers: dict[str, QLabel] = {}
        self._curves: dict[str, pg.PlotDataItem] = {}
        self._cursor_lines: dict[str, tuple[pg.InfiniteLine, pg.InfiniteLine]] = {}
        self._store: SeriesStore | None = None
        self._history: HistoricalSignalStore | None = None
        self._updating_cursors = False
        self._measurement_dirty = False
        self._measurement_refresh_timer = QTimer(self)
        self._measurement_refresh_timer.setInterval(MEASUREMENT_REFRESH_INTERVAL_MS)
        self._measurement_refresh_timer.timeout.connect(self._flush_measurements)
        self._viewport_refresh_timer = QTimer(self)
        self._viewport_refresh_timer.setSingleShot(True)
        self._viewport_refresh_timer.setInterval(75)
        self._viewport_refresh_timer.timeout.connect(self.refresh_data)
        self._history_worker: HistoryViewportWorker | None = None
        self._history_generation = 0
        self._history_result_cache: OrderedDict[tuple, dict] = OrderedDict()
        self._history_result_cache_points = 0
        self._history_result_cache_limit = 64_000
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.controls = GraphControlsBar()
        self.fit_button.clicked.connect(self.fit)
        self.fit_y_button.clicked.connect(self.fit_y)
        self.follow_checkbox.toggled.connect(self._follow_toggled)
        self.cursor_a_button.clicked.connect(lambda: self.place_cursor("a"))
        self.cursor_b_button.clicked.connect(lambda: self.place_cursor("b"))
        self.measurement_visibility_button.toggled.connect(self._measurement_visibility_toggled)
        layout.addWidget(self.controls)
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
    @property
    def fit_button(self) -> QToolButton:
        return self.controls.fit_button
    @property
    def fit_y_button(self) -> QToolButton:
        return self.controls.fit_y_button
    @property
    def measurement_visibility_button(self) -> QToolButton:
        return self.controls.measurement_visibility_button
    @property
    def cursor_a_button(self) -> QToolButton:
        return self.controls.cursor_a_button
    @property
    def cursor_b_button(self) -> QToolButton:
        return self.controls.cursor_b_button
    @property
    def follow_checkbox(self) -> QToolButton:
        return self.controls.follow_checkbox
    @property
    def cursor_summary(self) -> QLabel:
        return self.controls.cursor_summary
    @property
    def empty_state_label(self) -> QLabel:
        return self.controls.empty_state_label
    @property
    def plots(self) -> dict[str, pg.PlotWidget]:
        return self._plots
    @property
    def curves(self) -> dict[str, pg.PlotDataItem]:
        return self._curves
    @property
    def signal_names(self) -> tuple[str, ...]:
        return tuple(self._plots)
    @property
    def lane_headers(self) -> dict[str, QLabel]:
        return self._lane_headers
    def sync(self, store: SeriesStore, shown: set[str]) -> None:
        """Rebuild one plot per shown signal, keeping the cursors where they are."""
        self._store = store
        wanted = sorted(shown) or [RAW_PREVIEW]
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        self._plots.clear()
        self._lane_headers.clear()
        self._curves.clear()
        self._cursor_lines.clear()
        anchor: pg.PlotWidget | None = None
        for index, signal_name in enumerate(wanted):
            colour = theme.TRACE_PALETTE[index % len(theme.TRACE_PALETTE)]
            object_name = (
                signal_name.replace(".", "_")
                .replace(":", "_")
                .replace("[", "_")
                .replace("]", "_")
                .replace(" ", "_")
            )
            title, detail = lane_identity(self._store, signal_name)
            plot = pg.PlotWidget(objectName=f"livePlot_{object_name}")
            plot.setAccessibleName(translate("graph.plot_accessible"))
            plot.setBackground(theme.PLOT_BACKGROUND)
            plot.showGrid(x=True, y=True, alpha=0.25)
            plot.getAxis("left").setWidth(SHARED_LEFT_AXIS_WIDTH)
            plot.getViewBox().enableAutoRange(x=False)
            plot.setToolTip(translate("graph.trace_colour").format(signal=title, colour=colour))
            plot.setMinimumHeight(0)
            plot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            curve = plot.plot(pen=pg.mkPen(colour, width=2))
            curve.setClipToView(True)
            curve.setDownsampling(auto=True, method="peak")
            line_a = pg.InfiniteLine(pos=0.0, angle=90, movable=True, pen=pg.mkPen(theme.CURSOR_A))
            line_b = pg.InfiniteLine(pos=0.0, angle=90, movable=True, pen=pg.mkPen(theme.CURSOR_B))
            plot.addItem(line_a)
            plot.addItem(line_b)
            line_a.sigPositionChanged.connect(lambda line: self._cursor_dragged("a", line))
            line_b.sigPositionChanged.connect(lambda line: self._cursor_dragged("b", line))
            plot._peaklive_cursor_a = line_a  # type: ignore[attr-defined]
            plot._peaklive_cursor_b = line_b  # type: ignore[attr-defined]
            if anchor is None:
                anchor = plot
            else:
                plot.setXLink(anchor)
            plot.getViewBox().sigXRangeChanged.connect(self._x_range_changed)
            lane, header = build_lane(
                object_name=object_name,
                colour=colour,
                title=title,
                detail=detail,
                plot=plot,
                is_last=index == len(wanted) - 1,
            )
            self.container_layout.addWidget(lane, 1)
            self._plots[signal_name] = plot
            self._lane_headers[signal_name] = header
            self._curves[signal_name] = curve
            self._cursor_lines[signal_name] = (line_a, line_b)
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
    def closeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self.cancel_history_refresh()
        super().closeEvent(event)
    def request_view_refresh(self) -> None:
        self._viewport_refresh_timer.start()
    def cancel_history_refresh(self) -> None:
        self._history_generation += 1
        self._history_result_cache.clear()
        self._history_result_cache_points = 0
        worker = self._history_worker
        if worker is not None and worker.isRunning():
            worker.request_cancel()
            abandon_worker(worker)
        self._history_worker = None
    def refresh_data(self) -> None:
        """Push the retained samples into the curves without moving the cursors."""
        store = self._store
        if store is None:
            return
        if self._history is not None:
            extent, visible = viewport(
                self._history, self.global_extent(), self._window_chosen, self.visible_window()
            )
            if extent is not None and visible is not None:
                key = (str(self._history.path), tuple(self._curves), extent, visible)
                cached = self._history_result_cache.get(key)
                if cached is not None:
                    self._history_result_cache.move_to_end(key)
                    self._historical_refresh_completed(cached, self._history_generation)
                    return
                self._history_generation += 1
                generation = self._history_generation
                old = self._history_worker
                if old is not None and old.isRunning():
                    old.request_cancel()
                worker = HistoryViewportWorker(
                    self._history.path, tuple(self._curves), extent, visible, generation
                )
                worker.completed.connect(self._historical_refresh_completed)
                worker.finished.connect(self._history_worker_finished)
                self._history_worker = worker
                worker.start()
                abandon_worker(worker)
            return
        has_sample = False
        extent, visible = viewport(
            self._history, self.global_extent(), self._window_chosen, self.visible_window()
        )
        for signal_name, curve in self._curves.items():
            # Live samples are raw and unreduced: the automatic peak reducer
            # is pyqtgraph's only display-time reduction here, so it stays on.
            curve.setDownsampling(auto=True, method="peak")
            points = curve_points(self._history, store, signal_name, extent, visible)
            if points is not None:
                curve.setData(*points)
                has_sample = True
                continue
            curve.setData([], [])
        bounds = extent or store.bounds()
        if bounds is not None:
            self._seed_cursors(bounds)
        extent = self.global_extent()
        if extent is not None and self.follow_live:
            self._apply_follow(extent)
        self.note.setVisible(not has_sample)
        self.empty_state_label.setVisible(not has_sample)
        if not has_sample:
            self.note.show_message(translate("graph.empty"), "info")
            self.empty_state_label.setText(translate("graph.empty"))
        self._mark_measurements_dirty()
    def _historical_refresh_completed(self, points_by_signal: dict, generation: int) -> None:
        if generation != self._history_generation or self._history is None:
            return
        key = (
            str(self._history.path), tuple(self._curves),
            self.global_extent(), self.visible_window()
        )
        self._history_result_cache[key] = points_by_signal
        self._history_result_cache.move_to_end(key)
        self._history_result_cache_points += sum(
            len(points or ()) for points in points_by_signal.values()
        )
        while self._history_result_cache_points > self._history_result_cache_limit:
            _, removed = self._history_result_cache.popitem(last=False)
            self._history_result_cache_points -= sum(
                len(points or ()) for points in removed.values()
            )
        for signal_name, curve in self._curves.items():
            # Historical envelopes/exact ranges are already reduced to a
            # pixel-aware budget upstream (HistoricalSignalStore.overview);
            # pyqtgraph's own automatic peak reducer must not run a second
            # time on this prepared result, or it can erase a nonempty sparse
            # envelope entirely (factor > point count => zero display points).
            curve.setDownsampling(auto=False)
            points = points_by_signal.get(signal_name)
            if not points:
                curve.setData([], [])
                continue
            curve.setData(
                [timestamp for timestamp, _ in points],
                [
                    float(value)
                    if isinstance(value, int | float) and not isinstance(value, bool)
                    else 0.0
                    for _, value in points
                ],
            )
        bounds = self.global_extent()
        if bounds is not None:
            self._seed_cursors(bounds)
        self.note.setVisible(not any(points_by_signal.values()))
        self.empty_state_label.setVisible(not any(points_by_signal.values()))
        self._mark_measurements_dirty()
    def _history_worker_finished(self) -> None:
        worker = self._history_worker
        if worker is not None and not worker.isRunning():
            self._history_worker = None
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
        self._mark_measurements_dirty()
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
            self.cursor_summary.setMinimumWidth(0)
            return
        text = translate("graph.cursor_summary").format(
            cursor_a=f"{self.cursor_a:.3f}s",
            cursor_b=f"{self.cursor_b:.3f}s",
        )
        self.cursor_summary.setText(text)
        self.cursor_summary.setMinimumWidth(
            self.cursor_summary.fontMetrics().horizontalAdvance(text) + 4
        )
    @property
    def cursor_range(self) -> tuple[float, float] | None:
        if self.cursor_a is None or self.cursor_b is None:
            return None
        return min(self.cursor_a, self.cursor_b), max(self.cursor_a, self.cursor_b)
    def refresh_measurements(self) -> None:
        store = self._store
        if self._history is not None and self.cursor_a is not None and self.cursor_b is not None:
            exact_store = SeriesStore()
            for signal_name in self._plots:
                points = self._history.exact(
                    signal_name, self.cursor_a, self.cursor_b, limit=20_000
                )
                if points:
                    exact_store.replace(signal_name, points)
            if any(exact_store.series(name) for name in self._plots):
                store = exact_store
        self.measurement.refresh(
            store, tuple(self._plots), self.cursor_a, self.cursor_b
        )
    def _mark_measurements_dirty(self) -> None:
        """Ask for a recompute without performing one per request.
        A live stream can call this every 20Hz graph-refresh tick, and a
        cursor drag every pointer-move tick; either way, at most one
        recompute happens per `MEASUREMENT_REFRESH_INTERVAL_MS`.
        """
        self._measurement_dirty = True
        if not self._measurement_refresh_timer.isActive():
            self._measurement_refresh_timer.start()
    def _flush_measurements(self) -> None:
        if not self._measurement_dirty:
            self._measurement_refresh_timer.stop()
            return
        self._measurement_dirty = False
        self.refresh_measurements()
    def set_measurement_values_visible(self, visible: bool) -> None:
        """Hide or restore the values/statistics table, never the cursor lines.
        The A/B `InfiniteLine`s live on each plot and are untouched here: only
        `MeasurementPanel`'s own presentation is toggled.
        """
        self.measurement_visibility_button.blockSignals(True)
        self.measurement_visibility_button.setChecked(visible)
        self.measurement_visibility_button.blockSignals(False)
        self.measurement.set_values_visible(visible)
    def _measurement_visibility_toggled(self, visible: bool) -> None:
        self.measurement.set_values_visible(visible)
        self.measurement_visibility_changed.emit(visible)
