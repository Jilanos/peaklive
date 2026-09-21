"""Make Qt's own dialog chrome follow the application language.

Standard button captions and file-dialog chrome are Qt's strings, not the
application's, so translating the catalog alone would leave a French workspace
with English OK/Cancel buttons. Qt ships the catalogs for them; they simply have
to be installed, and swapped when the operator chooses another language.
"""

from __future__ import annotations

from PySide6.QtCore import QCoreApplication, QLibraryInfo, QTranslator

from peaklive.i18n import SOURCE_LOCALE

_installed: QTranslator | None = None


def qt_translations_path() -> str:
    return QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)


def apply_qt_translations(locale: str) -> bool:
    """Install Qt's catalog for `locale`; returns whether one is now active.

    The source locale needs no catalog — Qt's built-in strings are already
    English — and a missing catalog is a degraded deployment, not a failure:
    the application's own text stays translated either way.
    """
    global _installed
    app = QCoreApplication.instance()
    if app is None:
        return False
    if _installed is not None:
        app.removeTranslator(_installed)
        _installed = None
    if locale == SOURCE_LOCALE:
        return False
    translator = QTranslator()
    if not translator.load(f"qtbase_{locale}", qt_translations_path()):
        return False
    app.installTranslator(translator)
    _installed = translator
    return True
