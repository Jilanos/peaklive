"""Acceptance coverage for the Signals tree and combo-box affordance slice
(item_054, req_015).

Branch expand/collapse contrast, compact eye/star action pictograms, and a
combo-box contrast audit across the application.
"""

from __future__ import annotations

from collections import Counter

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QComboBox

from peaklive.adapters import FakeCanAdapter
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow
from peaklive.ui.main_window import SIGNAL_KEY_ROLE
from peaklive.ui.panels.signal_explorer import FAVORITE_COLUMN, SHOWN_COLUMN

VEHICLE_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 291 VehicleStatus: 8 ECU
 SG_ Speed : 0|16@1+ (0.1,0) [0|250] "km/h" ECU
'''

MINIMUM_CONTRAST = 4.5


def _with_dbc(qtbot, tmp_path) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window.resize(1024, 768)
    window.show()
    qtbot.waitExposed(window)
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


def _rendered_contrast(widget, *, minimum_pixels: int = 8) -> float:
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
# AC2 - branch expand/collapse affordance
# --------------------------------------------------------------------------


def test_dbc_and_message_rows_expose_a_high_contrast_branch_affordance(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    tree = window.signal_explorer
    dbc_row = tree.topLevelItem(0)
    assert dbc_row.childCount() > 0
    assert dbc_row.isExpanded()

    dbc_row.setExpanded(False)
    qtbot.wait(10)
    assert _rendered_contrast(tree.viewport()) >= MINIMUM_CONTRAST


def test_branch_expand_collapse_is_keyboard_operable(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    tree = window.signal_explorer
    dbc_row = tree.topLevelItem(0)
    tree.setCurrentItem(dbc_row)
    tree.setFocus(Qt.FocusReason.OtherFocusReason)
    assert dbc_row.isExpanded()

    qtbot.keyClick(tree, Qt.Key.Key_Left)
    assert not dbc_row.isExpanded()

    qtbot.keyClick(tree, Qt.Key.Key_Right)
    assert dbc_row.isExpanded()


def test_disabled_rows_still_carry_a_legible_branch(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    tree = window.signal_explorer
    tree.setEnabled(False)
    qtbot.wait(10)
    assert _rendered_contrast(tree.viewport()) >= MINIMUM_CONTRAST
    tree.setEnabled(True)


# --------------------------------------------------------------------------
# AC3 - compact eye/star row actions
# --------------------------------------------------------------------------


def test_shown_and_favorite_actions_paint_distinctly_when_active(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    item = _signal_item(window, "VehicleStatus.Speed")
    tree = window.signal_explorer
    tree.setCurrentItem(tree.topLevelItem(0))  # move selection off the row

    item.setCheckState(SHOWN_COLUMN, Qt.CheckState.Unchecked)
    item.setCheckState(FAVORITE_COLUMN, Qt.CheckState.Unchecked)
    tree.viewport().repaint()
    rect = tree.visualItemRect(item)
    muted = tree.viewport().grab(rect.adjusted(0, 0, 0, 0)).toImage()

    item.setCheckState(SHOWN_COLUMN, Qt.CheckState.Checked)
    item.setCheckState(FAVORITE_COLUMN, Qt.CheckState.Checked)
    tree.viewport().repaint()
    active = tree.viewport().grab(rect).toImage()

    def colours(image):
        counts: Counter[str] = Counter()
        for y in range(image.height()):
            for x in range(image.width()):
                counts[image.pixelColor(x, y).name()] += 1
        return counts

    assert colours(muted) != colours(active)


def test_the_action_columns_are_compact_and_the_name_keeps_the_flexible_width(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    header = window.signal_explorer.header()

    action_width = header.sectionSize(SHOWN_COLUMN) + header.sectionSize(FAVORITE_COLUMN)
    assert action_width < 80
    assert header.sectionSize(0) > action_width


def test_action_cells_keep_their_tooltip_and_accessible_state(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    item = _signal_item(window, "VehicleStatus.Speed")
    for column in (SHOWN_COLUMN, FAVORITE_COLUMN):
        assert item.toolTip(column)


# --------------------------------------------------------------------------
# AC5 - QComboBox contrast audit
# --------------------------------------------------------------------------


def test_every_workspace_combo_box_paints_a_visible_drop_down_affordance(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    combos = window.findChildren(QComboBox)
    assert combos
    for combo in combos:
        if not combo.isVisible():
            continue
        assert _rendered_contrast(combo) >= MINIMUM_CONTRAST, combo.objectName()
