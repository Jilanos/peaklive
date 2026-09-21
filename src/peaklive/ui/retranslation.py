"""Re-captioning the whole shell in place after a language change.

Nothing here rebuilds a widget, a menu action or a worker connection. Every
surface is re-read from the catalog onto the objects that already exist, which
is what lets an operator change language during a live capture and find the
session, the selection and the viewport exactly as they left them.
"""

from __future__ import annotations

from PySide6.QtWidgets import QDialog

from peaklive.i18n import current_locale, render, translate
from peaklive.ui.workspace_center import WORKSPACE_MODES
from peaklive.version import build_info


class WorkspaceRetranslation:
    """Pushes the active language through every surface the shell owns."""

    def _set_status(self, key: str, **params: object) -> None:
        """Show a status-bar message and remember what it meant.

        The key and its parameters are retained rather than the finished
        sentence, so the same message can be re-rendered in another language
        without parsing the prose back apart.
        """
        self._status_message = (key, params)
        self.status.showMessage(render(key, **params))

    def retranslate(self) -> None:
        self.setWindowTitle(translate("app.title"))
        self._retranslate_panels()
        self._retranslate_status()
        self._retranslate_menus()
        for dialog in self.findChildren(QDialog):
            retranslate = getattr(dialog, "retranslate", None)
            if retranslate is not None:
                retranslate()

    def _retranslate_panels(self) -> None:
        for panel in self._layout_panels:
            panel.retranslate()
        self.acquisition_bar.retranslate()
        self.workspace_header.retranslate()
        self.signal_summary_panel.retranslate()
        self.explorer_panel.retranslate()
        self.inspector.retranslate()
        self.graph_panel.retranslate()
        self.trace_panel.retranslate()
        self.report_panel.retranslate()
        # Rewritten by stable item data: the selector must not change index,
        # which would persist a workspace-mode change nobody asked for.
        for value, key in WORKSPACE_MODES:
            index = self.workspace_mode_selector.findData(value)
            if index >= 0:
                self.workspace_mode_selector.setItemText(index, translate(key))
        self.session_note.retranslate()

    def _retranslate_status(self) -> None:
        identifier = build_info().identifier
        self.build.setText(translate("app.build_label").format(identifier=identifier))
        self.build.setAccessibleName(translate("app.build_accessible"))
        self.build.setToolTip(translate("app.build_tooltip").format(identifier=identifier))
        self.progress.setAccessibleName(translate("progress.accessible"))
        message = getattr(self, "_status_message", None)
        if message is not None:
            key, params = message
            self.status.showMessage(render(key, **params))

    def _retranslate_menus(self) -> None:
        for menu, key in self._translated_menus:
            menu.setTitle(translate(key))
        for action, key, shortcut in self._translated_actions:
            action.setText(translate(key))
            if shortcut:
                action.setToolTip(f"{translate(key)} ({shortcut})")
        # The Setup submenus mirror their combo's item text, which has just
        # changed; the combos never emitted an index change, so nothing else
        # would refresh them.
        self._sync_setup_menu_enabled()
        self._sync_language_actions()
        self._refresh_dbc_menu(self._catalog.view())

    @property
    def interface_locale(self) -> str:
        """The language the shell is currently showing."""
        return current_locale()
