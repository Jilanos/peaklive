"""Acceptance coverage for the workspace visual-usability wave (req_003).

Three slices share this suite: the name-first signal explorer (item_026), the
dark-theme control contract (item_027), and collapsed-panel space reclamation
with the regrouped graph workspace (item_028). Everything runs headless under
the offscreen platform with fake adapters.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QCheckBox, QComboBox, QHeaderView, QWidget

from peaklive.adapters import FakeCanAdapter
from peaklive.i18n import translate
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow, theme
from peaklive.ui.main_window import SIGNAL_KEY_ROLE
from peaklive.ui.panels.signal_explorer import (
    ACCESSIBLE_ROLE,
    ACTION_COLUMN_WIDTH,
    FAVORITE_COLUMN,
    SHOWN_COLUMN,
)

UI_ROOT = Path(__file__).resolve().parents[1] / "src" / "peaklive" / "ui"

VEHICLE_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 291 VehicleStatus: 8 ECU
 SG_ Speed : 0|16@1+ (0.1,0) [0|250] "km/h" ECU
 SG_ Rpm : 16|16@1+ (1,0) [0|8000] "rpm" ECU
'''

#: WCAG AA for normal text. The instrument theme has no reason to sit below it.
MINIMUM_CONTRAST = 4.5


def _window(qtbot, tmp_path, *, show: bool = True, size=(1280, 720)) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    if show:
        window.resize(*size)
        window.show()
        qtbot.waitExposed(window)
    return window


def _with_dbc(qtbot, tmp_path, **kwargs) -> MainWindow:
    window = _window(qtbot, tmp_path, **kwargs)
    path = tmp_path / "vehicle.dbc"
    path.write_text(VEHICLE_DBC, encoding="utf-8")
    window._load_dbc_path(path)
    return window


def _signal_item(window: MainWindow, key: str):
    for item in window.signal_explorer.findItems(
        "", Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive, 0
    ):
        if item.data(0, SIGNAL_KEY_ROLE) == key:
            return item
    raise AssertionError(f"Signal item not found: {key}")


def _relative_luminance(color: QColor) -> float:
    def channel(value: int) -> float:
        srgb = value / 255.0
        return srgb / 12.92 if srgb <= 0.03928 else ((srgb + 0.055) / 1.055) ** 2.4

    return (
        0.2126 * channel(color.red())
        + 0.7152 * channel(color.green())
        + 0.0722 * channel(color.blue())
    )


def _contrast(first: QColor, second: QColor) -> float:
    lighter = max(_relative_luminance(first), _relative_luminance(second))
    darker = min(_relative_luminance(first), _relative_luminance(second))
    return (lighter + 0.05) / (darker + 0.05)


def _rendered_contrast(widget: QWidget, *, minimum_pixels: int = 8) -> float:
    """Contrast between what a widget paints most and its most distinct ink.

    Reading the rendered pixels rather than the stylesheet text is the point:
    a rule that Qt never applies leaves the control dark on dark, and only the
    painted result shows that.
    """
    image = widget.grab().toImage()
    counts: Counter[str] = Counter()
    for y in range(image.height()):
        for x in range(image.width()):
            counts[image.pixelColor(x, y).name()] += 1
    assert counts, "widget painted nothing"
    background = QColor(counts.most_common(1)[0][0])
    candidates = [QColor(name) for name, count in counts.items() if count >= minimum_pixels]
    return max(_contrast(background, candidate) for candidate in candidates)


# --------------------------------------------------------------------------
# item_026 - compact, name-first, state-legible signal selection
# --------------------------------------------------------------------------


def test_signal_rows_no_longer_repeat_the_action_words(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)

    item = _signal_item(window, "VehicleStatus.Speed")

    assert item.text(0).startswith("Speed")
    assert item.text(SHOWN_COLUMN) == ""
    assert item.text(FAVORITE_COLUMN) == ""


def test_the_signal_name_column_keeps_the_flexible_width(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    header = window.signal_explorer.header()

    assert header.sectionResizeMode(0) == QHeaderView.ResizeMode.Stretch
    assert header.sectionResizeMode(SHOWN_COLUMN) == QHeaderView.ResizeMode.Fixed
    assert header.sectionResizeMode(FAVORITE_COLUMN) == QHeaderView.ResizeMode.Fixed
    assert not header.stretchLastSection()

    action_width = header.sectionSize(SHOWN_COLUMN) + header.sectionSize(FAVORITE_COLUMN)
    assert action_width <= 2 * ACTION_COLUMN_WIDTH
    assert header.sectionSize(0) > action_width


def test_the_headers_still_name_the_two_actions(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    header = window.signal_explorer.headerItem()

    assert header.text(0) == translate("signals.column_signal")
    assert header.text(SHOWN_COLUMN) == translate("signals.column_shown")
    assert header.text(FAVORITE_COLUMN) == translate("signals.column_favorite")


def test_shown_and_favorite_toggle_independently(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    item = _signal_item(window, "VehicleStatus.Speed")

    item.setCheckState(SHOWN_COLUMN, Qt.CheckState.Checked)
    assert "VehicleStatus.Speed" in window._selected_signal_names
    assert "VehicleStatus.Speed" not in window._favorite_signal_names

    item.setCheckState(FAVORITE_COLUMN, Qt.CheckState.Checked)
    item.setCheckState(SHOWN_COLUMN, Qt.CheckState.Unchecked)
    assert "VehicleStatus.Speed" not in window._selected_signal_names
    assert "VehicleStatus.Speed" in window._favorite_signal_names


def test_a_toggle_emits_exactly_one_change(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    item = _signal_item(window, "VehicleStatus.Speed")
    seen: list[tuple[str, bool]] = []
    window.explorer_panel.shown_changed.connect(lambda key, state: seen.append((key, state)))

    item.setCheckState(SHOWN_COLUMN, Qt.CheckState.Checked)

    assert seen == [("VehicleStatus.Speed", True)]


def test_the_keyboard_toggles_the_focused_action_cell(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    tree = window.signal_explorer
    item = _signal_item(window, "VehicleStatus.Speed")
    tree.setCurrentItem(item, SHOWN_COLUMN)
    tree.setFocus(Qt.FocusReason.OtherFocusReason)

    qtbot.keyClick(tree, Qt.Key.Key_Space)

    assert item.checkState(SHOWN_COLUMN) == Qt.CheckState.Checked
    assert "VehicleStatus.Speed" in window._selected_signal_names


def test_activation_still_toggles_the_shown_state(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    item = _signal_item(window, "VehicleStatus.Speed")

    window.explorer_panel._item_activated(item)

    assert item.checkState(SHOWN_COLUMN) == Qt.CheckState.Checked


def test_each_action_cell_states_its_action_and_its_state(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    item = _signal_item(window, "VehicleStatus.Speed")

    for column in (SHOWN_COLUMN, FAVORITE_COLUMN):
        label = item.data(column, ACCESSIBLE_ROLE)
        assert label == item.toolTip(column)
        assert "VehicleStatus.Speed" in label
        assert translate("signals.state_off") in label

    item.setCheckState(SHOWN_COLUMN, Qt.CheckState.Checked)
    assert translate("signals.state_on") in item.data(SHOWN_COLUMN, ACCESSIBLE_ROLE)
    assert translate("signals.state_off") in item.data(FAVORITE_COLUMN, ACCESSIBLE_ROLE)


def test_dbc_enablement_stays_in_the_library_and_is_not_duplicated(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)

    library_row = window.dbc_library.topLevelItem(0)
    assert library_row.checkState(0) == Qt.CheckState.Checked

    assert window.signal_explorer.columnCount() == 3
    dbc_row = window.signal_explorer.topLevelItem(0)
    for column in range(window.signal_explorer.columnCount()):
        assert dbc_row.checkState(column) == Qt.CheckState.Unchecked
        assert not dbc_row.data(column, SIGNAL_KEY_ROLE)


def test_search_and_the_two_filters_keep_working(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    # Loading a DBC shows its first signal so the workspace is never blank;
    # this slice is about the filters, so start from a single known selection.
    for item in _signal_rows(window):
        item.setCheckState(SHOWN_COLUMN, Qt.CheckState.Unchecked)
    _signal_item(window, "VehicleStatus.Speed").setCheckState(
        SHOWN_COLUMN, Qt.CheckState.Checked
    )

    window.signal_filter.setText("rpm")
    assert [item.text(0) for item in _signal_rows(window)] == ["Rpm [rpm]"]

    window.signal_filter.clear()
    window.shown_only_checkbox.setChecked(True)
    assert [item.text(0) for item in _signal_rows(window)] == ["Speed [km/h]"]

    window.shown_only_checkbox.setChecked(False)
    window.favorites_only_checkbox.setChecked(True)
    assert _signal_rows(window) == []


def _signal_rows(window: MainWindow) -> list:
    return [
        item
        for item in window.signal_explorer.findItems(
            "", Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive, 0
        )
        if item.data(0, SIGNAL_KEY_ROLE)
    ]


def test_shown_and_favorite_selections_survive_a_restart(qtbot, tmp_path):
    store = ProfileStore(tmp_path / "settings")
    dbc = tmp_path / "vehicle.dbc"
    dbc.write_text(VEHICLE_DBC, encoding="utf-8")

    window = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window._load_dbc_path(dbc)
    item = _signal_item(window, "VehicleStatus.Speed")
    item.setCheckState(SHOWN_COLUMN, Qt.CheckState.Checked)
    item.setCheckState(FAVORITE_COLUMN, Qt.CheckState.Checked)

    restored = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(restored)

    restored_item = _signal_item(restored, "VehicleStatus.Speed")
    assert restored_item.checkState(SHOWN_COLUMN) == Qt.CheckState.Checked
    assert restored_item.checkState(FAVORITE_COLUMN) == Qt.CheckState.Checked


# --------------------------------------------------------------------------
# item_027 - dark-theme control and menu legibility
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "selector",
    [
        "QComboBox QAbstractItemView::item",
        "QComboBox QAbstractItemView::item:selected",
        "QComboBox QAbstractItemView::item:disabled",
        "QAbstractItemView::item:hover",
        "QAbstractItemView::item:selected",
        "QMenu::item",
        "QMenu::item:selected",
        "QMenu::item:disabled",
        "QCheckBox::indicator:unchecked",
        "QCheckBox::indicator:checked",
        "QCheckBox::indicator:disabled",
        "QPushButton:focus",
    ],
)
def test_the_control_contract_names_every_state(selector):
    assert selector in theme.CONTROL_STYLE


@pytest.mark.parametrize(
    ("foreground", "background"),
    [
        (theme.TEXT, theme.POPUP_SURFACE),
        (theme.TEXT, theme.CONTROL_SURFACE),
        (theme.TEXT_BODY, theme.SURFACE),
        (theme.SELECTION_TEXT, theme.SELECTION_BACKGROUND),
        (theme.DISABLED_TEXT, theme.DISABLED_BACKGROUND),
        (theme.INDICATOR_BORDER, theme.SURFACE),
        (theme.INDICATOR_CHECKED, theme.SURFACE),
    ],
)
def test_every_declared_pair_clears_the_contrast_floor(foreground, background):
    assert _contrast(QColor(foreground), QColor(background)) >= MINIMUM_CONTRAST


def test_focus_is_marked_by_outline_width_not_only_by_colour():
    assert theme.FOCUS_RING_WIDTH != "1px"
    assert f"border: {theme.FOCUS_RING_WIDTH} solid {theme.FOCUS_RING}" in theme.CONTROL_STYLE


def test_no_ui_module_outside_the_theme_declares_its_own_colour():
    literals = {
        path.relative_to(UI_ROOT).as_posix(): re.findall(
            r'"#[0-9a-fA-F]{3,8}"', path.read_text(encoding="utf-8")
        )
        for path in UI_ROOT.rglob("*.py")
        if path.name != "theme.py"
    }

    assert {name: found for name, found in literals.items() if found} == {}


def test_an_expanded_combo_popup_paints_readable_text(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    combo = window.workspace_mode_selector
    combo.showPopup()
    qtbot.wait(10)

    assert _rendered_contrast(combo.view()) >= MINIMUM_CONTRAST
    assert _rendered_contrast(combo) >= MINIMUM_CONTRAST


def test_every_workspace_combo_paints_readable_text_when_closed(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    combos = window.findChildren(QComboBox)
    assert combos
    for combo in combos:
        if not combo.isVisible():
            continue
        assert _rendered_contrast(combo) >= MINIMUM_CONTRAST, combo.objectName()


def test_an_expanded_menu_paints_readable_text(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    for action in window.menuBar().actions():
        menu = action.menu()
        menu.popup(window.mapToGlobal(window.rect().center()))
        qtbot.wait(10)
        assert _rendered_contrast(menu) >= MINIMUM_CONTRAST, action.text()
        menu.close()


def test_checked_and_unchecked_boxes_are_visibly_distinct(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    boxes = [box for box in window.findChildren(QCheckBox) if box.isVisible()]
    assert boxes
    for box in boxes:
        was_checked = box.isChecked()
        box.setChecked(False)
        unchecked = box.grab().toImage()
        box.setChecked(True)
        checked = box.grab().toImage()
        box.setChecked(was_checked)
        assert unchecked != checked, box.objectName()
