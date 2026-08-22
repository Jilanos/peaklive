"""The initial instrument-style desktop workspace."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
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

from peaklive.adapters import CanAdapter, default_adapter
from peaklive.analysis import AmbiguousMessageError, DbcCatalog
from peaklive.domain import BusEvent, CanFrame, MeasurementProfile
from peaklive.i18n import translate
from peaklive.services.profiles import ProfileState, ProfileStore
from peaklive.services.replay_worker import ReplayWorker
from peaklive.services.worker import AcquisitionWorker

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
    def __init__(
        self,
        profile_store: ProfileStore | None = None,
        adapter_factory: Callable[[], CanAdapter] = default_adapter,
    ) -> None:
        super().__init__()
        self.setWindowTitle(translate("app.title"))
        self.setMinimumSize(1024, 680)
        self._store = profile_store or ProfileStore()
        self._state: ProfileState = self._store.load()
        self._adapter_factory = adapter_factory
        self._worker: AcquisitionWorker | None = None
        self._replay_worker: ReplayWorker | None = None
        self._catalog = DbcCatalog()
        self._selected_signal_name: str | None = None
        self._plot_times: list[float] = []
        self._plot_samples: list[int] = []
        self._plot_origin: float | None = None
        self._build_ui()
        self._select_last_profile()
        self._load_profile_dbcs()

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
        self.load_dbc_button = QPushButton("Load DBC", objectName="loadDbcButton")
        self.load_dbc_button.setAccessibleName("Load DBC")
        self.load_dbc_button.clicked.connect(self._choose_dbc)
        control_layout.addWidget(self.load_dbc_button)
        self.open_trace_button = QPushButton("Open Trace", objectName="openTraceButton")
        self.open_trace_button.setAccessibleName("Open ASC or TRC trace")
        self.open_trace_button.clicked.connect(self._choose_trace)
        control_layout.addWidget(self.open_trace_button)
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
        self.signal_explorer = QListWidget(objectName="signalExplorer")
        self.signal_explorer.setAccessibleName("Signal explorer")
        self.signal_explorer.addItems(["No DBC loaded", "Favorites appear here"])
        self.signal_explorer.currentTextChanged.connect(self._signal_selected)
        layout.addWidget(self.signal_explorer)
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
        self.live_plot.setTitle("Live sample preview")
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
        self._load_profile_dbcs()

    def _show_profile(self, profile: MeasurementProfile) -> None:
        mode = profile.controller_mode.value.replace("_", " ")
        recording = "recording enabled" if profile.recording.enabled else "monitor only"
        self.mode_label.setText(f"{profile.bitrate // 1000} kbit/s · {mode} · {recording}")

    def _load_profile_dbcs(self) -> None:
        self._catalog.clear()
        for configured_path in self.selected_profile.dbc_paths:
            path = Path(configured_path)
            if path.exists():
                self._catalog.load(path)
        self._refresh_signal_explorer()

    def _choose_dbc(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(self, "Load DBC", "", "DBC files (*.dbc)")
        if selected:
            self._load_dbc_path(Path(selected))

    def _load_dbc_path(self, path: Path) -> None:
        try:
            self._catalog.load(path)
        except (OSError, UnicodeDecodeError, ValueError) as error:
            self.status.showMessage(f"Cannot load DBC: {error}")
            return
        profile = self.selected_profile
        if str(path) not in profile.dbc_paths:
            profile.dbc_paths.append(str(path))
            profile.updated_at = datetime.now().astimezone().isoformat()
            self._store.save(self._state)
        self._refresh_signal_explorer()
        self.status.showMessage(f"Loaded DBC: {path.name}")

    def _choose_trace(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self, "Open Trace", "", "CAN traces (*.asc *.trc)"
        )
        if selected:
            self._open_trace(Path(selected))

    def _open_trace(self, path: Path) -> None:
        if self._replay_worker is not None and self._replay_worker.isRunning():
            self._replay_worker.request_stop()
            self._replay_worker.wait(1_000)
        self.trace_table.setRowCount(0)
        self._plot_times.clear()
        self._plot_samples.clear()
        self._plot_origin = None
        self._replay_worker = ReplayWorker(path)
        self._replay_worker.frames_received.connect(self._render_frames)
        self._replay_worker.event_received.connect(self._render_replay_event)
        self._replay_worker.replay_failed.connect(self._acquisition_failed)
        self._replay_worker.finished.connect(self._replay_finished)
        self.status.showMessage(f"Opening trace: {path.name}")
        self._replay_worker.start()

    def _render_replay_event(self, event: object) -> None:
        if isinstance(event, BusEvent):
            self.status.showMessage(f"Replay {event.kind}: {event.message}")

    def _refresh_signal_explorer(self) -> None:
        names = self._catalog.signal_names()
        saved = next(
            (name for name in self.selected_profile.displayed_signals if name in names), None
        )
        self.signal_explorer.blockSignals(True)
        self.signal_explorer.clear()
        self.signal_explorer.addItems(names or ["No DBC loaded"])
        if saved:
            self._selected_signal_name = saved
            self.signal_explorer.setCurrentRow(names.index(saved))
        elif self._selected_signal_name in names:
            self.signal_explorer.setCurrentRow(names.index(self._selected_signal_name))
        elif names:
            self._selected_signal_name = names[0]
            self.signal_explorer.setCurrentRow(0)
        else:
            self._selected_signal_name = None
        self.signal_explorer.blockSignals(False)

    def _signal_selected(self, name: str) -> None:
        if name and name != "No DBC loaded":
            self._selected_signal_name = name
            profile = self.selected_profile
            profile.displayed_signals = [name]
            profile.updated_at = datetime.now().astimezone().isoformat()
            self._store.save(self._state)
            self._plot_times.clear()
            self._plot_samples.clear()
            self._plot_origin = None
            self.live_plot.setTitle(f"Live: {name}")

    def _start_acquisition(self) -> None:
        if self._worker and self._worker.isRunning():
            return
        self._plot_times.clear()
        self._plot_samples.clear()
        self._plot_origin = None
        self._worker = AcquisitionWorker(self._adapter_factory(), self.selected_profile)
        self._worker.frames_received.connect(self._render_frames)
        self._worker.status_changed.connect(self.status.showMessage)
        self._worker.acquisition_failed.connect(self._acquisition_failed)
        self._worker.finished.connect(self._acquisition_finished)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status.showMessage("Opening CAN channel…")
        self._worker.start()

    def _render_frames(self, frames: list[CanFrame]) -> None:
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
            value = self._decoded_plot_value(frame)
            if value is None and self._selected_signal_name is None:
                value = frame.data[0] if frame.data else 0
            if value is not None:
                self._append_plot_value(frame.timestamp, value)
        overflow = self.trace_table.rowCount() - 5_000
        if overflow > 0:
            for _ in range(overflow):
                self.trace_table.removeRow(0)
        if len(self._plot_times) > 2_500:
            self._plot_times = self._plot_times[-2_500:]
            self._plot_samples = self._plot_samples[-2_500:]
        self._plot_curve.setData(
            self._plot_times,
            self._plot_samples,
        )

    def _decoded_plot_value(self, frame: CanFrame) -> float | None:
        if self._selected_signal_name is None:
            return None
        try:
            decoded = self._catalog.decode(frame)
        except AmbiguousMessageError as error:
            self.status.showMessage(f"DBC conflict: {error}")
            return None
        for signal in decoded:
            if f"{signal.message_name}.{signal.signal_name}" != self._selected_signal_name:
                continue
            if isinstance(signal.value, int | float):
                self.inspector.setText(
                    (
                        f"{signal.message_name}.{signal.signal_name} = "
                        f"{signal.value} {signal.unit or ''}"
                    ).strip()
                )
                return float(signal.value)
        return None

    def _append_plot_value(self, timestamp: float, value: float | int) -> None:
        if self._plot_origin is None:
            self._plot_origin = timestamp
        self._plot_times.append(timestamp - self._plot_origin)
        self._plot_samples.append(value)

    def _stop_acquisition(self) -> None:
        if self._worker is not None:
            self._worker.request_stop()
            self.status.showMessage("Stopping acquisition…")

    def _acquisition_failed(self, message: str) -> None:
        self.status.showMessage(f"Acquisition error: {message}")

    def _acquisition_finished(self) -> None:
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self._worker = None

    def _replay_finished(self) -> None:
        self.status.showMessage("Trace replay complete")
        self._replay_worker = None

    def closeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if self._worker is not None and self._worker.isRunning():
            self._worker.request_stop()
            self._worker.wait(1_000)
        if self._replay_worker is not None and self._replay_worker.isRunning():
            self._replay_worker.request_stop()
            self._replay_worker.wait(1_000)
        super().closeEvent(event)
