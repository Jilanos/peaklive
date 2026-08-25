"""The workspace shell: composition, wiring, and profile persistence.

Every panel lives in `peaklive.ui.panels`. This module owns the session state
the panels share — the DBC catalog, the bounded series store, the trace buffer,
the session facts, and the workers — and keeps the measurement profile in sync.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from peaklive.adapters import CanAdapter, default_adapter
from peaklive.analysis import (
    DbcCatalog,
    SeriesStore,
    SessionFacts,
    TraceBuffer,
    TraceRecord,
)
from peaklive.domain import MeasurementProfile
from peaklive.i18n import translate
from peaklive.services.profiles import ProfileState, ProfileStore
from peaklive.services.replay_worker import ReplayWorker
from peaklive.services.worker import AcquisitionWorker
from peaklive.ui.actions import WorkspaceActions
from peaklive.ui.addressing import WorkspaceAddressing
from peaklive.ui.catalog_controller import WorkspaceCatalog
from peaklive.ui.dialogs import ColumnsDialog, ExportDialog
from peaklive.ui.panels import (
    AcquisitionBar,
    DbcLibraryPanel,
    GraphStackPanel,
    InspectorPanel,
    ReportPanel,
    SignalExplorerPanel,
    TraceViewPanel,
)
from peaklive.ui.panels.signal_explorer import SIGNAL_KEY_ROLE
from peaklive.ui.session_controller import WorkspaceSession
from peaklive.ui.theme import APP_STYLE
from peaklive.ui.widgets import CollapsiblePanel, StateNote

__all__ = ["SIGNAL_KEY_ROLE", "MainWindow"]

WORKSPACE_MODES = (
    ("combo", "workspace.mode_combo"),
    ("graphs", "workspace.mode_graphs"),
    ("trace", "workspace.mode_trace"),
    ("report", "workspace.mode_report"),
)
PANEL_SIGNALS = "signals"
PANEL_CENTER = "center"
PANEL_INSPECTOR = "inspector"


class MainWindow(
    WorkspaceActions,
    WorkspaceAddressing,
    WorkspaceCatalog,
    WorkspaceSession,
    QMainWindow,
):
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
        self._series = SeriesStore()
        self._trace = TraceBuffer()
        self._facts = SessionFacts()
        self._selected_signal_names: set[str] = set(self.selected_profile.displayed_signals)
        self._favorite_signal_names: set[str] = set(self.selected_profile.favorite_signals)
        self._restoring = False
        self._build_ui()
        self._install_shortcuts()
        self._select_last_profile()
        self._load_profile_dbcs()

    @property
    def selected_profile(self) -> MeasurementProfile:
        return self._state.selected

    # ---- construction --------------------------------------------------

    def _build_ui(self) -> None:
        self.setStyleSheet(APP_STYLE)
        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        self.acquisition_bar = AcquisitionBar([p.name for p in self._state.profiles])
        self.acquisition_bar.profile_changed.connect(self._profile_changed)
        self.acquisition_bar.options_changed.connect(self._acquisition_options_changed)
        self.acquisition_bar.load_dbc_requested.connect(self._choose_dbc)
        self.acquisition_bar.open_trace_requested.connect(self._choose_trace)
        self.acquisition_bar.export_requested.connect(self._open_export_dialog)
        self.acquisition_bar.start_requested.connect(self._start_acquisition)
        self.acquisition_bar.stop_requested.connect(self._stop_acquisition)
        root_layout.addWidget(self.acquisition_bar)

        self.session_note = StateNote()
        root_layout.addWidget(self.session_note)

        self.workspace = QSplitter(Qt.Orientation.Horizontal, objectName="workspaceSplitter")

        self.signals_panel = CollapsiblePanel(translate("workspace.signals"), PANEL_SIGNALS)
        self.dbc_panel = DbcLibraryPanel()
        self.dbc_panel.enabled_changed.connect(self._dbc_enabled_changed)
        self.dbc_panel.remove_requested.connect(self._remove_dbc)
        self.dbc_panel.conflict_resolved.connect(self._resolve_conflict)
        self.signals_panel.body_layout.addWidget(self.dbc_panel)
        self.explorer_panel = SignalExplorerPanel()
        self.explorer_panel.filters_changed.connect(self._refresh_signal_explorer)
        self.explorer_panel.shown_changed.connect(self._signal_shown_changed)
        self.explorer_panel.favorite_changed.connect(self._signal_favorite_changed)
        self.signals_panel.body_layout.addWidget(self.explorer_panel, 1)

        self.trace_graph_panel = CollapsiblePanel(
            translate("workspace.graphs_trace"), PANEL_CENTER
        )
        self._build_center_panel()

        self.inspector_panel = CollapsiblePanel(translate("workspace.inspector"), PANEL_INSPECTOR)
        self.inspector = InspectorPanel()
        self.inspector_panel.body_layout.addWidget(self.inspector)

        for panel in (self.signals_panel, self.trace_graph_panel, self.inspector_panel):
            panel.collapsed_changed.connect(self._persist_layout)
            self.workspace.addWidget(panel)
        self.workspace.setSizes([320, 720, 280])
        self.workspace.splitterMoved.connect(lambda *_: self._persist_layout())
        root_layout.addWidget(self.workspace, 1)
        self.setCentralWidget(root)

        self.progress = QProgressBar(objectName="workProgress")
        self.progress.setAccessibleName(translate("progress.accessible"))
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        self.status = QStatusBar(self)
        self.status.addPermanentWidget(self.progress)
        self.status.showMessage(translate("acquisition.disconnected"))
        self.setStatusBar(self.status)
        self._build_menu()

    def _build_center_panel(self) -> None:
        layout = self.trace_graph_panel.body_layout
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel(translate("workspace.view").upper()))
        self.workspace_mode_selector = QComboBox(objectName="workspaceModeSelector")
        self.workspace_mode_selector.setAccessibleName(translate("workspace.mode_accessible"))
        self.workspace_mode_selector.setToolTip(translate("workspace.mode_accessible"))
        for value, key in WORKSPACE_MODES:
            self.workspace_mode_selector.addItem(translate(key), value)
        self.workspace_mode_selector.currentIndexChanged.connect(self._workspace_mode_changed)
        mode_row.addWidget(self.workspace_mode_selector)
        mode_row.addStretch(1)
        layout.addLayout(mode_row)

        self.center_divider = QSplitter(Qt.Orientation.Vertical, objectName="centerDivider")
        self.graph_panel = GraphStackPanel()
        self.graph_panel.cursors_changed.connect(self._persist_layout)
        self.trace_panel = TraceViewPanel()
        self.trace_panel.set_buffer(self._trace)
        self.trace_panel.filters_changed.connect(self._persist_trace_filters)
        self.trace_panel.record_selected.connect(self._trace_record_selected)
        self.trace_panel.columns_requested.connect(self._open_columns_dialog)
        self.report_panel = ReportPanel()
        self.report_panel.refresh_requested.connect(self._refresh_report)
        self.report_panel.export_requested.connect(self._export_report)
        self.center_divider.addWidget(self.graph_panel)
        self.center_divider.addWidget(self.trace_panel)
        self.center_divider.addWidget(self.report_panel)
        self.center_divider.setSizes([420, 280, 0])
        self.center_divider.splitterMoved.connect(lambda *_: self._persist_layout())
        layout.addWidget(self.center_divider, 1)

    # ---- profiles ------------------------------------------------------

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
        self._save()
        self._show_profile(self.selected_profile)
        self._load_profile_dbcs()

    def _show_profile(self, profile: MeasurementProfile) -> None:
        self._restoring = True
        try:
            self.acquisition_bar.show_profile(profile)
            self.trace_panel.apply_columns(profile.trace_columns)
            self.trace_panel.apply_settings(profile.trace_filter)
            layout = profile.layout
            mode_index = self.workspace_mode_selector.findData(layout.workspace_mode)
            self.workspace_mode_selector.setCurrentIndex(max(0, mode_index))
            if layout.splitter_sizes:
                self.workspace.setSizes(layout.splitter_sizes)
            if layout.divider_sizes:
                self.center_divider.setSizes(layout.divider_sizes)
            for panel in (self.signals_panel, self.trace_graph_panel, self.inspector_panel):
                panel.set_collapsed(panel.key in layout.collapsed_panels)
            self.graph_panel.restore_cursors(layout.cursor_a, layout.cursor_b)
            if layout.fullscreen and not self.isFullScreen():
                self.showFullScreen()
        finally:
            self._restoring = False
        self._apply_workspace_mode(profile.layout.workspace_mode)

    def _acquisition_options_changed(self) -> None:
        profile = self.selected_profile
        self.acquisition_bar.apply_to_profile(profile)
        self._save()
        self.acquisition_bar.show_profile(profile)

    def _save(self) -> None:
        self.selected_profile.updated_at = datetime.now().astimezone().isoformat()
        self._store.save(self._state)

    def _persist_layout(self) -> None:
        if self._restoring:
            return
        layout = self.selected_profile.layout
        layout.splitter_sizes = list(self.workspace.sizes())
        layout.divider_sizes = list(self.center_divider.sizes())
        layout.collapsed_panels = [
            panel.key
            for panel in (self.signals_panel, self.trace_graph_panel, self.inspector_panel)
            if panel.is_collapsed
        ]
        layout.cursor_a = self.graph_panel.cursor_a
        layout.cursor_b = self.graph_panel.cursor_b
        layout.fullscreen = self.isFullScreen()
        self._save()

    def _persist_trace_filters(self) -> None:
        if self._restoring:
            return
        self.selected_profile.trace_filter = self.trace_panel.settings
        self._save()

    def _persist_signal_state(self) -> None:
        profile = self.selected_profile
        available = set(self._catalog.signal_names())
        profile.displayed_signals = sorted(
            name for name in self._selected_signal_names if not available or name in available
        )
        profile.favorite_signals = sorted(self._favorite_signal_names)
        self._save()

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
        self._save()

    # ---- inspector -----------------------------------------------------

    def _trace_record_selected(self, record_index: int) -> None:
        record = self._trace.record(record_index) if record_index >= 0 else None
        self.inspector.show_record(record)

    def selected_record(self) -> TraceRecord | None:
        index = self.trace_panel.selected_index()
        return None if index is None else self._trace.record(index)

    # ---- workspace mode and layout -------------------------------------

    def _workspace_mode_changed(self) -> None:
        mode = str(self.workspace_mode_selector.currentData() or "combo")
        self._apply_workspace_mode(mode)
        if self._restoring:
            return
        self.selected_profile.layout.workspace_mode = mode
        self._save()

    def _apply_workspace_mode(self, mode: str) -> None:
        self.graph_panel.setVisible(mode in {"combo", "graphs"})
        self.trace_panel.setVisible(mode in {"combo", "trace"})
        self.report_panel.setVisible(mode == "report")

    def _toggle_signals_panel(self) -> None:
        self.signals_panel.set_collapsed(not self.signals_panel.is_collapsed)

    def _toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
        self._persist_layout()

    def _focus_trace_filter(self) -> None:
        self.trace_panel.id_filter.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _show_about(self) -> None:
        QMessageBox.information(
            self, translate("menu.about"), translate("menu.about_text")
        )

    # ---- dialogs -------------------------------------------------------

    def _open_columns_dialog(self) -> ColumnsDialog:
        dialog = ColumnsDialog(self.selected_profile.trace_columns, self)
        dialog.columns_changed.connect(self._columns_changed)
        dialog.open()
        return dialog

    def _columns_changed(self) -> None:
        self.trace_panel.apply_columns(self.selected_profile.trace_columns)
        self._save()

    def _open_export_dialog(self) -> ExportDialog:
        dialog = ExportDialog(
            self._series,
            self.graph_panel.signal_names,
            self.graph_panel.cursor_range,
            self.graph_panel.visible_window(),
            self,
        )
        dialog.open()
        return dialog

    # ---- lifecycle -----------------------------------------------------

    def closeEvent(self, event) -> None:  # type: ignore[no-untyped-def]  # noqa: N802
        if self._worker is not None and self._worker.isRunning():
            self._worker.request_stop()
            self._worker.wait(1_000)
        if self._replay_worker is not None and self._replay_worker.isRunning():
            self._replay_worker.request_stop()
            self._replay_worker.wait(1_000)
        super().closeEvent(event)
