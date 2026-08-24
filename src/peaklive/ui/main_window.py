"""The initial instrument-style desktop workspace."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from peaklive.adapters import CanAdapter, default_adapter
from peaklive.analysis import AmbiguousMessageError, DbcCatalog, DecodedSignal
from peaklive.domain import BusEvent, CanFrame, ControllerMode, MeasurementProfile
from peaklive.i18n import translate
from peaklive.services.profiles import ProfileState, ProfileStore
from peaklive.services.replay_worker import ReplayWorker
from peaklive.services.worker import AcquisitionWorker

COMMON_BITRATES = (125_000, 250_000, 500_000, 1_000_000)

APP_STYLE = """
QMainWindow { background: #0b1018; color: #e6edf7; }
QLabel { color: #cbd5e1; }
QLabel#panelHeading { color: #f59e0b; font-weight: 800; letter-spacing: 0.08em; }
QLabel#statusPill { background: #111923; border: 1px solid #334155; border-radius: 999px;
                    color: #93c5fd; padding: 5px 10px; }
QFrame#instrument { background: #141c27; border: 1px solid #263448; border-radius: 8px; }
QPushButton, QToolButton { background: #1f6feb; border: none; border-radius: 5px; color: white;
                           font-weight: 700; min-height: 28px; padding: 0 10px; }
QToolButton#collapseButton { background: #202b3a; color: #cbd5e1; min-width: 24px; }
QPushButton:disabled { background: #334155; color: #94a3b8; }
QComboBox, QListWidget, QTableWidget, QTreeWidget, QLineEdit {
    background: #0f1722; border: 1px solid #293748; border-radius: 5px;
    color: #e6edf7; selection-background-color: #1f6feb; min-height: 26px;
}
QCheckBox { color: #cbd5e1; spacing: 8px; }
QHeaderView::section { background: #17202b; color: #94a3b8; border: none; padding: 5px; }
QStatusBar { background: #080d13; color: #94a3b8; }
"""

SIGNAL_KEY_ROLE = Qt.ItemDataRole.UserRole
DBC_HASH_ROLE = Qt.ItemDataRole.UserRole + 1


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
        self._selected_signal_names: set[str] = set(self.selected_profile.displayed_signals)
        self._favorite_signal_names: set[str] = set(self.selected_profile.favorite_signals)
        self._shown_only = False
        self._plot_series: dict[str, tuple[list[float], list[float]]] = {}
        self._plot_curves: dict[str, pg.PlotDataItem] = {}
        self._plot_widgets: dict[str, pg.PlotWidget] = {}
        self._cursor_readouts: dict[str, QLabel] = {}
        self._plot_origin: float | None = None
        self._trace_graph_mode = "combo"
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
        control_layout.addWidget(QLabel("CHANNEL"))
        self.channel_selector = QComboBox(objectName="channelSelector")
        self.channel_selector.setAccessibleName("CAN channel")
        self.channel_selector.addItems(["channel-1", "PCAN_USBBUS1", "PCAN_USBBUS2"])
        self.channel_selector.currentTextChanged.connect(self._acquisition_options_changed)
        control_layout.addWidget(self.channel_selector)
        control_layout.addWidget(QLabel("BITRATE"))
        self.bitrate_selector = QComboBox(objectName="bitrateSelector")
        self.bitrate_selector.setAccessibleName("CAN bitrate")
        for bitrate in COMMON_BITRATES:
            self.bitrate_selector.addItem(f"{bitrate // 1000} kbit/s", bitrate)
        self.bitrate_selector.currentIndexChanged.connect(self._acquisition_options_changed)
        control_layout.addWidget(self.bitrate_selector)
        self.controller_mode_selector = QComboBox(objectName="controllerModeSelector")
        self.controller_mode_selector.setAccessibleName("Controller acknowledge mode")
        self.controller_mode_selector.addItem(
            "Passive listen-only · no ACK",
            ControllerMode.PASSIVE_LISTEN_ONLY.value,
        )
        self.controller_mode_selector.addItem(
            "Normal receive · controller ACK",
            ControllerMode.NORMAL_RECEIVE.value,
        )
        self.controller_mode_selector.currentIndexChanged.connect(
            self._acquisition_options_changed
        )
        control_layout.addWidget(self.controller_mode_selector)
        self.mode_label = QLabel(objectName="statusPill")
        control_layout.addWidget(self.mode_label)
        self.load_dbc_button = QPushButton("Load DBC", objectName="loadDbcButton")
        self.load_dbc_button.setAccessibleName("Load one or more DBC files")
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
        self.signals_panel, self.signals_body = self._collapsible_panel(
            translate("workspace.signals")
        )
        self._populate_signal_panel(self.signals_body)
        self.trace_graph_panel, self.trace_graph_body = self._collapsible_panel(
            "Graphs · Trace"
        )
        self._populate_trace_graph_panel(self.trace_graph_body)
        self.inspector_panel, self.inspector_body = self._collapsible_panel(
            translate("workspace.inspector")
        )
        self._populate_inspector_panel(self.inspector_body)
        workspace.addWidget(self.signals_panel)
        workspace.addWidget(self.trace_graph_panel)
        workspace.addWidget(self.inspector_panel)
        workspace.setSizes([320, 720, 280])
        root_layout.addWidget(workspace, 1)
        self.setCentralWidget(root)
        self.status = QStatusBar(self)
        self.status.showMessage(translate("acquisition.disconnected"))
        self.setStatusBar(self.status)

    def _panel(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        panel = QFrame(objectName="instrument")
        layout = QVBoxLayout(panel)
        heading = QLabel(title.upper(), objectName="panelHeading")
        layout.addWidget(heading)
        return panel, layout

    def _collapsible_panel(self, title: str) -> tuple[QFrame, QWidget]:
        panel = QFrame(objectName="instrument")
        layout = QVBoxLayout(panel)
        header = QHBoxLayout()
        heading = QLabel(title.upper(), objectName="panelHeading")
        header.addWidget(heading, 1)
        toggle = QToolButton(objectName="collapseButton")
        toggle.setAccessibleName(f"Collapse {title}")
        toggle.setText("−")
        header.addWidget(toggle)
        layout.addLayout(header)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(body, 1)
        toggle.clicked.connect(lambda: self._toggle_panel(body, toggle))
        return panel, body

    @staticmethod
    def _toggle_panel(body: QWidget, button: QToolButton) -> None:
        body.setVisible(not body.isVisible())
        button.setText("+" if not body.isVisible() else "−")

    def _populate_signal_panel(self, body: QWidget) -> None:
        layout = body.layout()
        assert isinstance(layout, QVBoxLayout)
        self.dbc_library = QTreeWidget(objectName="dbcLibrary")
        self.dbc_library.setAccessibleName("DBC library")
        self.dbc_library.setHeaderLabels(["DBC", "State"])
        self.dbc_library.itemChanged.connect(self._dbc_item_changed)
        layout.addWidget(self.dbc_library)
        library_actions = QHBoxLayout()
        self.remove_dbc_button = QPushButton("Remove selected", objectName="removeDbcButton")
        self.remove_dbc_button.clicked.connect(self._remove_selected_dbc)
        library_actions.addWidget(self.remove_dbc_button)
        self.conflict_selector = QComboBox(objectName="dbcConflictSelector")
        self.conflict_selector.setAccessibleName("DBC conflict resolver")
        self.conflict_selector.currentIndexChanged.connect(self._conflict_resolution_changed)
        library_actions.addWidget(self.conflict_selector, 1)
        layout.addLayout(library_actions)
        self.signal_filter = QLineEdit(objectName="signalFilter")
        self.signal_filter.setAccessibleName("Search signals")
        self.signal_filter.setPlaceholderText("Search DBC, message, signal…")
        self.signal_filter.textChanged.connect(self._refresh_signal_explorer)
        layout.addWidget(self.signal_filter)
        filter_actions = QHBoxLayout()
        self.shown_only_checkbox = QCheckBox("Shown only", objectName="shownOnlyCheckbox")
        self.shown_only_checkbox.toggled.connect(self._shown_only_changed)
        filter_actions.addWidget(self.shown_only_checkbox)
        self.favorites_only_checkbox = QCheckBox(
            "Favorites only",
            objectName="favoritesOnlyCheckbox",
        )
        self.favorites_only_checkbox.toggled.connect(self._refresh_signal_explorer)
        filter_actions.addWidget(self.favorites_only_checkbox)
        layout.addLayout(filter_actions)
        self.signal_explorer = QTreeWidget(objectName="signalExplorer")
        self.signal_explorer.setAccessibleName("Signal explorer")
        self.signal_explorer.setHeaderLabels(["Signal", "Shown", "Fav"])
        self.signal_explorer.itemChanged.connect(self._signal_item_changed)
        self.signal_explorer.itemActivated.connect(self._signal_item_activated)
        layout.addWidget(self.signal_explorer, 1)

    def _populate_trace_graph_panel(self, body: QWidget) -> None:
        layout = body.layout()
        assert isinstance(layout, QVBoxLayout)
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("VIEW"))
        self.workspace_mode_selector = QComboBox(objectName="workspaceModeSelector")
        self.workspace_mode_selector.setAccessibleName("Workspace visible configuration")
        self.workspace_mode_selector.addItem("Graph + trace combo", "combo")
        self.workspace_mode_selector.addItem("Graphs only", "graphs")
        self.workspace_mode_selector.addItem("Trace only", "trace")
        self.workspace_mode_selector.currentIndexChanged.connect(self._workspace_mode_changed)
        mode_row.addWidget(self.workspace_mode_selector)
        self.cursor_summary = QLabel("Cursors: A/B disabled until a graph has data.")
        mode_row.addWidget(self.cursor_summary, 1)
        layout.addLayout(mode_row)
        self.graph_scroll = QScrollArea(objectName="graphScroll")
        self.graph_scroll.setWidgetResizable(True)
        self.graph_container = QWidget()
        self.graph_layout = QVBoxLayout(self.graph_container)
        self.graph_layout.setContentsMargins(0, 0, 0, 0)
        self.graph_scroll.setWidget(self.graph_container)
        layout.addWidget(self.graph_scroll, 1)
        self.trace_table = QTableWidget(0, 6, objectName="traceTable")
        self.trace_table.setAccessibleName("CAN trace")
        self.trace_table.setHorizontalHeaderLabels(
            ["Time", "ID", "DLC", "Data", "Channel", "State"]
        )
        self.trace_table.setAlternatingRowColors(True)
        layout.addWidget(self.trace_table)

    def _populate_inspector_panel(self, body: QWidget) -> None:
        layout = body.layout()
        assert isinstance(layout, QVBoxLayout)
        self.inspector = QLabel("Select a frame to inspect its raw payload and decoded values.")
        self.inspector.setWordWrap(True)
        layout.addWidget(self.inspector)
        layout.addStretch(1)

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
        self._selected_signal_names = set(self.selected_profile.displayed_signals)
        self._favorite_signal_names = set(self.selected_profile.favorite_signals)
        self._store.save(self._state)
        self._show_profile(self.selected_profile)
        self._load_profile_dbcs()

    def _show_profile(self, profile: MeasurementProfile) -> None:
        self.channel_selector.blockSignals(True)
        channel_index = self.channel_selector.findText(profile.channel)
        if channel_index < 0:
            self.channel_selector.addItem(profile.channel)
            channel_index = self.channel_selector.findText(profile.channel)
        self.channel_selector.setCurrentIndex(channel_index)
        self.channel_selector.blockSignals(False)
        self.bitrate_selector.blockSignals(True)
        bitrate_index = self.bitrate_selector.findData(profile.bitrate)
        self.bitrate_selector.setCurrentIndex(max(0, bitrate_index))
        self.bitrate_selector.blockSignals(False)
        self.controller_mode_selector.blockSignals(True)
        mode_index = self.controller_mode_selector.findData(profile.controller_mode.value)
        self.controller_mode_selector.setCurrentIndex(max(0, mode_index))
        self.controller_mode_selector.blockSignals(False)
        self._trace_graph_mode = str(profile.trace_filters.get("workspace_mode", "combo"))
        workspace_index = self.workspace_mode_selector.findData(self._trace_graph_mode)
        self.workspace_mode_selector.setCurrentIndex(max(0, workspace_index))
        self._workspace_mode_changed()
        mode = profile.controller_mode.value.replace("_", " ")
        recording = "recording enabled" if profile.recording.enabled else "monitor only"
        ack = (
            "controller ACK"
            if profile.controller_mode is ControllerMode.NORMAL_RECEIVE
            else "no ACK"
        )
        self.mode_label.setText(
            f"APP READ-ONLY · {profile.bitrate // 1000} kbit/s · {mode} · {ack} · {recording}"
        )

    def _acquisition_options_changed(self) -> None:
        profile = self.selected_profile
        profile.channel = self.channel_selector.currentText() or "channel-1"
        bitrate = self.bitrate_selector.currentData()
        if bitrate is not None:
            profile.bitrate = int(bitrate)
        mode = self.controller_mode_selector.currentData()
        if mode is not None:
            profile.controller_mode = ControllerMode(str(mode))
        profile.updated_at = datetime.now().astimezone().isoformat()
        self._store.save(self._state)
        self._show_profile(profile)

    def _load_profile_dbcs(self) -> None:
        self._catalog.clear()
        for configured_path in self.selected_profile.dbc_paths:
            path = Path(configured_path)
            if path.exists():
                try:
                    self._catalog.load(path)
                except (OSError, ValueError) as error:
                    self.status.showMessage(f"Cannot load DBC: {error}")
        disabled = set(self.selected_profile.trace_filters.get("disabled_dbc_hashes", []))
        for definition in self._catalog.definitions:
            self._catalog.set_enabled(
                definition.content_hash,
                definition.content_hash not in disabled,
            )
        for raw_id, content_hash in dict(
            self.selected_profile.trace_filters.get("dbc_conflict_resolutions", {})
        ).items():
            try:
                self._catalog.resolve(int(raw_id), str(content_hash))
            except (KeyError, ValueError):
                continue
        self._refresh_dbc_library()
        self._refresh_signal_explorer()
        self._sync_graph_widgets()

    def _choose_dbc(self) -> None:
        selected, _ = QFileDialog.getOpenFileNames(self, "Load DBC", "", "DBC files (*.dbc)")
        for item in selected:
            self._load_dbc_path(Path(item))

    def _load_dbc_path(self, path: Path) -> None:
        try:
            definition = self._catalog.load(path)
        except (OSError, ValueError) as error:
            self.status.showMessage(f"Cannot load DBC: {error}")
            return
        profile = self.selected_profile
        if str(path) not in profile.dbc_paths:
            profile.dbc_paths.append(str(path))
            profile.updated_at = datetime.now().astimezone().isoformat()
            self._store.save(self._state)
        self._catalog.set_enabled(definition.content_hash, True)
        if not self._selected_signal_names:
            first_signal = next(iter(self._catalog.signal_names()), None)
            if first_signal is not None:
                self._selected_signal_names.add(first_signal)
                self._persist_signal_state()
        self._persist_dbc_state()
        self._refresh_dbc_library()
        self._refresh_signal_explorer()
        self._sync_graph_widgets()
        self.status.showMessage(f"Loaded DBC: {path.name}")

    def _refresh_dbc_library(self) -> None:
        self.dbc_library.blockSignals(True)
        self.dbc_library.clear()
        for definition in self._catalog.definitions:
            item = QTreeWidgetItem(
                [
                    f"{definition.path.name} · {definition.short_hash}",
                    "enabled" if self._catalog.is_enabled(definition.content_hash) else "disabled",
                ]
            )
            item.setData(0, DBC_HASH_ROLE, definition.content_hash)
            item.setCheckState(
                0,
                Qt.CheckState.Checked
                if self._catalog.is_enabled(definition.content_hash)
                else Qt.CheckState.Unchecked,
            )
            self.dbc_library.addTopLevelItem(item)
        self.dbc_library.blockSignals(False)
        self._refresh_conflict_selector()

    def _dbc_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        if column != 0:
            return
        content_hash = item.data(0, DBC_HASH_ROLE)
        if not content_hash:
            return
        self._catalog.set_enabled(str(content_hash), item.checkState(0) == Qt.CheckState.Checked)
        self._persist_dbc_state()
        self._refresh_dbc_library()
        self._refresh_signal_explorer()
        self._sync_graph_widgets()

    def _remove_selected_dbc(self) -> None:
        item = self.dbc_library.currentItem()
        if item is None:
            return
        content_hash = item.data(0, DBC_HASH_ROLE)
        if not content_hash:
            return
        removed = next(
            (
                definition
                for definition in self._catalog.definitions
                if definition.content_hash == content_hash
            ),
            None,
        )
        self._catalog.remove(str(content_hash))
        if removed is not None:
            profile = self.selected_profile
            profile.dbc_paths = [
                configured
                for configured in profile.dbc_paths
                if configured != str(removed.path)
            ]
        self._selected_signal_names = {
            name for name in self._selected_signal_names if name in self._catalog.signal_names()
        }
        self._persist_signal_state()
        self._persist_dbc_state()
        self._refresh_dbc_library()
        self._refresh_signal_explorer()
        self._sync_graph_widgets()

    def _refresh_conflict_selector(self) -> None:
        self.conflict_selector.blockSignals(True)
        self.conflict_selector.clear()
        self.conflict_selector.addItem("No DBC conflicts", None)
        for conflict in self._catalog.conflicts():
            for definition in conflict.candidates:
                self.conflict_selector.addItem(
                    f"0x{conflict.arbitration_id:03X} → {definition.path.name}",
                    (conflict.arbitration_id, definition.content_hash),
                )
        self.conflict_selector.blockSignals(False)

    def _conflict_resolution_changed(self) -> None:
        data = self.conflict_selector.currentData()
        if data is None:
            return
        arbitration_id, content_hash = data
        self._catalog.resolve(int(arbitration_id), str(content_hash))
        self._persist_dbc_state()
        self.status.showMessage(
            f"DBC conflict 0x{int(arbitration_id):03X} resolved by selected DBC"
        )

    def _persist_dbc_state(self) -> None:
        profile = self.selected_profile
        profile.trace_filters["disabled_dbc_hashes"] = [
            definition.content_hash
            for definition in self._catalog.definitions
            if not self._catalog.is_enabled(definition.content_hash)
        ]
        profile.trace_filters["dbc_conflict_resolutions"] = {
            str(arbitration_id): content_hash
            for arbitration_id, content_hash in self._catalog.resolutions.items()
        }
        profile.updated_at = datetime.now().astimezone().isoformat()
        self._store.save(self._state)

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
        self._plot_series.clear()
        self._plot_origin = None
        self._sync_graph_widgets()
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
        self.signal_explorer.blockSignals(True)
        self.signal_explorer.clear()
        references = self._filtered_signal_references()
        if not references:
            empty = QTreeWidgetItem(["No matching DBC signal", "", ""])
            empty.setDisabled(True)
            self.signal_explorer.addTopLevelItem(empty)
            self.signal_explorer.blockSignals(False)
            return
        dbc_items: dict[str, QTreeWidgetItem] = {}
        message_items: dict[tuple[str, str], QTreeWidgetItem] = {}
        first_signal: QTreeWidgetItem | None = None
        for reference in references:
            dbc_item = dbc_items.get(reference.database_hash)
            if dbc_item is None:
                dbc_item = QTreeWidgetItem(
                    [f"{reference.database_name} · {reference.database_hash[:8]}", "", ""]
                )
                dbc_item.setExpanded(True)
                dbc_items[reference.database_hash] = dbc_item
                self.signal_explorer.addTopLevelItem(dbc_item)
            message_key = (reference.database_hash, reference.message_name)
            message_item = message_items.get(message_key)
            if message_item is None:
                message_item = QTreeWidgetItem(
                    dbc_item,
                    [f"{reference.message_name} · 0x{reference.frame_id:03X}", "", ""],
                )
                message_item.setExpanded(True)
                message_items[message_key] = message_item
            display_name = reference.display_name
            signal_item = QTreeWidgetItem(
                message_item,
                [
                    f"{reference.signal_name}"
                    + (f" [{reference.unit}]" if reference.unit else ""),
                    "shown",
                    "fav",
                ],
            )
            signal_item.setData(0, SIGNAL_KEY_ROLE, display_name)
            signal_item.setCheckState(
                1,
                Qt.CheckState.Checked
                if display_name in self._selected_signal_names
                else Qt.CheckState.Unchecked,
            )
            signal_item.setCheckState(
                2,
                Qt.CheckState.Checked
                if display_name in self._favorite_signal_names
                else Qt.CheckState.Unchecked,
            )
            if first_signal is None:
                first_signal = signal_item
        if first_signal is not None:
            self.signal_explorer.setCurrentItem(first_signal)
        self.signal_explorer.blockSignals(False)

    def _filtered_signal_references(self):
        query = self.signal_filter.text().strip().casefold()
        shown_only = self.shown_only_checkbox.isChecked()
        favorites_only = self.favorites_only_checkbox.isChecked()
        references = []
        for reference in self._catalog.signal_references():
            display_name = reference.display_name
            haystack = " ".join(
                [
                    reference.database_name,
                    reference.message_name,
                    reference.signal_name,
                    display_name,
                ]
            ).casefold()
            if query and query not in haystack:
                continue
            if shown_only and display_name not in self._selected_signal_names:
                continue
            if favorites_only and display_name not in self._favorite_signal_names:
                continue
            references.append(reference)
        return references

    def _shown_only_changed(self, checked: bool) -> None:
        self._shown_only = checked
        self._refresh_signal_explorer()

    def _signal_item_activated(self, item: QTreeWidgetItem) -> None:
        key = item.data(0, SIGNAL_KEY_ROLE)
        if key:
            next_state = (
                Qt.CheckState.Unchecked
                if item.checkState(1) == Qt.CheckState.Checked
                else Qt.CheckState.Checked
            )
            item.setCheckState(1, next_state)

    def _signal_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        key = item.data(0, SIGNAL_KEY_ROLE)
        if not key:
            return
        signal_name = str(key)
        if column == 1:
            if item.checkState(1) == Qt.CheckState.Checked:
                self._selected_signal_names.add(signal_name)
            else:
                self._selected_signal_names.discard(signal_name)
            self._reset_plot_buffers(signal_name)
            self._persist_signal_state()
            self._sync_graph_widgets()
        elif column == 2:
            if item.checkState(2) == Qt.CheckState.Checked:
                self._favorite_signal_names.add(signal_name)
            else:
                self._favorite_signal_names.discard(signal_name)
            self._persist_signal_state()

    def _persist_signal_state(self) -> None:
        profile = self.selected_profile
        available = set(self._catalog.signal_names())
        profile.displayed_signals = sorted(
            name for name in self._selected_signal_names if not available or name in available
        )
        profile.favorite_signals = sorted(self._favorite_signal_names)
        profile.updated_at = datetime.now().astimezone().isoformat()
        self._store.save(self._state)

    def _start_acquisition(self) -> None:
        if self._worker and self._worker.isRunning():
            return
        self._plot_series.clear()
        self._plot_origin = None
        self._sync_graph_widgets()
        self._worker = AcquisitionWorker(self._adapter_factory(), self.selected_profile)
        self._worker.frames_received.connect(self._render_frames)
        self._worker.status_changed.connect(self.status.showMessage)
        self._worker.event_received.connect(self._render_acquisition_event)
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
            decoded = self._decoded_signals(frame)
            plotted = False
            for signal in decoded:
                key = f"{signal.message_name}.{signal.signal_name}"
                if key not in self._selected_signal_names:
                    continue
                if isinstance(signal.value, int | float):
                    self._append_plot_value(key, frame.timestamp, float(signal.value))
                    self.inspector.setText(
                        (
                            f"{signal.message_name}.{signal.signal_name} = "
                            f"{signal.value} {signal.unit or ''}"
                        ).strip()
                    )
                    plotted = True
            if not self._selected_signal_names and frame.data:
                self._append_plot_value("Raw byte 0", frame.timestamp, float(frame.data[0]))
                plotted = True
            if plotted:
                self._refresh_graph_data()
        overflow = self.trace_table.rowCount() - 5_000
        if overflow > 0:
            for _ in range(overflow):
                self.trace_table.removeRow(0)

    def _render_acquisition_event(self, event: object) -> None:
        if isinstance(event, BusEvent):
            row = self.trace_table.rowCount()
            self.trace_table.insertRow(row)
            cells = [
                f"{event.timestamp:.6f}",
                event.kind,
                "",
                event.message,
                event.channel,
                "EVENT",
            ]
            for column, value in enumerate(cells):
                self.trace_table.setItem(row, column, QTableWidgetItem(value))

    def _decoded_signals(self, frame: CanFrame) -> list[DecodedSignal]:
        try:
            return self._catalog.decode(frame)
        except AmbiguousMessageError as error:
            self.status.showMessage(f"DBC conflict: {error}")
            return []

    def _append_plot_value(self, signal_name: str, timestamp: float, value: float) -> None:
        if self._plot_origin is None:
            self._plot_origin = timestamp
        times, values = self._plot_series.setdefault(signal_name, ([], []))
        times.append(timestamp - self._plot_origin)
        values.append(value)
        if len(times) > 2_500:
            del times[:-2_500]
            del values[:-2_500]

    def _reset_plot_buffers(self, signal_name: str) -> None:
        self._plot_series.pop(signal_name, None)
        if not self._plot_series:
            self._plot_origin = None

    def _sync_graph_widgets(self) -> None:
        wanted = sorted(self._selected_signal_names) or ["Raw byte 0"]
        while self.graph_layout.count():
            item = self.graph_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        self._plot_widgets.clear()
        self._plot_curves.clear()
        self._cursor_readouts.clear()
        for signal_name in wanted:
            plot = pg.PlotWidget(objectName=f"livePlot_{signal_name.replace('.', '_')}")
            plot.setAccessibleName("Live signal plot")
            plot.setBackground("#080d13")
            plot.showGrid(x=True, y=True, alpha=0.25)
            plot.setLabel("left", signal_name)
            plot.setLabel("bottom", "Time", units="s")
            plot.setTitle(signal_name)
            plot.setMinimumHeight(170)
            curve = plot.plot(pen=pg.mkPen("#38bdf8", width=2))
            cursor_a = pg.InfiniteLine(pos=0.0, angle=90, movable=True, pen=pg.mkPen("#f59e0b"))
            cursor_b = pg.InfiniteLine(pos=0.0, angle=90, movable=True, pen=pg.mkPen("#a78bfa"))
            plot.addItem(cursor_a)
            plot.addItem(cursor_b)
            readout = QLabel("A: 0.000s · B: 0.000s · Δ 0.000s")
            cursor_a.sigPositionChanged.connect(
                lambda _line, name=signal_name: self._update_cursor_readout(name)
            )
            cursor_b.sigPositionChanged.connect(
                lambda _line, name=signal_name: self._update_cursor_readout(name)
            )
            plot._peaklive_cursor_a = cursor_a  # type: ignore[attr-defined]
            plot._peaklive_cursor_b = cursor_b  # type: ignore[attr-defined]
            self.graph_layout.addWidget(plot)
            self.graph_layout.addWidget(readout)
            self._plot_widgets[signal_name] = plot
            self._plot_curves[signal_name] = curve
            self._cursor_readouts[signal_name] = readout
        self.graph_layout.addStretch(1)
        self._plot_curve = self._plot_curves[wanted[0]]
        self.live_plot = self._plot_widgets[wanted[0]]
        self._refresh_graph_data()

    def _refresh_graph_data(self) -> None:
        for signal_name, curve in self._plot_curves.items():
            times, values = self._plot_series.get(signal_name, ([], []))
            curve.setData(times, values)
            if times:
                plot = self._plot_widgets[signal_name]
                plot._peaklive_cursor_a.setValue(times[0])  # type: ignore[attr-defined]
                plot._peaklive_cursor_b.setValue(times[-1])  # type: ignore[attr-defined]
                self._update_cursor_readout(signal_name)

    def _update_cursor_readout(self, signal_name: str) -> None:
        plot = self._plot_widgets.get(signal_name)
        readout = self._cursor_readouts.get(signal_name)
        if plot is None or readout is None:
            return
        cursor_a = float(plot._peaklive_cursor_a.value())  # type: ignore[attr-defined]
        cursor_b = float(plot._peaklive_cursor_b.value())  # type: ignore[attr-defined]
        delta = abs(cursor_b - cursor_a)
        readout.setText(f"A: {cursor_a:.3f}s · B: {cursor_b:.3f}s · Δ {delta:.3f}s")

    def _workspace_mode_changed(self) -> None:
        mode = self.workspace_mode_selector.currentData() or self._trace_graph_mode
        self._trace_graph_mode = str(mode)
        if hasattr(self, "graph_scroll"):
            self.graph_scroll.setVisible(self._trace_graph_mode in {"combo", "graphs"})
        if hasattr(self, "trace_table"):
            self.trace_table.setVisible(self._trace_graph_mode in {"combo", "trace"})
        profile = self.selected_profile
        profile.trace_filters["workspace_mode"] = self._trace_graph_mode
        profile.updated_at = datetime.now().astimezone().isoformat()
        self._store.save(self._state)

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
