"""The initial instrument-style desktop workspace."""

from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from peaklive.adapters import FakeCanAdapter
from peaklive.domain import MeasurementProfile
from peaklive.i18n import translate
from peaklive.services.profiles import ProfileState, ProfileStore

APP_STYLE = """
QMainWindow { background: #10151d; color: #e6edf7; }
QLabel { color: #cbd5e1; }
QFrame#instrument { background: #17202b; border: 1px solid #293748; border-radius: 6px; }
QPushButton { background: #1f6feb; border: none; border-radius: 5px; color: white;
              font-weight: 600; min-height: 30px; padding: 0 12px; }
QPushButton:disabled { background: #334155; color: #94a3b8; }
QComboBox, QListWidget, QTableWidget { background: #111923; border: 1px solid #293748;
                                       color: #e6edf7; selection-background-color: #1f6feb; }
QHeaderView::section { background: #17202b; color: #94a3b8; border: none; padding: 5px; }
QStatusBar { background: #0d1219; color: #94a3b8; }
"""


class MainWindow(QMainWindow):
    def __init__(self, profile_store: ProfileStore | None = None) -> None:
        super().__init__()
        self.setWindowTitle(translate("app.title"))
        self.setMinimumSize(1024, 680)
        self._store = profile_store or ProfileStore()
        self._state: ProfileState = self._store.load()
        self._adapter = FakeCanAdapter()
        self._build_ui()
        self._select_last_profile()

    @property
    def selected_profile(self) -> MeasurementProfile:
        return self._state.selected

    def _build_ui(self) -> None:
        self.setStyleSheet(APP_STYLE)
        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        controls = QFrame(objectName="instrument")
        control_layout = QHBoxLayout(controls)
        control_layout.addWidget(QLabel(translate("profile.label").upper()))
        self.profile_selector = QComboBox(objectName="profileSelector")
        self.profile_selector.setAccessibleName("Measurement profile")
        self.profile_selector.addItems([profile.name for profile in self._state.profiles])
        self.profile_selector.currentIndexChanged.connect(self._profile_changed)
        control_layout.addWidget(self.profile_selector, 1)
        self.mode_label = QLabel(objectName="modeLabel")
        control_layout.addWidget(self.mode_label)
        self.start_button = QPushButton(
            translate("acquisition.start"), objectName="startAcquisitionButton"
        )
        self.start_button.setAccessibleName(translate("acquisition.start"))
        self.start_button.clicked.connect(self._start_acquisition)
        control_layout.addWidget(self.start_button)
        self.stop_button = QPushButton(
            translate("acquisition.stop"), objectName="stopAcquisitionButton"
        )
        self.stop_button.setAccessibleName(translate("acquisition.stop"))
        self.stop_button.clicked.connect(self._stop_acquisition)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        root_layout.addWidget(controls)

        workspace = QSplitter(Qt.Orientation.Horizontal)
        workspace.addWidget(self._signal_panel())
        workspace.addWidget(self._trace_panel())
        workspace.addWidget(self._inspector_panel())
        workspace.setSizes([220, 600, 260])
        root_layout.addWidget(workspace, 1)
        self.setCentralWidget(root)
        self.status = QStatusBar(self)
        self.status.showMessage(translate("acquisition.disconnected"))
        self.setStatusBar(self.status)

    def _panel(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        panel = QFrame(objectName="instrument")
        layout = QVBoxLayout(panel)
        heading = QLabel(title.upper())
        heading.setStyleSheet("font-weight: 700; color: #7dd3fc;")
        layout.addWidget(heading)
        return panel, layout

    def _signal_panel(self) -> QFrame:
        panel, layout = self._panel(translate("workspace.signals"))
        signals = QListWidget(objectName="signalExplorer")
        signals.setAccessibleName("Signal explorer")
        signals.addItems(["No DBC loaded", "Favorites appear here"])
        layout.addWidget(signals)
        return panel

    def _trace_panel(self) -> QFrame:
        panel, layout = self._panel(translate("workspace.trace"))
        self.trace_table = QTableWidget(0, 6, objectName="traceTable")
        self.trace_table.setAccessibleName("CAN trace")
        self.trace_table.setHorizontalHeaderLabels(
            ["Time", "ID", "DLC", "Data", "Channel", "State"]
        )
        self.trace_table.setAlternatingRowColors(True)
        layout.addWidget(self.trace_table)
        self.live_plot = pg.PlotWidget(objectName="livePlot")
        self.live_plot.setAccessibleName("Live signal plot")
        self.live_plot.setBackground("#0d1219")
        self.live_plot.showGrid(x=True, y=True, alpha=0.2)
        self.live_plot.setLabel("left", "Sample")
        self.live_plot.setLabel("bottom", "Time", units="s")
        self.live_plot.setTitle("Live sample preview — select a DBC signal for engineering plots")
        self._plot_curve = self.live_plot.plot(pen=pg.mkPen("#38bdf8", width=2))
        self.live_plot.setMinimumHeight(180)
        layout.addWidget(self.live_plot)
        return panel

    def _inspector_panel(self) -> QFrame:
        panel, layout = self._panel(translate("workspace.inspector"))
        self.inspector = QLabel("Select a frame to inspect its raw payload and decoded values.")
        self.inspector.setWordWrap(True)
        layout.addWidget(self.inspector)
        layout.addStretch(1)
        return panel

    def _select_last_profile(self) -> None:
        selected_index = next(
            index
            for index, profile in enumerate(self._state.profiles)
            if profile.identifier == self._state.last_profile_id
        )
        self.profile_selector.setCurrentIndex(selected_index)
        self._show_profile(self.selected_profile)

    def _profile_changed(self, index: int) -> None:
        if index < 0:
            return
        self._state.last_profile_id = self._state.profiles[index].identifier
        self._store.save(self._state)
        self._show_profile(self.selected_profile)

    def _show_profile(self, profile: MeasurementProfile) -> None:
        mode = profile.controller_mode.value.replace("_", " ")
        recording = "recording enabled" if profile.recording.enabled else "monitor only"
        self.mode_label.setText(f"{profile.bitrate // 1000} kbit/s · {mode} · {recording}")

    def _start_acquisition(self) -> None:
        event = self._adapter.connect(self.selected_profile)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status.showMessage(event.message)
        frames = list(self._adapter.frames())
        origin = frames[0].timestamp if frames else 0.0
        for frame in frames:
            row = self.trace_table.rowCount()
            self.trace_table.insertRow(row)
            cells = [
                f"{frame.timestamp:.6f}",
                f"0x{frame.arbitration_id:03X}",
                str(frame.dlc),
                frame.data.hex(" ").upper(),
                frame.channel,
                "RX",
            ]
            for column, value in enumerate(cells):
                self.trace_table.setItem(row, column, QTableWidgetItem(value))
        self._plot_curve.setData(
            [frame.timestamp - origin for frame in frames],
            [frame.data[0] if frame.data else 0 for frame in frames],
        )

    def _stop_acquisition(self) -> None:
        event = self._adapter.disconnect()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status.showMessage(event.message)
