"""Menu bar and keyboard shortcut construction for the workspace shell."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtGui import QAction, QKeySequence

from peaklive.i18n import translate


class WorkspaceActions:
    """Builds the File/View/Help menus and the workspace shortcuts.

    Every action carries its shortcut in the tooltip, so an operator can find
    the keyboard path without reading the documentation.
    """

    def _build_menu(self) -> None:
        bar = self.menuBar()
        file_menu = bar.addMenu(translate("menu.file"))
        file_menu.addAction(self._action("menu.load_dbc", self._choose_dbc, "Ctrl+D"))
        self.open_trace_action = self._action("menu.open_trace", self._choose_trace, "Ctrl+O")
        file_menu.addAction(self.open_trace_action)
        file_menu.addAction(self._action("menu.export", self._open_export_dialog, "Ctrl+E"))
        file_menu.addAction(self._action("menu.export_report", self._export_report))
        file_menu.addSeparator()
        file_menu.addAction(
            self._action("menu.save_profile_as", self._save_profile_as, "Ctrl+Shift+S")
        )
        file_menu.addSeparator()
        file_menu.addAction(self._action("menu.quit", self.close, "Ctrl+Q"))

        view_menu = bar.addMenu(translate("menu.view"))
        self.start_action = self._action("menu.start", self._start_acquisition, "F5")
        view_menu.addAction(self.start_action)
        self.stop_action = self._action("menu.stop", self._stop_acquisition, "F6")
        view_menu.addAction(self.stop_action)
        view_menu.addAction(self._action("menu.recording_settings", self._open_recording_dialog))
        view_menu.addSeparator()
        view_menu.addAction(self._action("menu.fit", self.graph_panel.fit, "Ctrl+0"))
        view_menu.addAction(
            self._action("menu.focus_filter", self._focus_trace_filter, "Ctrl+F")
        )
        view_menu.addAction(self._action("menu.fullscreen", self._toggle_fullscreen, "F11"))
        view_menu.addSeparator()
        self._panel_visibility_actions = {
            self.signals_panel.key: self._panel_visibility_action(
                "menu.view_signals", self.signals_panel
            ),
            self.trace_graph_panel.key: self._panel_visibility_action(
                "menu.view_graphs_trace", self.trace_graph_panel
            ),
            self.inspector_panel.key: self._panel_visibility_action(
                "menu.view_inspector", self.inspector_panel
            ),
        }
        for panel in self._layout_panels:
            view_menu.addAction(self._panel_visibility_actions[panel.key])

        help_menu = bar.addMenu(translate("menu.help"))
        help_menu.addAction(self._action("menu.about", self._show_about))

    def _action(self, key: str, slot: Callable[[], None], shortcut: str = "") -> QAction:
        action = QAction(translate(key), self)
        action.setObjectName(key.replace(".", "_"))
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
            action.setToolTip(f"{translate(key)} ({shortcut})")
        action.triggered.connect(slot)
        return action

    def _panel_visibility_action(self, key: str, panel) -> QAction:  # noqa: ANN001
        """A checkable View action that shows/hides one panel, rail included.

        Checked means visible, so the box mirrors what the operator sees
        rather than an internal "hidden" flag. `set_hidden` is idempotent, so
        triggering the action from either the menu or the keyboard always
        converges the panel and the checkmark to the same state.
        """
        action = QAction(translate(key), self)
        action.setObjectName(key.replace(".", "_"))
        action.setCheckable(True)
        action.setChecked(not panel.is_hidden)
        action.toggled.connect(lambda checked, target=panel: target.set_hidden(not checked))
        panel.visibility_changed.connect(
            lambda hidden, target=action: target.setChecked(not hidden)
        )
        return action

    def _sync_visibility_actions(self) -> None:
        """Reconcile every View checkmark with its panel's actual state.

        Needed after profile restoration, where `set_hidden` is called while
        `_restoring` suppresses the persistence path but the checkmark still
        has to reflect whatever the newly loaded profile says.
        """
        for panel in self._layout_panels:
            action = self._panel_visibility_actions[panel.key]
            action.blockSignals(True)
            action.setChecked(not panel.is_hidden)
            action.blockSignals(False)

    def _install_shortcuts(self) -> None:
        self.cursor_a_action = self._action(
            "graph.cursor_a", lambda: self.graph_panel.place_cursor("a"), "Ctrl+1"
        )
        self.cursor_b_action = self._action(
            "graph.cursor_b", lambda: self.graph_panel.place_cursor("b"), "Ctrl+2"
        )
        self.collapse_action = self._action(
            "workspace.signals", self._toggle_signals_panel, "Ctrl+B"
        )
        for action in (self.cursor_a_action, self.cursor_b_action, self.collapse_action):
            self.addAction(action)
