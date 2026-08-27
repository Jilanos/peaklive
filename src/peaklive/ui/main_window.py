"""The workspace shell: composition, wiring, and profile persistence.

Every panel lives in `peaklive.ui.panels`. This module owns the session state
the panels share — the DBC catalog, the bounded series store, the trace buffer,
the session facts, and the workers — and keeps the measurement profile in sync.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
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
from peaklive.services.dbc_worker import CatalogOperation, DbcCatalogWorker
from peaklive.services.lifecycle import AcquisitionLifecycle
from peaklive.services.profiles import ProfileState, ProfileStore
from peaklive.services.replay_worker import ReplayWorker
from peaklive.services.worker import AcquisitionWorker
from peaklive.ui.actions import WorkspaceActions
from peaklive.ui.addressing import WorkspaceAddressing
from peaklive.ui.catalog_controller import WorkspaceCatalog
from peaklive.ui.dialogs import ColumnsDialog, ExportDialog
from peaklive.ui.layout_reflow import WorkspaceReflow
from peaklive.ui.panels import (
    AcquisitionBar,
    DbcLibraryPanel,
    InspectorPanel,
    SignalExplorerPanel,
)
from peaklive.ui.panels.signal_explorer import SIGNAL_KEY_ROLE
from peaklive.ui.session_controller import (
    SHUTDOWN_TIMEOUT_MS,
    WorkspaceSession,
    abandon_worker,
)
from peaklive.ui.theme import APP_STYLE
from peaklive.ui.widgets import CollapsiblePanel, StateNote
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
    WorkspaceReflow,
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
        self._lifecycle = AcquisitionLifecycle()
        self._shutdown_timeout_ms = SHUTDOWN_TIMEOUT_MS
        self._shutdown_timer = QTimer(self)
        self._shutdown_timer.setSingleShot(True)
        self._shutdown_timer.timeout.connect(self._shutdown_timed_out)
        self._catalog = DbcCatalog()
        self._catalog_worker: DbcCatalogWorker | None = None
        self._catalog_queue: list[CatalogOperation] = []
        self._catalog_generation = 0
        self._series = SeriesStore()
        self._trace = TraceBuffer()
        self._facts = SessionFacts()
        self._selected_signal_names: set[str] = set(self.selected_profile.displayed_signals)
        self._favorite_signal_names: set[str] = set(self.selected_profile.favorite_signals)
        self._restoring = False
        self._expanded_widths: dict[str, int] = dict(self.selected_profile.layout.panel_widths)
        self._build_ui()
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
            self._expanded_widths = dict(layout.panel_widths)
            for panel in self._layout_panels:
                panel.set_collapsed(panel.key in layout.collapsed_panels)
            self._reflow_workspace()
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
        self._remember_panel_widths()
        layout = self.selected_profile.layout
        layout.splitter_sizes = list(self.workspace.sizes())
        layout.divider_sizes = list(self.center_divider.sizes())
        layout.panel_widths = dict(self._expanded_widths)
        layout.collapsed_panels = [
            panel.key for panel in self._layout_panels if panel.is_collapsed
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

    def _persist_signal_state(self, signal_names: tuple[str, ...] | None = None) -> None:
        """Persist the selection, reusing already-computed names when given.

        A catalog commit has just walked every message off-thread; recomputing
        the same names here would put that work straight back on the UI thread.
        """
        profile = self.selected_profile
        available = set(
            self._catalog.signal_names() if signal_names is None else signal_names
        )
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
        """Close without ever waiting unbounded on a worker.

        The wait is a courtesy so a healthy worker finalizes its capture before
        the process ends. A worker that does not return within it is abandoned
        rather than allowed to hold the close: its generation is retired, so any
        signal it emits afterwards reaches nobody, and its recording stays on
        disk as recoverable `.partial` segments.
        """
        self._shutdown_timer.stop()
        if self._worker is not None and self._worker.isRunning():
            self._worker.request_stop()
            self._worker.wait(self._shutdown_timeout_ms)
        self._lifecycle.reset()
        abandon_worker(self._worker)
        self._worker = None
        self._cancel_catalog_operation()
        if self._catalog_worker is not None:
            self._catalog_worker.wait(self._shutdown_timeout_ms)
            abandon_worker(self._catalog_worker)
            self._catalog_worker = None
        if self._replay_worker is not None and self._replay_worker.isRunning():
            self._replay_worker.request_stop()
            self._replay_worker.wait(1_000)
        super().closeEvent(event)
