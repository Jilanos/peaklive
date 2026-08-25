"""The trace view: display-only filters, active chips, columns, and selection."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from peaklive.analysis import DECODE_DECODED, DECODE_UNKNOWN, TraceBuffer, filter_records
from peaklive.analysis.trace import DECODE_CONFLICT, cell_text
from peaklive.domain import (
    TRACE_DECODE_ANY,
    TRACE_DIRECTION_ANY,
    TraceColumn,
    TraceFilterSettings,
)
from peaklive.i18n import translate
from peaklive.ui.widgets import StateNote

RECORD_INDEX_ROLE = Qt.ItemDataRole.UserRole + 3


class TraceViewPanel(QWidget):
    """A chronological, display-only trace projection over a bounded buffer.

    Filtering and column configuration change what is shown, never what was
    recorded: the ASC recorder and the retained buffer are untouched.
    """

    filters_changed = Signal()
    record_selected = Signal(int)
    columns_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = TraceFilterSettings()
        self.columns: list[TraceColumn] = []
        self._buffer: TraceBuffer | None = None
        self._updating = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        header.addWidget(QLabel(translate("trace.filters").upper()))
        self.id_filter = self._line("traceIdFilter", "trace.filter_id")
        header.addWidget(self.id_filter)
        self.message_filter = self._line("traceMessageFilter", "trace.filter_message")
        header.addWidget(self.message_filter)
        self.signal_filter = self._line("traceSignalFilter", "trace.filter_signal")
        header.addWidget(self.signal_filter)

        self.show_frames = QCheckBox(
            translate("trace.show_frames"), objectName="showFramesCheckbox"
        )
        self.show_frames.setChecked(True)
        self.show_frames.setToolTip(translate("trace.show_frames"))
        self.show_frames.toggled.connect(self._read_filters)
        header.addWidget(self.show_frames)
        self.show_events = QCheckBox(
            translate("trace.show_events"), objectName="showEventsCheckbox"
        )
        self.show_events.setChecked(True)
        self.show_events.setToolTip(translate("trace.show_events"))
        self.show_events.toggled.connect(self._read_filters)
        header.addWidget(self.show_events)

        self.more_filters_button = QPushButton(
            translate("trace.more_filters"), objectName="moreFiltersButton"
        )
        self.more_filters_button.setToolTip(translate("trace.more_filters"))
        self.more_filters_button.clicked.connect(self._toggle_secondary)
        header.addWidget(self.more_filters_button)

        self.columns_button = QPushButton(
            translate("trace.columns"), objectName="traceColumnsButton"
        )
        self.columns_button.setToolTip(translate("trace.columns_tooltip"))
        self.columns_button.clicked.connect(self.columns_requested)
        header.addWidget(self.columns_button)

        self.clear_filters_button = QPushButton(
            translate("trace.clear_filters"), objectName="clearFiltersButton"
        )
        self.clear_filters_button.setToolTip(translate("trace.clear_filters"))
        self.clear_filters_button.clicked.connect(self.clear_filters)
        header.addWidget(self.clear_filters_button)
        layout.addLayout(header)

        self.secondary = QWidget(objectName="secondaryFilters")
        secondary_layout = QGridLayout(self.secondary)
        secondary_layout.setContentsMargins(0, 0, 0, 0)
        secondary_layout.addWidget(QLabel(translate("trace.filter_direction")), 0, 0)
        self.direction_filter = QComboBox(objectName="traceDirectionFilter")
        self.direction_filter.setAccessibleName(translate("trace.filter_direction"))
        self.direction_filter.addItem(translate("trace.any"), TRACE_DIRECTION_ANY)
        self.direction_filter.addItem("RX", "RX")
        self.direction_filter.addItem("EVENT", "EVENT")
        self.direction_filter.currentIndexChanged.connect(self._read_filters)
        secondary_layout.addWidget(self.direction_filter, 0, 1)
        secondary_layout.addWidget(QLabel(translate("trace.filter_status")), 0, 2)
        self.status_filter = QComboBox(objectName="traceStatusFilter")
        self.status_filter.setAccessibleName(translate("trace.filter_status"))
        self.status_filter.addItem(translate("trace.any"), TRACE_DECODE_ANY)
        self.status_filter.addItem(DECODE_DECODED, DECODE_DECODED)
        self.status_filter.addItem(DECODE_UNKNOWN, DECODE_UNKNOWN)
        self.status_filter.addItem(DECODE_CONFLICT, DECODE_CONFLICT)
        self.status_filter.currentIndexChanged.connect(self._read_filters)
        secondary_layout.addWidget(self.status_filter, 0, 3)
        self.event_filter = self._line("traceEventFilter", "trace.filter_event")
        secondary_layout.addWidget(QLabel(translate("trace.filter_event")), 0, 4)
        secondary_layout.addWidget(self.event_filter, 0, 5)
        self.time_start_filter = self._line("traceStartFilter", "trace.filter_from")
        secondary_layout.addWidget(QLabel(translate("trace.filter_from")), 1, 0)
        secondary_layout.addWidget(self.time_start_filter, 1, 1)
        self.time_end_filter = self._line("traceEndFilter", "trace.filter_to")
        secondary_layout.addWidget(QLabel(translate("trace.filter_to")), 1, 2)
        secondary_layout.addWidget(self.time_end_filter, 1, 3)
        self.secondary.setVisible(False)
        layout.addWidget(self.secondary)

        self.chips = QWidget(objectName="filterChips")
        self.chips_layout = QHBoxLayout(self.chips)
        self.chips_layout.setContentsMargins(0, 0, 0, 0)
        self.chips.setVisible(False)
        layout.addWidget(self.chips)

        self.table = QTableWidget(0, 0, objectName="traceTable")
        self.table.setAccessibleName(translate("trace.table"))
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.currentCellChanged.connect(self._selection_changed)
        layout.addWidget(self.table, 1)

        self.note = StateNote(translate("trace.empty"))
        layout.addWidget(self.note)
        self.summary = QLabel("", objectName="traceSummary")
        layout.addWidget(self.summary)

    # ---- construction -------------------------------------------------

    def _line(self, object_name: str, key: str) -> QLineEdit:
        edit = QLineEdit(objectName=object_name)
        label = translate(key)
        edit.setAccessibleName(label)
        edit.setToolTip(label)
        edit.setPlaceholderText(label)
        edit.setClearButtonEnabled(True)
        edit.textChanged.connect(self._read_filters)
        return edit

    def _toggle_secondary(self) -> None:
        showing = not self.secondary.isVisible()
        self.secondary.setVisible(showing)
        label = translate("trace.fewer_filters" if showing else "trace.more_filters")
        self.more_filters_button.setText(label)
        self.more_filters_button.setToolTip(label)

    # ---- filters ------------------------------------------------------

    def apply_settings(self, settings: TraceFilterSettings) -> None:
        """Reflect a restored filter set without echoing change signals."""
        self.settings = settings
        self._updating = True
        try:
            self.id_filter.setText(settings.arbitration_id)
            self.message_filter.setText(settings.message)
            self.signal_filter.setText(settings.signal)
            self.event_filter.setText(settings.event_kind)
            self.time_start_filter.setText(
                "" if settings.time_start is None else f"{settings.time_start:g}"
            )
            self.time_end_filter.setText(
                "" if settings.time_end is None else f"{settings.time_end:g}"
            )
            self.show_frames.setChecked(settings.show_frames)
            self.show_events.setChecked(settings.show_events)
            self.direction_filter.setCurrentIndex(
                max(0, self.direction_filter.findData(settings.direction))
            )
            self.status_filter.setCurrentIndex(
                max(0, self.status_filter.findData(settings.decode_status))
            )
        finally:
            self._updating = False
        if settings.is_active():
            self.secondary.setVisible(True)
            self.more_filters_button.setText(translate("trace.fewer_filters"))
        self._refresh_chips()

    def _read_filters(self) -> None:
        if self._updating:
            return
        self.settings.arbitration_id = self.id_filter.text().strip()
        self.settings.message = self.message_filter.text().strip()
        self.settings.signal = self.signal_filter.text().strip()
        self.settings.event_kind = self.event_filter.text().strip()
        self.settings.time_start = _optional_float(self.time_start_filter.text())
        self.settings.time_end = _optional_float(self.time_end_filter.text())
        self.settings.show_frames = self.show_frames.isChecked()
        self.settings.show_events = self.show_events.isChecked()
        self.settings.direction = str(
            self.direction_filter.currentData() or TRACE_DIRECTION_ANY
        )
        self.settings.decode_status = str(self.status_filter.currentData() or TRACE_DECODE_ANY)
        self._refresh_chips()
        self.refresh()
        self.filters_changed.emit()

    def clear_filters(self) -> None:
        self.settings.clear()
        self.apply_settings(self.settings)
        self.refresh()
        self.filters_changed.emit()

    def remove_filter(self, field_name: str) -> None:
        self.settings.reset_field(field_name)
        self.apply_settings(self.settings)
        self.refresh()
        self.filters_changed.emit()

    def _refresh_chips(self) -> None:
        while self.chips_layout.count():
            item = self.chips_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        chips = self.settings.active_chips()
        for field_name, label in chips:
            chip = QPushButton(f"{label}  ×", objectName="chipButton")
            chip.setAccessibleName(label)
            chip.setToolTip(label)
            chip.setProperty("filterField", field_name)
            chip.clicked.connect(lambda _=False, name=field_name: self.remove_filter(name))
            self.chips_layout.addWidget(chip)
        self.chips_layout.addStretch(1)
        self.chips.setVisible(bool(chips))

    # ---- columns ------------------------------------------------------

    def apply_columns(self, columns: list[TraceColumn]) -> None:
        self.columns = columns
        visible = [column for column in columns if column.visible]
        self.table.setColumnCount(len(visible))
        self.table.setHorizontalHeaderLabels(
            [translate(f"trace.column_{column.key}") for column in visible]
        )
        for index, column in enumerate(visible):
            self.table.setColumnWidth(index, column.width)
        self.refresh()

    # ---- rendering ----------------------------------------------------

    def set_buffer(self, buffer: TraceBuffer) -> None:
        self._buffer = buffer

    def refresh(self) -> None:
        """Re-render the filtered projection of the buffer."""
        buffer = self._buffer
        if buffer is None:
            return
        selected = self.selected_index()
        filtered = filter_records(buffer, self.settings)
        visible = [column for column in self.columns if column.visible]
        self.table.blockSignals(True)
        self.table.setRowCount(len(filtered.records))
        for row, record in enumerate(filtered.records):
            for index, column in enumerate(visible):
                item = QTableWidgetItem(cell_text(record, column.key, column.value_format))
                item.setData(RECORD_INDEX_ROLE, record.index)
                self.table.setItem(row, index, item)
        self.table.blockSignals(False)
        self._restore_selection(selected)
        self._refresh_state(filtered.total, len(filtered.records), filtered.hidden, buffer.capacity)

    def _refresh_state(self, total: int, shown: int, hidden: int, capacity: int) -> None:
        if total == 0:
            self.note.show_message(translate("trace.empty"), "info")
        elif shown == 0:
            self.note.show_message(
                translate("trace.filtered_empty").format(hidden=hidden), "warning"
            )
        else:
            self.note.clear_message()
        self.summary.setText(
            translate("trace.summary").format(shown=shown, total=total, capacity=capacity)
        )

    def selected_index(self) -> int | None:
        row = self.table.currentRow()
        if row < 0 or self.table.columnCount() == 0:
            return None
        item = self.table.item(row, 0)
        if item is None:
            return None
        value = item.data(RECORD_INDEX_ROLE)
        return int(value) if value is not None else None

    def select_record(self, record_index: int) -> bool:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item is not None and item.data(RECORD_INDEX_ROLE) == record_index:
                self.table.setCurrentCell(row, 0)
                return True
        return False

    def _restore_selection(self, record_index: int | None) -> None:
        if record_index is None:
            return
        if not self.select_record(record_index):
            # The selected record aged out of the bounded buffer.
            self.table.clearSelection()
            self.record_selected.emit(-1)

    def _selection_changed(self, row: int, column: int, previous_row: int, previous: int) -> None:
        del column, previous_row, previous
        if row < 0 or self.table.columnCount() == 0:
            self.record_selected.emit(-1)
            return
        item = self.table.item(row, 0)
        if item is None:
            return
        value = item.data(RECORD_INDEX_ROLE)
        self.record_selected.emit(int(value) if value is not None else -1)


def _optional_float(text: str) -> float | None:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return float(stripped)
    except ValueError:
        return None
