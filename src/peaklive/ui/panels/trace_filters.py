"""The trace filter bar: field filters, progressive disclosure, and chips."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from peaklive.analysis import DECODE_DECODED, DECODE_UNKNOWN
from peaklive.analysis.trace import DECODE_CONFLICT
from peaklive.domain import TRACE_DECODE_ANY, TRACE_DIRECTION_ANY, TraceFilterSettings
from peaklive.i18n import translate
from peaklive.ui.flow_layout import FlowLayout


class TraceFilterBar(QWidget):
    """Reads the display-only filter set and shows it back as removable chips.

    Only the primary fields are visible by default; the rest sit behind
    "More filters" so a dense trace header stays readable.
    """

    changed = Signal()
    columns_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = TraceFilterSettings()
        self._updating = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # The filter bar has more controls than a narrow centre workspace can
        # safely keep in one row.  A wrapping layout retains every control
        # (and its normal keyboard order) instead of forcing the splitter to
        # reserve the combined width of the entire header.
        self.header = QWidget(objectName="traceFilterHeader")
        header = FlowLayout(self.header, spacing=8)
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
        self.show_frames.setAccessibleName(translate("trace.show_frames"))
        self.show_frames.toggled.connect(self._read_filters)
        header.addWidget(self.show_frames)
        self.show_events = QCheckBox(
            translate("trace.show_events"), objectName="showEventsCheckbox"
        )
        self.show_events.setChecked(True)
        self.show_events.setToolTip(translate("trace.show_events"))
        self.show_events.setAccessibleName(translate("trace.show_events"))
        self.show_events.toggled.connect(self._read_filters)
        header.addWidget(self.show_events)

        self.more_filters_button = QPushButton(
            translate("trace.more_filters"), objectName="moreFiltersButton"
        )
        self.more_filters_button.setToolTip(translate("trace.more_filters"))
        self.more_filters_button.setAccessibleName(translate("trace.more_filters"))
        self.more_filters_button.clicked.connect(self._toggle_secondary)
        header.addWidget(self.more_filters_button)

        self.columns_button = QPushButton(
            translate("trace.columns"), objectName="traceColumnsButton"
        )
        self.columns_button.setToolTip(translate("trace.columns_tooltip"))
        self.columns_button.setAccessibleName(translate("trace.columns"))
        self.columns_button.clicked.connect(self.columns_requested)
        header.addWidget(self.columns_button)

        self.follow_slot = QWidget(objectName="followSlot")
        self.follow_slot_layout = QHBoxLayout(self.follow_slot)
        self.follow_slot_layout.setContentsMargins(0, 0, 0, 0)
        header.addWidget(self.follow_slot)

        self.clear_filters_button = QPushButton(
            translate("trace.clear_filters"), objectName="clearFiltersButton"
        )
        self.clear_filters_button.setToolTip(translate("trace.clear_filters"))
        self.clear_filters_button.setAccessibleName(translate("trace.clear_filters"))
        self.clear_filters_button.clicked.connect(self.clear_filters)
        header.addWidget(self.clear_filters_button)
        layout.addWidget(self.header)

        self.secondary = QWidget(objectName="secondaryFilters")
        secondary_layout = QGridLayout(self.secondary)
        secondary_layout.setContentsMargins(0, 0, 0, 0)
        secondary_layout.addWidget(QLabel(translate("trace.filter_direction")), 0, 0)
        self.direction_filter = QComboBox(objectName="traceDirectionFilter")
        self.direction_filter.setAccessibleName(translate("trace.filter_direction"))
        self.direction_filter.setToolTip(translate("trace.filter_direction"))
        self.direction_filter.addItem(translate("trace.any"), TRACE_DIRECTION_ANY)
        self.direction_filter.addItem(translate("trace.direction_rx"), "RX")
        self.direction_filter.addItem(translate("trace.direction_event"), "EVENT")
        self.direction_filter.currentIndexChanged.connect(self._read_filters)
        secondary_layout.addWidget(self.direction_filter, 0, 1)
        secondary_layout.addWidget(QLabel(translate("trace.filter_status")), 0, 2)
        self.status_filter = QComboBox(objectName="traceStatusFilter")
        self.status_filter.setAccessibleName(translate("trace.filter_status"))
        self.status_filter.setToolTip(translate("trace.filter_status"))
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
        self.changed.emit()

    def clear_filters(self) -> None:
        self.settings.clear()
        self.apply_settings(self.settings)
        self.changed.emit()

    def remove_filter(self, field_name: str) -> None:
        self.settings.reset_field(field_name)
        self.apply_settings(self.settings)
        self.changed.emit()

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

def _optional_float(text: str) -> float | None:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return float(stripped)
    except ValueError:
        return None
