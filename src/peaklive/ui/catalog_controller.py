"""DBC catalog and signal-selection coordination for the workspace shell."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from peaklive.i18n import translate


class WorkspaceCatalog:
    """Owns the DBC lifecycle and the shown/favorite signal selection.

    Enable, disable, and remove all funnel through here so the profile, the
    catalog, the explorer, and the graph stack can never disagree about which
    databases are active.
    """

    # ---- DBC -----------------------------------------------------------

    def _load_profile_dbcs(self) -> None:
        self._catalog.clear()
        for configured_path in self.selected_profile.dbc_paths:
            path = Path(configured_path)
            if path.exists():
                try:
                    self._catalog.load(path)
                except (OSError, ValueError) as error:
                    self._report_dbc_error(path, error)
        disabled = set(self.selected_profile.trace_filters.get("disabled_dbc_hashes", []))
        for definition in self._catalog.definitions:
            self._catalog.set_enabled(
                definition.content_hash, definition.content_hash not in disabled
            )
        for raw_id, content_hash in dict(
            self.selected_profile.trace_filters.get("dbc_conflict_resolutions", {})
        ).items():
            try:
                self._catalog.resolve(int(raw_id), str(content_hash))
            except (KeyError, ValueError):
                continue
        self.dbc_panel.refresh(self._catalog)
        self._refresh_signal_explorer()
        self._sync_graphs()

    def _choose_dbc(self) -> None:
        selected, _ = QFileDialog.getOpenFileNames(
            self, translate("dbc.load_dialog"), "", translate("dbc.load_filter")
        )
        if not selected:
            return
        self._begin_work(translate("dbc.loading").format(count=len(selected)))
        try:
            for item in selected:
                self._load_dbc_path(Path(item))
        finally:
            self._end_work()

    def _load_dbc_path(self, path: Path) -> None:
        try:
            definition = self._catalog.load(path)
        except (OSError, ValueError) as error:
            self._report_dbc_error(path, error)
            return
        profile = self.selected_profile
        if str(path) not in profile.dbc_paths:
            profile.dbc_paths.append(str(path))
            self._save()
        self._catalog.set_enabled(definition.content_hash, True)
        if not self._selected_signal_names:
            first_signal = next(iter(self._catalog.signal_names()), None)
            if first_signal is not None:
                self._selected_signal_names.add(first_signal)
                self._persist_signal_state()
        self._persist_dbc_state()
        self.dbc_panel.refresh(self._catalog)
        self._refresh_signal_explorer()
        self._sync_graphs()
        self.status.showMessage(translate("dbc.loaded").format(name=path.name))

    def _report_dbc_error(self, path: Path, error: Exception) -> None:
        self._facts.record_anomaly("dbc_error")
        self.dbc_panel.show_error(
            translate("dbc.load_failed").format(name=path.name, message=error)
        )

    def _dbc_enabled_changed(self, content_hash: str, enabled: bool) -> None:
        self._catalog.set_enabled(content_hash, enabled)
        self._persist_dbc_state()
        self.dbc_panel.set_row_state(content_hash, enabled)
        self._refresh_signal_explorer()
        self._sync_graphs()

    def _remove_dbc(self, content_hash: str) -> None:
        removed = next(
            (
                definition
                for definition in self._catalog.definitions
                if definition.content_hash == content_hash
            ),
            None,
        )
        self._catalog.remove(content_hash)
        if removed is not None:
            profile = self.selected_profile
            profile.dbc_paths = [
                configured for configured in profile.dbc_paths if configured != str(removed.path)
            ]
        self._selected_signal_names = {
            name for name in self._selected_signal_names if name in self._catalog.signal_names()
        }
        self._persist_signal_state()
        self._persist_dbc_state()
        self.dbc_panel.refresh(self._catalog)
        self._refresh_signal_explorer()
        self._sync_graphs()

    def _remove_selected_dbc(self) -> None:
        self.dbc_panel._remove_current()

    def _resolve_conflict(self, arbitration_id: int, content_hash: str) -> None:
        self._catalog.resolve(arbitration_id, content_hash)
        self._persist_dbc_state()
        name = next(
            (
                definition.path.name
                for definition in self._catalog.definitions
                if definition.content_hash == content_hash
            ),
            content_hash[:8],
        )
        self.dbc_panel.refresh(self._catalog)
        self.status.showMessage(
            translate("dbc.conflict_resolved").format(
                arbitration_id=arbitration_id, name=name
            )
        )

    # ---- signals -------------------------------------------------------

    def _refresh_signal_explorer(self) -> None:
        self.explorer_panel.refresh(
            self._catalog.signal_references(),
            self._selected_signal_names,
            self._favorite_signal_names,
        )

    def _signal_shown_changed(self, signal_name: str, shown: bool) -> None:
        if shown:
            self._selected_signal_names.add(signal_name)
        else:
            self._selected_signal_names.discard(signal_name)
            self._series.drop(signal_name)
        self._persist_signal_state()
        self._sync_graphs()

    def _signal_favorite_changed(self, signal_name: str, favorite: bool) -> None:
        if favorite:
            self._favorite_signal_names.add(signal_name)
        else:
            self._favorite_signal_names.discard(signal_name)
        self._persist_signal_state()

    def _sync_graphs(self) -> None:
        self.graph_panel.sync(self._series, self._selected_signal_names)
