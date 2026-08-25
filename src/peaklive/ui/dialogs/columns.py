"""Trace column configuration: visibility, order, width, and value format."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from peaklive.domain import TRACE_COLUMN_FORMATS, TraceColumn, default_trace_columns
from peaklive.i18n import translate

FORMAT_LABELS = {
    "time": "columns.format_time",
    "hex": "columns.format_hex",
    "dec": "columns.format_dec",
    "bin": "columns.format_bin",
    "status": "columns.format_status",
    "text": "columns.format_text",
}


class ColumnsDialog(QDialog):
    """Edits the trace column set in place and reports every change immediately."""

    columns_changed = Signal()

    def __init__(self, columns: list[TraceColumn], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("columnsDialog")
        self.setWindowTitle(translate("columns.title"))
        self.columns = columns
        layout = QVBoxLayout(self)
        self.grid_host = QWidget(objectName="columnsGrid")
        layout.addWidget(self.grid_host)

        actions = QHBoxLayout()
        self.reset_button = QPushButton(translate("columns.reset"), objectName="columnsReset")
        self.reset_button.clicked.connect(self._reset)
        actions.addWidget(self.reset_button)
        actions.addStretch(1)
        self.close_button = QPushButton(translate("columns.close"), objectName="columnsClose")
        self.close_button.setDefault(True)
        self.close_button.clicked.connect(self.accept)
        actions.addWidget(self.close_button)
        layout.addLayout(actions)

        self._rebuild()

    def _rebuild(self) -> None:
        old_layout = self.grid_host.layout()
        if old_layout is not None:
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
            old_layout.deleteLater()
        grid = QGridLayout(self.grid_host)
        grid.addWidget(QLabel(translate("columns.visible")), 0, 0)
        grid.addWidget(QLabel(translate("columns.column")), 0, 1)
        grid.addWidget(QLabel(translate("columns.width")), 0, 2)
        grid.addWidget(QLabel(translate("columns.format")), 0, 3)
        for row, column in enumerate(self.columns, start=1):
            visible = QCheckBox(objectName=f"columnVisible_{column.key}")
            visible.setChecked(column.visible)
            visible.setAccessibleName(translate(f"trace.column_{column.key}"))
            visible.toggled.connect(
                lambda checked, key=column.key: self._set_visible(key, checked)
            )
            grid.addWidget(visible, row, 0)
            grid.addWidget(QLabel(translate(f"trace.column_{column.key}")), row, 1)

            width = QSpinBox(objectName=f"columnWidth_{column.key}")
            width.setRange(20, 600)
            width.setValue(column.width)
            width.setAccessibleName(translate("columns.width"))
            width.valueChanged.connect(lambda value, key=column.key: self._set_width(key, value))
            grid.addWidget(width, row, 2)

            formats = TRACE_COLUMN_FORMATS.get(column.key, ("text",))
            selector = QComboBox(objectName=f"columnFormat_{column.key}")
            selector.setAccessibleName(translate("columns.format"))
            for value_format in formats:
                selector.addItem(translate(FORMAT_LABELS[value_format]), value_format)
            selector.setCurrentIndex(max(0, selector.findData(column.value_format)))
            selector.setEnabled(len(formats) > 1)
            selector.currentIndexChanged.connect(
                lambda _index, key=column.key, box=selector: self._set_format(
                    key, str(box.currentData())
                )
            )
            grid.addWidget(selector, row, 3)

            up = QPushButton("▲", objectName=f"columnUp_{column.key}")
            up.setAccessibleName(translate("columns.move_up"))
            up.setToolTip(translate("columns.move_up"))
            up.clicked.connect(lambda _=False, key=column.key: self._move(key, -1))
            grid.addWidget(up, row, 4)
            down = QPushButton("▼", objectName=f"columnDown_{column.key}")
            down.setAccessibleName(translate("columns.move_down"))
            down.setToolTip(translate("columns.move_down"))
            down.clicked.connect(lambda _=False, key=column.key: self._move(key, 1))
            grid.addWidget(down, row, 5)

    def _column(self, key: str) -> TraceColumn:
        return next(column for column in self.columns if column.key == key)

    def _set_visible(self, key: str, visible: bool) -> None:
        self._column(key).visible = visible
        self.columns_changed.emit()

    def _set_width(self, key: str, width: int) -> None:
        self._column(key).width = width
        self.columns_changed.emit()

    def _set_format(self, key: str, value_format: str) -> None:
        self._column(key).value_format = value_format
        self.columns_changed.emit()

    def _move(self, key: str, offset: int) -> None:
        index = next(i for i, column in enumerate(self.columns) if column.key == key)
        target = index + offset
        if not 0 <= target < len(self.columns):
            return
        self.columns[index], self.columns[target] = self.columns[target], self.columns[index]
        self._rebuild()
        self.columns_changed.emit()

    def _reset(self) -> None:
        self.columns[:] = default_trace_columns()
        self._rebuild()
        self.columns_changed.emit()
