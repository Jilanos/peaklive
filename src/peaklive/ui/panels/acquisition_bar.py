"""The top acquisition bar: profile, bus setup, bus state, and lifecycle."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPaintEvent
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from peaklive.domain import ControllerMode, MeasurementProfile
from peaklive.i18n import translate
from peaklive.ui.theme import BUS_STATE_COLORS, STATE_IDLE

COMMON_BITRATES = (125_000, 250_000, 500_000, 1_000_000)
CHANNELS = ("channel-1", "PCAN_USBBUS1", "PCAN_USBBUS2")

BUS_STATES = (
    "idle",
    "connecting",
    "running",
    "reconnecting",
    "bus_error",
    "bus_off",
    "stopped",
)


class BusStateLed(QWidget):
    """A colored marker for the current bus condition."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, objectName="busStateLed")
        self.setFixedSize(12, 12)
        self._color = STATE_IDLE

    def set_state(self, state: str) -> None:
        self._color = BUS_STATE_COLORS.get(state, STATE_IDLE)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802 - Qt override
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(self._color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect().adjusted(1, 1, -1, -1))


class AcquisitionBar(QFrame):
    """Bus setup and lifecycle controls, with no transmit affordance at all."""

    profile_changed = Signal(int)
    options_changed = Signal()
    load_dbc_requested = Signal()
    open_trace_requested = Signal()
    export_requested = Signal()
    start_requested = Signal()
    stop_requested = Signal()

    def __init__(self, profile_names: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent, objectName="instrument")
        layout = QHBoxLayout(self)
        layout.addWidget(QLabel(translate("profile.label").upper()))

        self.profile_selector = QComboBox(objectName="profileSelector")
        self.profile_selector.setAccessibleName(translate("profile.label"))
        self.profile_selector.setToolTip(translate("profile.label"))
        self.profile_selector.addItems(profile_names)
        self.profile_selector.currentIndexChanged.connect(self.profile_changed)
        layout.addWidget(self.profile_selector, 1)

        layout.addWidget(QLabel(translate("acquisition.channel").upper()))
        self.channel_selector = QComboBox(objectName="channelSelector")
        self.channel_selector.setAccessibleName("CAN channel")
        self.channel_selector.setToolTip("CAN channel")
        self.channel_selector.addItems(list(CHANNELS))
        self.channel_selector.currentTextChanged.connect(self.options_changed)
        layout.addWidget(self.channel_selector)

        layout.addWidget(QLabel(translate("acquisition.bitrate").upper()))
        self.bitrate_selector = QComboBox(objectName="bitrateSelector")
        self.bitrate_selector.setAccessibleName("CAN bitrate")
        self.bitrate_selector.setToolTip("CAN bitrate")
        for bitrate in COMMON_BITRATES:
            self.bitrate_selector.addItem(
                translate("acquisition.bitrate_value").format(kbit=bitrate // 1000), bitrate
            )
        self.bitrate_selector.currentIndexChanged.connect(self.options_changed)
        layout.addWidget(self.bitrate_selector)

        self.controller_mode_selector = QComboBox(objectName="controllerModeSelector")
        self.controller_mode_selector.setAccessibleName("Controller acknowledge mode")
        self.controller_mode_selector.setToolTip("Controller acknowledge mode")
        self.controller_mode_selector.addItem(
            translate("acquisition.mode_passive"), ControllerMode.PASSIVE_LISTEN_ONLY.value
        )
        self.controller_mode_selector.addItem(
            translate("acquisition.mode_normal"), ControllerMode.NORMAL_RECEIVE.value
        )
        self.controller_mode_selector.currentIndexChanged.connect(self.options_changed)
        layout.addWidget(self.controller_mode_selector)

        self.mode_label = QLabel(objectName="statusPill")
        layout.addWidget(self.mode_label)

        bus_state = QFrame(objectName="busState")
        bus_layout = QHBoxLayout(bus_state)
        bus_layout.setContentsMargins(8, 2, 10, 2)
        self.bus_led = BusStateLed()
        bus_layout.addWidget(self.bus_led)
        self.bus_state_label = QLabel(objectName="busStateLabel")
        self.bus_state_label.setAccessibleName(translate("bus.accessible"))
        bus_layout.addWidget(self.bus_state_label)
        layout.addWidget(bus_state)
        self.set_bus_state("idle")

        self.load_dbc_button = self._action(
            translate("dbc.load"), "loadDbcButton", translate("dbc.load_tooltip")
        )
        self.load_dbc_button.clicked.connect(self.load_dbc_requested)
        layout.addWidget(self.load_dbc_button)

        self.open_trace_button = self._action(
            translate("trace.open"), "openTraceButton", translate("trace.open_tooltip")
        )
        self.open_trace_button.clicked.connect(self.open_trace_requested)
        layout.addWidget(self.open_trace_button)

        self.export_button = self._action(
            translate("export.open"), "exportButton", translate("export.tooltip")
        )
        self.export_button.clicked.connect(self.export_requested)
        layout.addWidget(self.export_button)

        self.start_button = self._action(
            translate("acquisition.start"),
            "startAcquisitionButton",
            translate("acquisition.start_tooltip"),
        )
        self.start_button.clicked.connect(self.start_requested)
        layout.addWidget(self.start_button)

        self.stop_button = self._action(
            translate("acquisition.stop"),
            "stopAcquisitionButton",
            translate("acquisition.stop_tooltip"),
        )
        self.stop_button.clicked.connect(self.stop_requested)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

    @staticmethod
    def _action(label: str, object_name: str, tooltip: str) -> QPushButton:
        button = QPushButton(label, objectName=object_name)
        button.setAccessibleName(label)
        button.setToolTip(tooltip)
        return button

    def set_bus_state(self, state: str) -> None:
        """Show the bus condition as both a colored marker and a text label."""
        if state not in BUS_STATE_COLORS:
            state = "idle"
        self.bus_state = state
        self.bus_led.set_state(state)
        label = translate(f"bus.{state}")
        self.bus_state_label.setText(f"{translate('bus.label').upper()} {label}")
        self.bus_state_label.setToolTip(label)

    def set_running(self, running: bool) -> None:
        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(running)

    def show_profile(self, profile: MeasurementProfile) -> None:
        """Reflect the profile without echoing option-changed signals back out."""
        self.channel_selector.blockSignals(True)
        channel_index = self.channel_selector.findText(profile.channel)
        if channel_index < 0:
            self.channel_selector.addItem(profile.channel)
            channel_index = self.channel_selector.findText(profile.channel)
        self.channel_selector.setCurrentIndex(channel_index)
        self.channel_selector.blockSignals(False)

        self.bitrate_selector.blockSignals(True)
        self.bitrate_selector.setCurrentIndex(
            max(0, self.bitrate_selector.findData(profile.bitrate))
        )
        self.bitrate_selector.blockSignals(False)

        self.controller_mode_selector.blockSignals(True)
        self.controller_mode_selector.setCurrentIndex(
            max(0, self.controller_mode_selector.findData(profile.controller_mode.value))
        )
        self.controller_mode_selector.blockSignals(False)

        recording = (
            translate("acquisition.recording_on")
            if profile.recording.enabled
            else translate("acquisition.recording_off")
        )
        ack = (
            translate("acquisition.ack_on")
            if profile.controller_mode is ControllerMode.NORMAL_RECEIVE
            else translate("acquisition.ack_off")
        )
        self.mode_label.setText(
            translate("acquisition.read_only").format(
                kbit=profile.bitrate // 1000,
                mode=profile.controller_mode.value.replace("_", " "),
                ack=ack,
                recording=recording,
            )
        )

    def apply_to_profile(self, profile: MeasurementProfile) -> None:
        profile.channel = self.channel_selector.currentText() or "channel-1"
        bitrate = self.bitrate_selector.currentData()
        if bitrate is not None:
            profile.bitrate = int(bitrate)
        mode = self.controller_mode_selector.currentData()
        if mode is not None:
            profile.controller_mode = ControllerMode(str(mode))
