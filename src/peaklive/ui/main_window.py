"""The workspace shell: composition, wiring, and profile persistence.

Every panel lives in `peaklive.ui.panels`. This module owns the session state
the panels share — the DBC catalog, the bounded series store, the trace buffer,
the session facts, and the workers — and keeps the measurement profile in sync.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
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
from peaklive.analysis import DbcCatalog, TraceRecord
from peaklive.diagnostics import set_operator_notifier
from peaklive.domain import MeasurementProfile
from peaklive.i18n import translate
from peaklive.services.dbc_worker import CatalogOperation, DbcCatalogWorker
from peaklive.services.lifecycle import AcquisitionLifecycle
from peaklive.services.profiles import ProfileState, ProfileStore
from peaklive.services.replay_worker import ReplayWorker
from peaklive.services.worker import AcquisitionWorker
from peaklive.ui.actions import WorkspaceActions
from peaklive.ui.addressing import WorkspaceAddressing
from peaklive.ui.catalog_controller import WorkspaceCatalog
from peaklive.ui.dialogs import ColumnsDialog, ExportDialog, RecordingSettingsDialog
from peaklive.ui.ingest_controller import WorkspaceIngest
from peaklive.ui.layout_reflow import WorkspaceReflow
from peaklive.ui.panels import (
    AcquisitionBar,
    DbcLibraryPanel,
    InspectorPanel,
    SignalExplorerPanel,
)
from peaklive.ui.panels.signal_explorer import SIGNAL_KEY_ROLE
from peaklive.ui.profile_controller import WorkspaceProfiles
from peaklive.ui.session_controller import SHUTDOWN_TIMEOUT_MS, WorkspaceSession
from peaklive.ui.theme import APP_STYLE
from peaklive.ui.widgets import CollapsiblePanel, StateNote
from peaklive.ui.window_shutdown import WorkspaceShutdown
from peaklive.ui.workspace_center import WorkspaceCenter
from peaklive.version import build_info

__all__ = ["SIGNAL_KEY_ROLE", "MainWindow"]

PANEL_SIGNALS = "signals"
PANEL_CENTER = "center"
PANEL_INSPECTOR = "inspector"


class MainWindow(
    WorkspaceActions,
    WorkspaceAddressing,
    WorkspaceCatalog,
    WorkspaceCenter,
    WorkspaceIngest,
    WorkspaceProfiles,
    WorkspaceReflow,
    WorkspaceSession,
    WorkspaceShutdown,
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
        self._lifecycle = AcquisitionLifecycle()
        self._shutdown_timeout_ms = SHUTDOWN_TIMEOUT_MS
        self._shutdown_timer = QTimer(self)
        self._shutdown_timer.setSingleShot(True)
        self._shutdown_timer.timeout.connect(self._shutdown_timed_out)
        self._init_presentation_queue()
        self._init_graph_refresh()
        self._catalog = DbcCatalog()
        self._catalog_worker: DbcCatalogWorker | None = None
        self._catalog_queue: list[CatalogOperation] = []
        self._catalog_generation = 0
        self._init_session_state()
        # A replay owns one presentation timer for the lifetime of the window.
        # Creating one for every opened trace left inactive QObject timers
        # accumulating in long-running bench sessions.
        self._pending_replay_batches = []
        self._pending_replay_finish_generation: int | None = None
        self._replay_generation = 0
        self._replay_presentation_timer = QTimer(self)
        self._replay_presentation_timer.setSingleShot(True)
        self._replay_presentation_timer.setInterval(1)
        self._replay_presentation_timer.timeout.connect(self._drain_replay_batch)
        self._selected_signal_names: set[str] = set(self.selected_profile.displayed_signals)
        self._favorite_signal_names: set[str] = set(self.selected_profile.favorite_signals)
        self._restoring = False
        self._expanded_widths: dict[str, int] = dict(self.selected_profile.layout.panel_widths)
        self._build_ui()
        set_operator_notifier(lambda message: self.session_note.show_message(message, "error"))
        self._install_shortcuts()
        self._select_last_profile()
        self._load_profile_dbcs()

    @property
    def selected_profile(self) -> MeasurementProfile:
        return self._state.selected

    @property
    def _layout_panels(self) -> tuple[CollapsiblePanel, ...]:
        return (self.signals_panel, self.trace_graph_panel, self.inspector_panel)

    # ---- construction --------------------------------------------------

    def _build_ui(self) -> None:
        # Instrument controls should open directly.  These are application-wide
        # Qt popup effects, covering profile/channel/bitrate and every owned
        # combo/menu without changing keyboard or focus behaviour.
        QApplication.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)
        QApplication.setEffectEnabled(Qt.UIEffect.UI_AnimateMenu, False)
        self.setStyleSheet(APP_STYLE)
        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        self.acquisition_bar = AcquisitionBar([p.name for p in self._state.profiles])
        self.acquisition_bar.profile_changed.connect(self._profile_changed)
        self.acquisition_bar.save_profile_as_requested.connect(self._save_profile_as)
        self.acquisition_bar.options_changed.connect(self._acquisition_options_changed)
        self.acquisition_bar.load_dbc_requested.connect(self._choose_dbc)
        self.acquisition_bar.open_trace_requested.connect(self._choose_trace)
        self.acquisition_bar.export_requested.connect(self._open_export_dialog)
        self.acquisition_bar.start_requested.connect(self._start_acquisition)
        self.acquisition_bar.stop_requested.connect(self._stop_acquisition)
        self.acquisition_bar.recover_requested.connect(self._recover_timed_out_acquisition)
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

        for panel in self._layout_panels:
            panel.collapsed_changed.connect(self._panel_collapse_changed)
            self.workspace.addWidget(panel)
        self.workspace.setStretchFactor(1, 1)
        self.workspace.setSizes([320, 720, 280])
        self.workspace.splitterMoved.connect(lambda *_: self._persist_layout())
        root_layout.addWidget(self.workspace, 1)
        self.setCentralWidget(root)

        self.progress = QProgressBar(objectName="workProgress")
        self.progress.setAccessibleName(translate("progress.accessible"))
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        self.build = QLabel(objectName="buildIdentifier")
        identifier = build_info().identifier
        self.build.setText(translate("app.build_label").format(identifier=identifier))
        self.build.setAccessibleName(translate("app.build_accessible"))
        self.build.setToolTip(translate("app.build_tooltip").format(identifier=identifier))
        self.status = QStatusBar(self)
        self.status.addPermanentWidget(self.build)
        self.status.addPermanentWidget(self.progress)
        self.status.showMessage(translate("acquisition.disconnected"))
        self.setStatusBar(self.status)
        self._build_menu()

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
        QMessageBox.information(self, translate("menu.about"), self.about_text())

    def about_text(self) -> str:
        """Describe the product and, exactly, the build the operator is running."""
        info = build_info()
        lines = [
            translate("menu.about_text"),
            "",
            translate("menu.about_build").format(identifier=info.identifier),
            translate("menu.about_packaged" if info.packaged else "menu.about_source"),
        ]
        if info.is_test_rebuild:
            lines.append(translate("menu.about_test_rebuild").format(tag=info.build_tag))
        return "\n".join(lines)

    # ---- dialogs -------------------------------------------------------

    def _open_columns_dialog(self) -> ColumnsDialog:
        dialog = ColumnsDialog(self.selected_profile.trace_columns, self)
        dialog.columns_changed.connect(self._columns_changed)
        dialog.open()
        return dialog

    def _columns_changed(self) -> None:
        self.trace_panel.apply_columns(self.selected_profile.trace_columns)
        self._save()

    def _open_recording_dialog(self) -> RecordingSettingsDialog:
        dialog = RecordingSettingsDialog(self.selected_profile, parent=self)
        dialog.recording_changed.connect(self._recording_changed)
        dialog.open()
        return dialog

    def _recording_changed(self) -> None:
        self._save()
        self.acquisition_bar.show_profile(self.selected_profile)

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
