"""Structural guards for the decomposed UI layer (item_025).

These do not exercise behavior; they pin the shape the decomposition produced so
the next UX wave cannot quietly rebuild the monolith or bypass the i18n layer.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from peaklive.i18n import translate

UI_ROOT = Path(__file__).resolve().parents[1] / "src" / "peaklive" / "ui"

#: Stated line budget per UI module. The pre-decomposition main window was 863
#: lines and held every panel; nothing in this layer may grow back to that.
MODULE_LINE_BUDGET = 400

TRANSLATE_CALL = re.compile(r'translate\(\s*"([a-z0-9_.]+)"\s*\)')

#: Literals that are not user-facing prose: glyphs, enum values, and units the
#: catalog would only obscure.
ALLOWED_LITERALS = {"RX", "EVENT", "+", "−", "▲", "▼", "⤢", "A", "B", "—", ""}

LABEL_CALL = re.compile(
    r'(?:setText|setToolTip|setAccessibleName|setPlaceholderText|setWindowTitle)'
    r'\(\s*"([^"]*)"'
)


def _ui_modules() -> list[Path]:
    return sorted(path for path in UI_ROOT.rglob("*.py") if path.name != "__init__.py")


def test_every_ui_module_stays_within_the_stated_line_budget():
    oversized = {
        path.relative_to(UI_ROOT).as_posix(): len(path.read_text(encoding="utf-8").splitlines())
        for path in _ui_modules()
        if len(path.read_text(encoding="utf-8").splitlines()) > MODULE_LINE_BUDGET
    }

    assert oversized == {}


#: The shell is the main window plus the composition mixins it delegates to.
#: The guard is about what this layer may build, not about which file holds it.
SHELL_MODULES = ("main_window.py", "workspace_center.py")


def test_the_main_window_composes_panels_rather_than_building_them():
    source = "\n".join(
        (UI_ROOT / name).read_text(encoding="utf-8") for name in SHELL_MODULES
    )

    # The shell must not construct panel internals itself.
    for widget in ("QTreeWidget(", "QTableWidget(", "QLineEdit(", "pg.PlotWidget("):
        assert widget not in source

    for panel in (
        "AcquisitionBar",
        "DbcLibraryPanel",
        "GraphStackPanel",
        "InspectorPanel",
        "ReportPanel",
        "SignalExplorerPanel",
        "TraceViewPanel",
    ):
        assert panel in source


def test_the_stylesheet_lives_in_the_token_module_only():
    theme = (UI_ROOT / "theme.py").read_text(encoding="utf-8")
    assert "QFrame#instrument" in theme

    for path in _ui_modules():
        if path.name == "theme.py":
            continue
        source = path.read_text(encoding="utf-8")
        assert "QMainWindow {" not in source
        assert "border-radius" not in source


@pytest.mark.parametrize("path", _ui_modules(), ids=lambda path: path.name)
def test_every_translate_key_used_by_the_ui_resolves(path: Path):
    keys = TRANSLATE_CALL.findall(path.read_text(encoding="utf-8"))

    unresolved = []
    for key in keys:
        try:
            translate(key)
        except KeyError:
            unresolved.append(key)

    assert unresolved == []


@pytest.mark.parametrize("path", _ui_modules(), ids=lambda path: path.name)
def test_no_user_visible_label_bypasses_the_i18n_catalog(path: Path):
    literals = [
        literal
        for literal in LABEL_CALL.findall(path.read_text(encoding="utf-8"))
        if literal not in ALLOWED_LITERALS
    ]

    assert literals == []


def test_the_catalog_covers_every_key_the_ui_asks_for():
    used = {
        key
        for path in _ui_modules()
        for key in TRANSLATE_CALL.findall(path.read_text(encoding="utf-8"))
    }

    assert len(used) > 60
    assert all(translate(key) for key in used)
