"""The trace view: display-only filters, active chips, columns, and selection."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from peaklive.analysis import TraceBuffer, TraceRecord, filter_records, matches
from peaklive.analysis.trace import cell_text
from peaklive.domain import TraceColumn, TraceFilterSettings
from peaklive.i18n import translate
from peaklive.ui.panels.trace_filters import TraceFilterBar
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
        self.columns: list[TraceColumn] = []
        self.follow_tail = True
        self._selected_record: int | None = None
        self._buffer: TraceBuffer | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.filter_bar = TraceFilterBar()
        self.filter_bar.changed.connect(self._filters_changed)
        self.filter_bar.columns_requested.connect(self.columns_requested)
        layout.addWidget(self.filter_bar)

        self.follow_checkbox = QCheckBox(
            translate("trace.follow_tail"), objectName="followTailCheckbox"
        )
        self.follow_checkbox.setChecked(True)
        self.follow_checkbox.setToolTip(translate("trace.follow_tail"))
        self.follow_checkbox.setAccessibleName(translate("trace.follow_tail"))
        self.follow_checkbox.toggled.connect(self._follow_toggled)
        self.filter_bar.follow_slot_layout.addWidget(self.follow_checkbox)

        self.table = QTableWidget(0, 0, objectName="traceTable")
        self.table.setAccessibleName(translate("trace.table"))
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.currentCellChanged.connect(self._selection_changed)
        self.table.verticalScrollBar().valueChanged.connect(self._scrolled)
        layout.addWidget(self.table, 1)

        self.tail_note = StateNote(translate("trace.tail_paused"))
        self.tail_note.setVisible(False)
        layout.addWidget(self.tail_note)
        self.note = StateNote(translate("trace.empty"))
        layout.addWidget(self.note)
        self.summary = QLabel("", objectName="traceSummary")
        layout.addWidget(self.summary)

    # ---- filters ------------------------------------------------------

    @property
    def settings(self) -> TraceFilterSettings:
        return self.filter_bar.settings

    def apply_settings(self, settings: TraceFilterSettings) -> None:
        self.filter_bar.apply_settings(settings)
        self.refresh()

    def clear_filters(self) -> None:
        self.filter_bar.clear_filters()

    def remove_filter(self, field_name: str) -> None:
        self.filter_bar.remove_filter(field_name)

    def _filters_changed(self) -> None:
        self.refresh()
        self.filters_changed.emit()

    # ---- filter widget accessors ---------------------------------------

    @property
    def id_filter(self):
        return self.filter_bar.id_filter

    @property
    def message_filter(self):
        return self.filter_bar.message_filter

    @property
    def signal_filter(self):
        return self.filter_bar.signal_filter

    @property
    def event_filter(self):
        return self.filter_bar.event_filter

    @property
    def time_start_filter(self):
        return self.filter_bar.time_start_filter

    @property
    def time_end_filter(self):
        return self.filter_bar.time_end_filter

    @property
    def direction_filter(self):
        return self.filter_bar.direction_filter

    @property
    def status_filter(self):
        return self.filter_bar.status_filter

    @property
    def show_frames(self):
        return self.filter_bar.show_frames

    @property
    def show_events(self):
        return self.filter_bar.show_events

    @property
    def more_filters_button(self):
        return self.filter_bar.more_filters_button

    @property
    def clear_filters_button(self):
        return self.filter_bar.clear_filters_button

    @property
    def columns_button(self):
        return self.filter_bar.columns_button

    @property
    def secondary(self):
        return self.filter_bar.secondary

    @property
    def chips(self):
        return self.filter_bar.chips

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
        """Re-render the filtered projection from scratch.

        Used when the filters, the columns, or the buffer itself change. Live
        ingestion uses `append_records`, which touches only the new rows.
        """
        buffer = self._buffer
        if buffer is None:
            return
        selected = self._selected_record
        filtered = filter_records(buffer, self.settings)
        self.table.blockSignals(True)
        self.table.setRowCount(len(filtered.records))
        for row, record in enumerate(filtered.records):
            self._write_row(row, record)
        self.table.blockSignals(False)
        self._restore_selection(selected)
        self._refresh_state(filtered.total, len(filtered.records), filtered.hidden, buffer.capacity)
        self._scroll_to_tail()

    def append_records(self, records: Sequence[TraceRecord]) -> None:
        """Append the newly ingested records without re-rendering the table.

        Only rows that pass the active filters are appended, and the displayed
        window is trimmed from the front to the buffer capacity, so ingestion
        cost stays proportional to the batch rather than to the whole trace.
        """
        buffer = self._buffer
        if buffer is None:
            return
        matched = [record for record in records if matches(record, self.settings)]
        self.table.blockSignals(True)
        for record in matched:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self._write_row(row, record)
        if self._selected_record is not None and buffer.record(self._selected_record) is None:
            self._clear_selection()
        overflow = self.table.rowCount() - buffer.capacity
        if overflow > 0:
            # Trim the aged-out head in one pass instead of one removal per row.
            retained = [
                [self.table.takeItem(row, column) for column in range(self.table.columnCount())]
                for row in range(overflow, self.table.rowCount())
            ]
            self.table.setRowCount(len(retained))
            for row, cells in enumerate(retained):
                for column, item in enumerate(cells):
                    if item is not None:
                        self.table.setItem(row, column, item)
        self.table.blockSignals(False)
        filtered_total = len(buffer)
        self._refresh_state(
            filtered_total,
            self.table.rowCount(),
            max(0, filtered_total - self.table.rowCount()),
            buffer.capacity,
        )
        self._scroll_to_tail()

    def _write_row(self, row: int, record: TraceRecord) -> None:
        for index, column in enumerate(
            column for column in self.columns if column.visible
        ):
            item = QTableWidgetItem(cell_text(record, column.key, column.value_format))
            item.setData(RECORD_INDEX_ROLE, record.index)
            self.table.setItem(row, index, item)

    def set_follow_tail(self, enabled: bool) -> None:
        self.follow_tail = enabled
        self.follow_checkbox.blockSignals(True)
        self.follow_checkbox.setChecked(enabled)
        self.follow_checkbox.blockSignals(False)
        self.tail_note.setVisible(not enabled)
        if enabled:
            self._scroll_to_tail()

    def _follow_toggled(self, enabled: bool) -> None:
        self.set_follow_tail(enabled)

    def _scroll_to_tail(self) -> None:
        if self.follow_tail:
            self.table.scrollToBottom()

    def _scrolled(self, value: int) -> None:
        """Leave follow-tail as soon as the operator moves off the newest row."""
        bar = self.table.verticalScrollBar()
        if self.follow_tail and value < bar.maximum():
            self.set_follow_tail(False)

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
                self._selected_record = record_index
                return True
        return False

    def _restore_selection(self, record_index: int | None) -> None:
        if record_index is None:
            return
        if not self.select_record(record_index):
            # The selected record aged out of the buffer or the filters hid it.
            self._clear_selection()

    def _clear_selection(self) -> None:
        self._selected_record = None
        self.table.blockSignals(True)
        self.table.clearSelection()
        self.table.setCurrentCell(-1, -1)
        self.table.blockSignals(False)
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
        self._selected_record = int(value) if value is not None else None
        self.record_selected.emit(int(value) if value is not None else -1)
