"""The shell's ownership of the interface language.

The preference is application-scoped: it is read before any widget exists, and
selecting another measurement profile never touches it.
"""

from __future__ import annotations

from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QMenu, QMessageBox

from peaklive.diagnostics import logger
from peaklive.i18n import (
    LOCALE_AUTONYMS,
    SUPPORTED_LOCALES,
    current_locale,
    set_locale,
    translate,
)
from peaklive.services.ui_settings import UiSettingsStore


class WorkspaceLocale:
    """Loads, applies and persists the application's interface language."""

    def _init_locale(self, ui_settings: UiSettingsStore | None) -> None:
        """Adopt the stored language before the first widget is constructed."""
        self._ui_settings = ui_settings or UiSettingsStore()
        set_locale(self._ui_settings.load().locale)

    def _build_language_menu(self, setup_menu: QMenu) -> None:
        """Setup > Language: the two locales, exclusive, the active one checked.

        The entries are named by their autonyms, which are the same words in
        either language, and carry their stable `en`/`fr` code as action data
        rather than being identified by the caption shown.
        """
        submenu = self._menu(setup_menu, "menu.language")
        submenu.setObjectName("menu_language")
        group = QActionGroup(submenu)
        group.setExclusive(True)
        self._language_actions: dict[str, QAction] = {}
        for locale in SUPPORTED_LOCALES:
            action = QAction(LOCALE_AUTONYMS[locale], submenu)
            action.setObjectName(f"menu_language_{locale}")
            action.setData(locale)
            action.setCheckable(True)
            action.setChecked(locale == current_locale())
            action.setToolTip(translate("settings.language_accessible"))
            action.triggered.connect(lambda _checked=False, code=locale: self._select_locale(code))
            group.addAction(action)
            submenu.addAction(action)
            self._language_actions[locale] = action

    def _sync_language_actions(self) -> None:
        active = current_locale()
        for locale, action in getattr(self, "_language_actions", {}).items():
            action.blockSignals(True)
            action.setChecked(locale == active)
            action.setToolTip(translate("settings.language_accessible"))
            action.blockSignals(False)

    def _select_locale(self, locale: str) -> None:
        """Switch the live interface, then try to remember the choice.

        A failed write must leave the operator in the language they just chose:
        the selection is applied first, and only the persistence is reported as
        having failed.
        """
        if not set_locale(locale):
            self._sync_language_actions()
            return
        self.retranslate()
        try:
            self._ui_settings.save_locale(current_locale())
        except OSError as error:
            logger().warning("Could not persist the interface language: %s", error)
            self.session_note.show_key(
                "settings.locale_save_failed", "warning", message=str(error)
            )
            QMessageBox.warning(
                self,
                translate("menu.language").replace("&", ""),
                translate("settings.locale_save_failed").format(message=str(error)),
            )
