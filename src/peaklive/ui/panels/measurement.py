"""The A/B measurement table: cursor values plus range statistics."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from peaklive.analysis import RangeStatistics, SeriesStore, range_statistics
from peaklive.analysis.statistics import numeric_delta
from peaklive.i18n import translate

MEASURE_COLUMNS = (
    "measure.column_signal",
    "measure.column_a",
    "measure.column_b",
    "measure.column_delta",
    "measure.column_count",
    "measure.column_min",
    "measure.column_max",
    "measure.column_mean",
    "measure.column_std",
    "measure.column_rms",
)
STATS_FIRST_COLUMN = 5


class MeasurementPanel(QWidget):
    """One row per shown signal: value at A, value at B, delta, and A-B statistics.

    Numeric signals get count, min, max, mean, standard deviation, and RMS.
    Enumerated or textual signals get a value distribution instead, because a
    mean over state names would be noise dressed as a measurement.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.range_label = QLabel(translate("measure.needs_cursors"), objectName="rangeLabel")
        layout.addWidget(self.range_label)
        self.table = QTableWidget(0, len(MEASURE_COLUMNS), objectName="measureTable")
        self.table.setAccessibleName(translate("measure.accessible"))
        self.table.setHorizontalHeaderLabels([translate(key) for key in MEASURE_COLUMNS])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self.table.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        # The plots are the workspace; the statistics read under them.
        self.table.setMaximumHeight(140)
        layout.addWidget(self.table)

    def set_values_visible(self, visible: bool) -> None:
        """Hide or restore the values/statistics presentation.

        This never touches the A/B cursor lines: those live on the plots in
        `GraphStackPanel`, one level up, and this panel has no reach into
        them. Hiding only clears clutter from the read - it changes no
        computed value, cursor position, or export.
        """
        self.range_label.setVisible(visible)
        self.table.setVisible(visible)

    def refresh(
        self,
        store: SeriesStore | None,
        signal_names: tuple[str, ...],
        cursor_a: float | None,
        cursor_b: float | None,
    ) -> None:
        self.table.clearSpans()
        self.table.setRowCount(0)
        cursor_range = (
            None
            if cursor_a is None or cursor_b is None
            else (min(cursor_a, cursor_b), max(cursor_a, cursor_b))
        )
        if cursor_range is None:
            self.range_label.setText(translate("measure.needs_cursors"))
        else:
            self.range_label.setText(
                translate("measure.range").format(
                    start=f"{cursor_range[0]:.3f}s", end=f"{cursor_range[1]:.3f}s"
                )
            )
        if store is None:
            return
        for signal_name in signal_names:
            series = store.series(signal_name)
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(signal_name))
            self.table.item(row, 0).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
            if series is None or not len(series):
                self.table.setItem(row, 1, QTableWidgetItem(translate("measure.no_sample")))
                self.table.item(row, 1).setTextAlignment(Qt.AlignmentFlag.AlignRight)
                continue
            value_a = series.nearest(cursor_a) if cursor_a is not None else None
            value_b = series.nearest(cursor_b) if cursor_b is not None else None
            self.table.setItem(row, 1, QTableWidgetItem(_sample_text(value_a)))
            self.table.setItem(row, 2, QTableWidgetItem(_sample_text(value_b)))
            delta = (
                numeric_delta(value_a[1], value_b[1])
                if value_a is not None and value_b is not None
                else None
            )
            self.table.setItem(row, 3, QTableWidgetItem(_number_text(delta)))
            for column in range(1, len(MEASURE_COLUMNS)):
                item = self.table.item(row, column)
                if item is not None:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            if cursor_range is None:
                continue
            self._write_statistics(row, range_statistics(series, *cursor_range))

    def _write_statistics(self, row: int, stats: RangeStatistics) -> None:
        self.table.setItem(row, 4, QTableWidgetItem(str(stats.count)))
        if not stats.count:
            self.table.setItem(
                row, STATS_FIRST_COLUMN, QTableWidgetItem(translate("measure.no_sample"))
            )
            return
        if not stats.is_numeric:
            self.table.setItem(
                row, STATS_FIRST_COLUMN, QTableWidgetItem(stats.distribution_text)
            )
            self.table.setSpan(row, STATS_FIRST_COLUMN, 1, 5)
            return
        for column, value in enumerate(
            (stats.minimum, stats.maximum, stats.mean, stats.std, stats.rms),
            start=STATS_FIRST_COLUMN,
        ):
            self.table.setItem(row, column, QTableWidgetItem(_number_text(value)))


def _sample_text(sample: tuple[float, Any] | None) -> str:
    if sample is None:
        return "—"
    _, value = sample
    if isinstance(value, int | float) and not isinstance(value, bool):
        return f"{float(value):.6g}"
    return str(value)


def _number_text(value: float | None) -> str:
    return "—" if value is None else f"{value:.6g}"
