"""Acceptance coverage for the compact graph controls and unmistakable
signal-state slice (item_055, item_056, req_016).

Removed zoom/grid/window controls, an enlarged and still-accessible fit
glyph, Follow live sharing the fit row, durable simultaneous A/B cursor
timestamps, a high-contrast combo drop-down affordance, and a decisively
distinct bright-yellow selected favorite.
"""

from __future__ import annotations

from collections import Counter

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QComboBox

from peaklive.adapters import FakeCanAdapter
from peaklive.domain import CanFrame
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow, theme
from peaklive.ui.main_window import SIGNAL_KEY_ROLE
from peaklive.ui.panels.graph_controls import GraphControlsBar
from peaklive.ui.panels.signal_explorer import FAVORITE_COLUMN, SHOWN_COLUMN

VEHICLE_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 291 VehicleStatus: 8 ECU
 SG_ Speed : 0|16@1+ (0.1,0) [0|250] "km/h" ECU
'''


def _with_dbc(qtbot, tmp_path, **kwargs) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window.resize(*kwargs.pop("size", (1280, 720)))
    window.show()
    qtbot.waitExposed(window)
    path = tmp_path / "vehicle.dbc"
    path.write_text(VEHICLE_DBC, encoding="utf-8")
    window._load_dbc_path(path)
    return window


def _speed_frame(timestamp: float, raw_speed: int) -> CanFrame:
    payload = raw_speed.to_bytes(2, "little") + b"\x00" * 6
    return CanFrame(timestamp, 291, payload)


def _signal_item(window: MainWindow, key: str):
    for item in window.signal_explorer.findItems(
        "", Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive, 0
    ):
        if item.data(0, SIGNAL_KEY_ROLE) == key:
            return item
    raise AssertionError(f"Signal item not found: {key}")


def _pixel_counts(widget) -> Counter:
    image = widget.grab().toImage()
    counts: Counter[str] = Counter()
    for y in range(image.height()):
        for x in range(image.width()):
            counts[image.pixelColor(x, y).name()] += 1
    return counts


# --------------------------------------------------------------------------
# item_055 AC2/AC4 - removed controls, retained/enlarged fit glyphs
# --------------------------------------------------------------------------


def test_zoom_grid_and_window_readout_controls_no_longer_exist(qtbot):
    bar = GraphControlsBar()
    qtbot.addWidget(bar)
    for removed in ("zoom_in_button", "zoom_out_button", "grid_checkbox", "window_label"):
        assert not hasattr(bar, removed)


def test_no_control_exposes_a_removed_objects_name(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    for object_name in ("zoomInButton", "zoomOutButton", "gridCheckbox", "windowReadout"):
        assert window.findChild(type(window), object_name) is None


def test_the_fit_glyphs_are_marked_for_the_enlarged_treatment(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    bar = window.graph_panel.controls

    assert 'QToolButton[fitGlyph="true"]' in theme.APP_STYLE
    for fit_button in (bar.fit_button, bar.fit_y_button):
        # The pixel/point size QFontInfo reports for a stylesheet-driven font
        # is not portable across platforms (Windows CI has reported -1 for
        # both sides of this comparison) - the `fitGlyph` property, which the
        # theme's QSS keys its larger font-size rule off, is the reliable,
        # platform-independent signal that the enlargement is applied.
        assert fit_button.property("fitGlyph") is True
        assert fit_button.accessibleName()
        assert fit_button.toolTip()
        assert fit_button.focusPolicy() != Qt.FocusPolicy.NoFocus
    assert bar.cursor_a_button.property("fitGlyph") is not True


def test_follow_live_shares_the_fit_commands_row(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    header = window.workspace_header
    controls = [
        header.row.itemAt(index).widget()
        for index in range(header.row.count())
        if header.row.itemAt(index).widget() is not None
    ]

    assert window.graph_panel.fit_button in controls
    assert window.graph_panel.fit_y_button in controls
    assert window.graph_panel.follow_checkbox in controls


def test_removed_controls_do_not_regress_navigation_or_follow_live(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    panel = window.graph_panel
    window._render_frames([_speed_frame(float(i), 100 * i) for i in range(5)])

    panel.zoom(0.5)
    assert not panel.follow_live

    panel.follow_checkbox.setChecked(True)
    assert panel.follow_live


# --------------------------------------------------------------------------
# item_055 AC3 - durable, simultaneous A/B cursor timestamps
# --------------------------------------------------------------------------


@pytest.mark.parametrize("size", [(1024, 768), (1280, 720), (1600, 900)])
def test_both_complete_cursor_timestamps_render_together_without_eliding(qtbot, tmp_path, size):
    window = _with_dbc(qtbot, tmp_path, size=size)
    window._render_frames([_speed_frame(float(i), 100 * i) for i in range(5)])
    window.graph_panel.place_cursor("a", 1078.077)
    window.graph_panel.place_cursor("b", 84.387)
    qtbot.wait(20)

    summary = window.graph_panel.cursor_summary
    assert summary.isVisible()
    assert "1078.077" in summary.text()
    assert "84.387" in summary.text()
    assert summary.width() >= summary.fontMetrics().horizontalAdvance(summary.text())


def test_the_graph_header_shows_no_window_or_no_sample_text(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    header_texts = [
        child.text()
        for child in window.workspace_header.findChildren(object)
        if hasattr(child, "text") and callable(child.text)
    ]
    assert not any("No sample yet" in text for text in header_texts)
    assert not any("×)" in text for text in header_texts)  # the old "(1.0×)" zoom readout


# --------------------------------------------------------------------------
# item_056 AC1 - unmistakable combo drop-down affordance
# --------------------------------------------------------------------------


def test_the_combo_drop_down_is_not_an_unexplained_white_rectangle(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    combos = [combo for combo in window.findChildren(QComboBox) if combo.isVisible()]
    assert combos
    for combo in combos:
        counts = _pixel_counts(combo)
        near_white = sum(
            count for name, count in counts.items() if QColor(name).lightness() >= 250
        )
        total = sum(counts.values())
        assert near_white / total < 0.05, combo.objectName()


# --------------------------------------------------------------------------
# item_056 AC5/AC6 - decisive favorite yellow, stronger eye/star distinction
# --------------------------------------------------------------------------


def test_the_selected_favorite_star_is_a_decisive_bright_yellow(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    item = _signal_item(window, "VehicleStatus.Speed")
    tree = window.signal_explorer

    item.setCheckState(FAVORITE_COLUMN, Qt.CheckState.Checked)
    tree.viewport().repaint()
    rect = tree.visualRect(tree.indexFromItem(item, FAVORITE_COLUMN))
    counts = Counter()
    image = tree.viewport().grab(rect).toImage()
    for y in range(image.height()):
        for x in range(image.width()):
            counts[image.pixelColor(x, y).name()] += 1

    assert QColor(theme.ROW_ACTION_FAVORITE_ACTIVE).name() in counts
    assert QColor(theme.ROW_ACTION_ACTIVE).name() not in counts


def test_an_unselected_favorite_keeps_the_pre_existing_muted_treatment(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    item = _signal_item(window, "VehicleStatus.Speed")
    tree = window.signal_explorer

    item.setCheckState(FAVORITE_COLUMN, Qt.CheckState.Unchecked)
    tree.viewport().repaint()
    rect = tree.visualRect(tree.indexFromItem(item, FAVORITE_COLUMN))
    counts = Counter()
    image = tree.viewport().grab(rect).toImage()
    for y in range(image.height()):
        for x in range(image.width()):
            counts[image.pixelColor(x, y).name()] += 1

    assert QColor(theme.ROW_ACTION_MUTED).name() in counts
    assert QColor(theme.ROW_ACTION_FAVORITE_ACTIVE).name() not in counts


def test_favorite_and_shown_active_colours_are_a_different_hue_not_a_shade():
    favorite = QColor(theme.ROW_ACTION_FAVORITE_ACTIVE)
    shown = QColor(theme.ROW_ACTION_ACTIVE)

    # Yellow is red+green dominant with a low blue channel; the shown cyan is
    # the opposite - blue/green dominant with a low red channel. Comparing
    # channel dominance (rather than just brightness) is what proves this is
    # a distinct colour family, not a brighter cyan (item_056 AC5).
    assert favorite.red() > shown.red()
    assert favorite.blue() < shown.blue()


def test_favorite_and_eye_actions_keep_their_tooltip(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    item = _signal_item(window, "VehicleStatus.Speed")

    for column in (SHOWN_COLUMN, FAVORITE_COLUMN):
        assert item.toolTip(column)
