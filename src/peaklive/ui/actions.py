"""Menu bar and keyboard shortcut construction for the workspace shell."""

from __future__ import annotations

from collections.abc import Callable
from weakref import proxy

from PySide6.QtGui import QAction, QActionGroup, QKeySequence
from PySide6.QtWidgets import QComboBox, QMenu, QMenuBar

from peaklive.analysis import CatalogView
from peaklive.i18n import translate
from peaklive.ui.panels.graph_navigation import FOLLOW_MODE_FULL, FOLLOW_MODE_TRAILING


class WorkspaceActions:
    """Builds the File/View/Help menus and the workspace shortcuts.

    Every action carries its shortcut in the tooltip, so an operator can find
    the keyboard path without reading the documentation.
    """

    def _build_menu(self) -> None:
        # Menus, actions and submenus are registered as they are built so a
        # language change can re-caption the very same objects. Rebuilding the
        # bar instead would mint new QActions, dropping the enable/check state
        # the lifecycle maintains and duplicating panel signal connections.
        self._translated_actions: list[tuple[QAction, str, str]] = []
        self._translated_menus: list[tuple[QMenu, str]] = []
        bar = self.menuBar()
        file_menu = self._menu(bar, "menu.file")
        file_menu.addAction(self._action("menu.load_dbc", self._choose_dbc, "Ctrl+D"))
        self.open_trace_action = self._action("menu.open_trace", self._choose_trace, "Ctrl+O")
        file_menu.addAction(self.open_trace_action)
        file_menu.addAction(self._action("menu.export", self._open_export_dialog, "Ctrl+E"))
        file_menu.addAction(self._action("menu.export_report", self._export_report))
        file_menu.addSeparator()
        file_menu.addAction(self._action("menu.quit", self.close, "Ctrl+Q"))

        recording_menu = self._menu(bar, "menu.recording")
        self.start_action = self._action("menu.start", self._start_acquisition, "F5")
        recording_menu.addAction(self.start_action)
        self.stop_action = self._action("menu.stop", self._stop_acquisition, "F6")
        recording_menu.addAction(self.stop_action)
        recording_menu.addSeparator()
        recording_menu.addAction(
            self._action("menu.recording_settings", self._open_recording_dialog)
        )

        setup_menu = self._menu(bar, "menu.setup")
        self._setup_menu_refreshers = [
            # The setup strip that used to carry this selector is gone
            # (item_141); the combo still owns selection and persistence, so
            # this submenu drives it rather than duplicating it.
            self._build_choice_submenu(
                setup_menu, "menu.profile", self.acquisition_bar.profile_selector
            ),
        ]
        setup_menu.addAction(
            self._action("menu.save_profile_as", self._save_profile_as, "Ctrl+Shift+S")
        )
        setup_menu.addSeparator()
        self._setup_menu_refreshers += [
            self._build_choice_submenu(
                setup_menu, "menu.channel", self.acquisition_bar.channel_selector
            ),
            self._build_choice_submenu(
                setup_menu, "menu.bitrate", self.acquisition_bar.bitrate_selector
            ),
            self._build_choice_submenu(
                setup_menu, "menu.controller_mode", self.acquisition_bar.controller_mode_selector
            ),
        ]
        setup_menu.addSeparator()
        self._build_language_menu(setup_menu)

        view_menu = self._menu(bar, "menu.view")
        view_menu.addAction(self._action("menu.fit", self.graph_panel.fit, "Ctrl+0"))
        view_menu.addAction(
            self._action("menu.focus_filter", self._focus_trace_filter, "Ctrl+F")
        )
        view_menu.addAction(self._action("menu.fullscreen", self._toggle_fullscreen, "F11"))
        view_menu.addSeparator()
        self._build_follow_live_menu(view_menu)
        view_menu.addSeparator()

        self._dbc_menu = self._menu(bar, "dbc.menu")
        self._dbc_menu.setObjectName("menu_dbc")
        self._dbc_menu_entries: dict[str, QAction] = {}
        self._dbc_remove_actions: dict[str, QAction] = {}
        self._dbc_conflict_actions: list[QAction] = []

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

        help_menu = self._menu(bar, "menu.help")
        help_menu.addAction(self._action("menu.about", self._show_about))

    def _build_choice_submenu(self, menu: QMenu, key: str, combo: QComboBox) -> Callable[[], None]:
        """A cascading submenu mirroring one combo box's items and selection.

        The combo stays the single source of truth: choosing a submenu entry
        just drives the combo's current index, which already carries the
        existing persistence and lifecycle-safety wiring. Rebuilding on every
        `currentIndexChanged` keeps the menu correct even when the combo's
        item list itself changes (e.g. an unrecognised profile channel).
        """
        submenu = self._menu(menu, key)
        submenu.setObjectName(key.replace(".", "_"))
        object_prefix = key.replace(".", "_")
        group = QActionGroup(submenu)
        group.setExclusive(True)

        def rebuild() -> None:
            # A choice can rebuild its own menu from inside triggered().
            # Retire actions after that signal returns, and reuse the group.
            for action in submenu.actions():
                submenu.removeAction(action)
                action.deleteLater()
            for index in range(combo.count()):
                action = QAction(combo.itemText(index), submenu)
                action.setObjectName(f"{object_prefix}_{index}")
                action.setCheckable(True)
                action.setChecked(index == combo.currentIndex())
                action.setEnabled(combo.isEnabled())
                action.triggered.connect(
                    lambda _checked=False, i=index: combo.setCurrentIndex(i)
                )
                group.addAction(action)
                submenu.addAction(action)

        rebuild()
        combo.currentIndexChanged.connect(lambda *_: rebuild())
        return rebuild

    def _build_follow_live_menu(self, view_menu: QMenu) -> None:
        """View > Follow live: Full acquisition span (default) or Trailing window."""
        submenu = self._menu(view_menu, "graph.follow_live_menu")
        submenu.setObjectName("menu_follow_live")
        group = QActionGroup(self)
        group.setExclusive(True)
        owner = proxy(self)
        self._follow_live_mode_actions: dict[str, QAction] = {}
        for mode, key, object_name in (
            (FOLLOW_MODE_FULL, "graph.follow_live_full", "menu_follow_live_full"),
            (FOLLOW_MODE_TRAILING, "graph.follow_live_trailing", "menu_follow_live_trailing"),
        ):
            action = QAction(translate(key), self)
            action.setObjectName(object_name)
            self._translated_actions.append((action, key, ""))
            action.setCheckable(True)
            action.setChecked(mode == FOLLOW_MODE_FULL)
            action.triggered.connect(
                lambda _checked=False, m=mode: owner._follow_live_mode_changed(m)
            )
            group.addAction(action)
            submenu.addAction(action)
            self._follow_live_mode_actions[mode] = action

    def _sync_follow_live_mode_actions(self, mode: str) -> None:
        for action_mode, action in getattr(self, "_follow_live_mode_actions", {}).items():
            action.blockSignals(True)
            action.setChecked(action_mode == mode)
            action.blockSignals(False)

    def _follow_live_mode_changed(self, mode: str) -> None:
        self.graph_panel.set_follow_live_mode(mode)
        if self._restoring:
            return
        self.selected_profile.layout.follow_live_mode = mode
        self._save()

    def _refresh_dbc_menu(self, view: CatalogView) -> None:
        """Rebuild the DBC menu from one prepared catalog view.

        The menu is the sole DBC control surface (item_136): one checkable
        entry per loaded database, an Add command, and Remove/Conflicts
        submenus built only when there is something to remove or resolve.
        """
        menu = self._dbc_menu
        # Retire submenus explicitly: clear() removes their menu actions but
        # leaves the child QMenus alive. Own all leaf actions in their menus.
        for action in menu.actions():
            child_menu = action.menu()
            if child_menu is not None:
                child_menu.deleteLater()
        menu.clear()
        self._dbc_menu_entries = {}
        self._dbc_remove_actions = {}
        self._dbc_conflict_actions = []

        add_action = self._action("dbc.menu_add", self._choose_dbc)
        add_action.setParent(menu)
        menu.addAction(add_action)
        # Qt owns these callbacks. They must not retain the entire window in
        # a Python cycle that another worker's allocation may collect later.
        owner = proxy(self)
        if view.definitions:
            menu.addSeparator()
        for definition in view.definitions:
            action = QAction(f"{definition.path.name} · {definition.short_hash}", menu)
            action.setObjectName(f"dbc_entry_{definition.content_hash}")
            action.setCheckable(True)
            action.setChecked(view.is_enabled(definition.content_hash))
            action.toggled.connect(
                lambda checked, h=definition.content_hash: owner._dbc_enabled_changed(h, checked)
            )
            menu.addAction(action)
            self._dbc_menu_entries[definition.content_hash] = action

        if view.definitions:
            menu.addSeparator()
            remove_menu = menu.addMenu(translate("dbc.menu_remove"))
            remove_menu.setObjectName("menu_dbc_remove")
            for definition in view.definitions:
                action = QAction(definition.path.name, remove_menu)
                action.setObjectName(f"dbc_remove_{definition.content_hash}")
                action.triggered.connect(
                    lambda _checked=False, h=definition.content_hash: owner._remove_dbc(h)
                )
                remove_menu.addAction(action)
                self._dbc_remove_actions[definition.content_hash] = action

        unresolved = view.unresolved_conflicts
        if unresolved:
            menu.addSeparator()
            conflicts_menu = menu.addMenu(translate("dbc.menu_conflicts"))
            conflicts_menu.setObjectName("menu_dbc_conflicts")
            for conflict in unresolved:
                for definition in conflict.candidates:
                    label = translate("dbc.conflict_entry").format(
                        identifier=(
                            f"0x{conflict.arbitration_id:X}"
                            f"{'x' if conflict.is_extended_id else ''}"
                        ),
                        name=definition.path.name,
                    )
                    action = QAction(label, conflicts_menu)
                    action.triggered.connect(
                        lambda _checked=False,
                        arbitration_id=conflict.arbitration_id,
                        is_extended_id=conflict.is_extended_id,
                        content_hash=definition.content_hash: owner._resolve_conflict(
                            arbitration_id, is_extended_id, content_hash
                        )
                    )
                    conflicts_menu.addAction(action)
                    self._dbc_conflict_actions.append(action)
        self._sync_dbc_menu_busy()

    def _sync_dbc_menu_busy(self) -> None:
        """Disable the whole DBC menu while a catalog operation is in flight.

        A menu action triggered mid-mutation would queue a second operation
        against a catalog view that is about to change underneath it; disabling
        the menu for that one moment is simpler than reconciling overlapping
        mutations against a stale view.
        """
        menu = getattr(self, "_dbc_menu", None)
        if menu is not None:
            menu.setEnabled(self._catalog_worker is None)

    def _sync_setup_menu_enabled(self) -> None:
        """Reconcile every Setup submenu's items with their combo's gating.

        Lifecycle gating disables the channel/bitrate/mode combos without
        necessarily changing their current index, so `currentIndexChanged`
        never fires — the submenus need their own refresh hook after a
        lifecycle-phase change.
        """
        for refresh in getattr(self, "_setup_menu_refreshers", ()):
            refresh()

    def _menu(self, parent: QMenuBar | QMenu, key: str) -> QMenu:
        menu = parent.addMenu(translate(key))
        self._translated_menus.append((menu, key))
        return menu

    def _action(self, key: str, slot: Callable[[], None], shortcut: str = "") -> QAction:
        action = QAction(translate(key), self)
        action.setObjectName(key.replace(".", "_"))
        self._translated_actions.append((action, key, shortcut))
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
        self._translated_actions.append((action, key, ""))
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
