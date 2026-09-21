"""What the Windows bundle has to carry for the French build to be usable."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QCoreApplication

from peaklive.i18n import SOURCE_LOCALE, SUPPORTED_LOCALES, catalog_path
from peaklive.ui.qt_translations import apply_qt_translations, qt_translations_path

ROOT = Path(__file__).parents[1]
SPEC = ROOT / "peaklive.spec"


def test_every_supported_catalog_is_package_data_the_spec_collects():
    spec = SPEC.read_text(encoding="utf-8")

    assert 'includes=["i18n/*.json", "resources/*"]' in spec
    for locale in SUPPORTED_LOCALES:
        path = catalog_path(locale)
        assert path.exists(), locale
        # Collected by the glob above only if it sits in the package directory.
        assert path.parent.name == "i18n"
        assert path.suffix == ".json"


def test_the_spec_bundles_the_qt_catalogs_the_translated_dialogs_need():
    spec = SPEC.read_text(encoding="utf-8")

    assert "qtbase_" in spec
    assert "PySide6/Qt/translations" in spec
    for locale in SUPPORTED_LOCALES:
        if locale == SOURCE_LOCALE:
            continue
        assert (Path(qt_translations_path()) / f"qtbase_{locale}.qm").exists(), locale


def test_qt_dialog_chrome_follows_the_application_language(qtbot):
    del qtbot  # The fixture is only here to guarantee a QApplication exists.
    assert QCoreApplication.instance() is not None

    assert apply_qt_translations("fr") is True
    translated = QCoreApplication.translate("QPlatformTheme", "Cancel")
    assert apply_qt_translations(SOURCE_LOCALE) is False
    english = QCoreApplication.translate("QPlatformTheme", "Cancel")

    assert english == "Cancel"
    assert translated == "Annuler"


def test_an_absent_qt_catalog_leaves_the_application_usable(qtbot):
    del qtbot

    # A locale Qt has no catalog for is a degraded deployment, not a crash:
    # PeakLive's own text still translates, only Qt's chrome stays English.
    assert apply_qt_translations("zz") is False
    assert QCoreApplication.translate("QPlatformTheme", "Cancel") == "Cancel"
