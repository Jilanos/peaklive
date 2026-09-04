"""Measurement setup lifecycle for the workspace shell.

Selecting, duplicating, showing, and persisting a measurement profile is one
concern, and it is the only place that writes ``profiles.json``. Keeping it out
of the shell module leaves `MainWindow` as composition and wiring, and gives
the Save As flow — prompt, validation, atomic write, selection — a single home.
"""

from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import QInputDialog

from peaklive.diagnostics import logger
from peaklive.domain import MeasurementProfile
from peaklive.i18n import translate
from peaklive.services.profiles import ProfileNameError
from peaklive.ui.debounce import SAVE_DEBOUNCE_MS, Debouncer


class WorkspaceProfiles:
    """Owns profile selection, duplication, restoration, and persistence."""


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
        # Any debounced edit still pending belongs to the profile being left,
        # so it must land before its identity changes underneath it.
        self._flush_save()
        self._state.last_profile_id = self._state.profiles[index].identifier
        self._selected_signal_names = set(self.selected_profile.displayed_signals)
        self._favorite_signal_names = set(self.selected_profile.favorite_signals)
        self._save()
        self._show_profile(self.selected_profile)
        self._load_profile_dbcs()

    def _save_profile_as(self) -> None:
        """Duplicate the active setup under an operator-supplied name.

        Nothing is changed until the store has accepted the name and written
        the file: a cancelled prompt, a blank name, a duplicate name, or a
        failed write all leave the existing setups exactly as they were.
        """
        suggested = translate("profile.save_as_suggested").format(name=self.selected_profile.name)
        name, accepted = QInputDialog.getText(
            self,
            translate("profile.save_as_button"),
            translate("profile.save_as_prompt"),
            text=suggested,
        )
        if not accepted:
            return
        try:
            copy = self._store.save_as(self._state, name)
        except ProfileNameError as error:
            self.session_note.show_message(str(error), "warning")
            return
        except OSError as error:
            self.session_note.show_message(
                translate("profile.save_as_failed").format(message=error), "error"
            )
            logger().exception("Could not save the measurement setup copy")
            return
        selector = self.profile_selector
        selector.blockSignals(True)
        selector.addItem(copy.name)
        selector.blockSignals(False)
        # Selecting the appended row runs the ordinary profile-change path, so
        # the copy is adopted exactly the way a manual switch would adopt it.
        selector.setCurrentIndex(len(self._state.profiles) - 1)
        self.session_note.clear_message()
        self.status.showMessage(translate("profile.save_as_saved").format(name=copy.name))

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
            self.graph_panel.set_measurement_values_visible(profile.measurement_values_visible)
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
        try:
            self._store.save(self._state)
        except OSError as error:
            # Persistence is useful, but must never make an input slot take
            # down the interactive session or discard its in-memory state.
            self.session_note.show_message(str(error), "warning")
            logger().exception("Could not save measurement profiles")

    @property
    def _save_debouncer(self) -> Debouncer:
        """Coalesce a burst of persistence triggers into one write.

        Created lazily so mixin composition order never has to reserve an
        `__init__` slot for it; every high-frequency `_persist_*` caller
        shares this single instance and its single pending write.
        """
        debouncer = getattr(self, "_save_debouncer_instance", None)
        if debouncer is None:
            # A lambda, not the bound method: `_save` is looked up fresh on
            # every fire, so a subclass or test override installed after
            # this lazily-created debouncer still takes effect.
            debouncer = Debouncer(SAVE_DEBOUNCE_MS, lambda: self._save(), self)
            self._save_debouncer_instance = debouncer
        return debouncer

    def _schedule_save(self) -> None:
        """Persist after a burst of edits goes quiet, not once per edit."""
        self._save_debouncer.trigger()

    def _flush_save(self) -> None:
        """Persist a pending debounced edit immediately.

        Called wherever a delayed write could otherwise be lost or land in
        the wrong place: switching profiles, and closing the window.
        """
        self._save_debouncer.flush()

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
        self._schedule_save()

    def _persist_measurement_visibility(self, visible: bool) -> None:
        if self._restoring:
            return
        self.selected_profile.measurement_values_visible = visible
        self._schedule_save()

    def _persist_trace_filters(self) -> None:
        if self._restoring:
            return
        self.selected_profile.trace_filter = self.trace_panel.settings
        self._schedule_save()

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
        self._schedule_save()

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
        self._schedule_save()
