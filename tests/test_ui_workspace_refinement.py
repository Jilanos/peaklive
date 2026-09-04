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
from PySide6.QtWidgets import QCheckBox, QComboBox, QHeaderView, QLabel, QScrollArea, QWidget

from peaklive.adapters import FakeCanAdapter
from peaklive.i18n import translate
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow, theme
from peaklive.ui.flow_layout import FlowLayout
from peaklive.ui.layout_reflow import (
    GRAPH_MINIMUM_HEIGHT,
    MIN_CENTER_WIDTH,
    MIN_SIDE_WIDTH,
    SECTION_MINIMUM_HEIGHT,
    reflow_widths,
)
from peaklive.ui.main_window import SIGNAL_KEY_ROLE
from peaklive.ui.panels.graph_controls import (
    READOUT_MINIMUM_WIDTH,
    READOUT_PREFERRED_WIDTH,
    ElidingLabel,
    GraphControlsBar,
)
from peaklive.ui.panels.graph_stack import PLOT_AREA_MINIMUM_HEIGHT, SHARED_LEFT_AXIS_WIDTH
from peaklive.ui.panels.signal_explorer import (
    ACCESSIBLE_ROLE,
    ACTION_COLUMN_WIDTH,
    FAVORITE_COLUMN,
    SHOWN_COLUMN,
)
from peaklive.ui.widgets import RAIL_WIDTH

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


def _speed_frame(timestamp: float, raw_speed: int):
    from peaklive.domain import CanFrame

    payload = raw_speed.to_bytes(2, "little") + b"\x00" * 6
    return CanFrame(timestamp, 291, payload)


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

    # Profile DBC restoration prepares its catalog on the operation queue;
    # assertions must wait for that atomic async commit rather than assuming
    # parsing completed during widget construction.
    qtbot.waitUntil(
        lambda: any(
            item.data(0, SIGNAL_KEY_ROLE) == "VehicleStatus.Speed"
            for item in restored.signal_explorer.findItems(
                "", Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive, 0
            )
        )
    )
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


# --------------------------------------------------------------------------
# item_028 - reclaimed panel space and a regrouped graph workspace
# --------------------------------------------------------------------------


def _about(actual: int, expected: int) -> bool:
    """Splitter widths land near, not exactly on, what a caller asks for.

    The centre column has a minimum of its own, so restoring a side panel
    returns the remembered width less whatever the centre still needs.
    """
    return abs(actual - expected) <= max(8, expected // 20)


def _rects(widgets):
    return [widget.geometry() for widget in widgets]


def _paints_its_content(control: QWidget) -> bool:
    """Is the control wide enough for what it has to draw?

    Not `minimumSizeHint()`: that carries the stylesheet's padding, which a
    layout is free to eat, and a glyph button squeezed out of its padding is
    still perfectly readable. A readout is exempt because it elides on
    purpose - it only has to keep its floor.
    """
    if isinstance(control, ElidingLabel):
        return control.width() >= READOUT_MINIMUM_WIDTH
    text = control.text() if hasattr(control, "text") else ""
    return control.width() >= control.fontMetrics().horizontalAdvance(text)


def _leaf_controls(bar) -> list[QWidget]:
    return [
        child
        for group in bar.groups
        for child in group.findChildren(QWidget)
        if child.isVisible()
    ]


def test_collapsing_a_side_panel_releases_its_column(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    before = window.workspace.sizes()

    window.signals_panel.set_collapsed(True)
    qtbot.wait(10)
    after = window.workspace.sizes()

    assert after[0] == RAIL_WIDTH
    assert window.signals_panel.width() == RAIL_WIDTH
    assert after[1] > before[1]
    assert sum(after) == sum(before)


def test_both_side_panels_can_be_collapsed_at_once(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    window.signals_panel.set_collapsed(True)
    window.inspector_panel.set_collapsed(True)
    qtbot.wait(10)

    sizes = window.workspace.sizes()
    assert sizes[0] == sizes[2] == RAIL_WIDTH
    assert sizes[1] == sum(sizes) - 2 * RAIL_WIDTH


def test_the_collapsed_rail_names_its_panel_and_offers_the_expand_control(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    window.inspector_panel.set_collapsed(True)
    qtbot.wait(10)

    panel = window.inspector_panel
    assert panel.rail.isVisible()
    assert panel.rail.text() == translate("workspace.inspector").upper()
    assert not window.inspector_body.isVisible()
    assert panel.toggle.isVisible()
    assert panel.toggle.text() == "+"
    expected = translate("panel.expand").format(panel=translate("workspace.inspector"))
    assert panel.toggle.accessibleName() == expected
    assert panel.toggle.toolTip() == expected


@pytest.mark.parametrize("panel_name", ["signals_panel", "inspector_panel"])
def test_the_collapsed_rail_centres_a_compact_unobstructed_expand_control(
    qtbot, tmp_path, panel_name
):
    window = _window(qtbot, tmp_path)
    panel = getattr(window, panel_name)
    panel.set_collapsed(True)
    qtbot.wait(10)

    button = panel.toggle
    assert button.width() < RAIL_WIDTH
    assert panel.rect().contains(button.geometry())
    assert abs(button.geometry().center().x() - panel.rect().center().x()) <= 1


def test_expanding_restores_the_remembered_width_and_the_content(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    window.workspace.setSizes([340, 700, 240])
    window._persist_layout()
    window.signal_filter.setText("speed")
    qtbot.wait(10)
    remembered = window.workspace.sizes()[0]

    window.signals_panel.set_collapsed(True)
    qtbot.wait(10)
    window.signals_panel.set_collapsed(False)
    qtbot.wait(10)

    assert _about(window.workspace.sizes()[0], remembered)
    assert window.signals_body.isVisible()
    assert not window.signals_panel.rail.isVisible()
    assert window.signal_filter.text() == "speed"


def test_the_collapsed_state_and_remembered_width_persist_per_profile(qtbot, tmp_path):
    store = ProfileStore(tmp_path / "settings")
    window = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window.resize(1280, 720)
    window.show()
    qtbot.waitExposed(window)
    window.workspace.setSizes([340, 700, 240])
    window._persist_layout()
    window.inspector_panel.set_collapsed(True)
    qtbot.wait(10)

    stored = store.load().selected.layout
    assert stored.collapsed_panels == ["inspector"]
    assert stored.panel_widths["inspector"] > RAIL_WIDTH

    restored = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(restored)
    restored.resize(1280, 720)
    restored.show()
    qtbot.waitExposed(restored)

    assert restored.inspector_panel.is_collapsed
    assert restored.workspace.sizes()[2] == RAIL_WIDTH
    restored.inspector_panel.set_collapsed(False)
    qtbot.wait(10)
    assert _about(restored.workspace.sizes()[2], stored.panel_widths["inspector"])


def test_an_unusable_stored_width_falls_back_to_a_safe_default(qtbot, tmp_path):
    store = ProfileStore(tmp_path / "settings")
    state = store.load()
    state.selected.layout.panel_widths = {"signals": -40, "inspector": 0}
    state.selected.layout.collapsed_panels = ["signals"]
    store.save(state)

    assert store.load().selected.layout.panel_widths == {}

    window = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window.resize(1280, 720)
    window.show()
    qtbot.waitExposed(window)
    window.signals_panel.set_collapsed(False)
    qtbot.wait(10)

    assert window.workspace.sizes()[0] >= MIN_SIDE_WIDTH


@pytest.mark.parametrize(
    ("collapsed", "remembered", "total", "expected"),
    [
        ([False, False, False], [300, 0, 300], 1200, [300, 600, 300]),
        ([True, False, False], [300, 0, 300], 1200, [RAIL_WIDTH, 866, 300]),
        ([True, False, True], [300, 0, 300], 1200, [RAIL_WIDTH, 1132, RAIL_WIDTH]),
        ([False, True, False], [300, 0, 300], 1200, [583, RAIL_WIDTH, 583]),
        ([False, False, False], [0, 0, 0], 1200, [300, 600, 300]),
    ],
)
def test_the_width_split_is_arithmetic_not_guesswork(collapsed, remembered, total, expected):
    assert reflow_widths(collapsed, remembered, total) == expected


def test_the_centre_keeps_its_floor_when_the_window_is_narrow():
    widths = reflow_widths([False, False, False], [500, 0, 500], 1000)

    assert sum(widths) == 1000
    assert widths[1] >= MIN_CENTER_WIDTH


def test_the_keyboard_collapse_shortcut_reclaims_the_column(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    window._toggle_signals_panel()
    qtbot.wait(10)
    assert window.signals_panel.is_collapsed
    assert window.workspace.sizes()[0] == RAIL_WIDTH

    window._toggle_signals_panel()
    qtbot.wait(10)
    assert not window.signals_panel.is_collapsed
    assert window.workspace.sizes()[0] >= MIN_SIDE_WIDTH


def test_graph_controls_are_grouped_by_purpose(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    bar = window.graph_panel.controls

    assert [group.objectName() for group in bar.groups] == [
        "graphViewGroup",
        "graphCursorGroup",
    ]
    # These commands were reparented into the one-line Graphs/Trace header
    # (item_053 AC6) - GraphControlsBar still owns and wires them, it just no
    # longer displays them in its own row. cursor_summary stays behind in
    # GraphControlsBar's own row instead (item_055 AC3): the shared header has
    # too little width on every platform to hold both complete A/B timestamps
    # without eliding, while the dedicated row spans the full graph column.
    header = window.workspace_header
    for control in (
        bar.fit_button,
        bar.fit_y_button,
        bar.follow_checkbox,
        bar.cursor_a_button,
        bar.cursor_b_button,
        bar.measurement_visibility_button,
        bar.mode_selector,
        window.acquisition_bar.start_button,
        window.acquisition_bar.stop_button,
    ):
        assert control.parent() is header
    assert bar.cursor_summary.parent() is bar.cursor_group


@pytest.mark.parametrize("size", [(1024, 768), (1280, 720), (1600, 900)])
def test_the_graph_controls_stay_readable_at_the_bench_viewports(qtbot, tmp_path, size):
    window = _with_dbc(qtbot, tmp_path, size=size)
    qtbot.wait(20)
    bar = window.graph_panel.controls

    assert bar.isVisible()
    for group in bar.groups:
        assert group.isVisible()
        assert group.x() >= 0
        assert group.x() + group.width() <= bar.width() + 1


@pytest.mark.parametrize("size", [(1024, 768), (1280, 720), (1600, 900)])
def test_the_one_line_graphs_trace_header_stays_readable_at_the_bench_viewports(
    qtbot, tmp_path, size
):
    """item_053 AC6: title, view selection, fit, Follow live, Play/Stop, and
    cursor actions on one row, at every bench viewport, without wrapping,
    overlap, or clipping. item_055 AC3: both complete cursor timestamps stay
    visible together (in GraphControlsBar's own row) rather than falling back
    to a tooltip.
    """
    window = _with_dbc(qtbot, tmp_path, size=size)
    window._render_frames([_speed_frame(float(i), 100 * i) for i in range(5)])
    window.graph_panel.place_cursor("a", 1078.077)
    window.graph_panel.place_cursor("b", 84.387)
    qtbot.wait(20)
    header = window.workspace_header
    heading = window.trace_graph_panel.heading

    assert header.isVisible()
    assert heading.isVisible()
    assert heading.parentWidget() is header.parentWidget()

    controls = [
        header.row.itemAt(index).widget()
        for index in range(header.row.count())
        if header.row.itemAt(index).widget() is not None
    ]
    assert window.workspace_mode_selector in controls
    assert window.acquisition_bar.start_button in controls
    assert window.acquisition_bar.stop_button in controls
    assert window.graph_panel.fit_button in controls
    assert window.graph_panel.fit_y_button in controls
    assert window.graph_panel.follow_checkbox in controls
    assert window.graph_panel.cursor_a_button in controls
    assert window.graph_panel.cursor_b_button in controls

    visible = [control for control in controls if control.isVisible()]
    rects = _rects(visible)
    for first in range(len(rects)):
        for second in range(first + 1, len(rects)):
            assert not rects[first].intersects(rects[second]), (
                visible[first].objectName(),
                visible[second].objectName(),
            )
    for control in visible:
        left = control.mapTo(header, control.rect().topLeft()).x()
        right = control.mapTo(header, control.rect().topRight()).x()
        assert 0 <= left <= right <= header.width(), control.objectName()

    summary = window.graph_panel.cursor_summary
    assert summary.isVisible()
    assert "1078.077" in summary.text() and "84.387" in summary.text()
    assert summary.width() >= summary.fontMetrics().horizontalAdvance(summary.text())


@pytest.mark.parametrize("size", [(1024, 768), (1280, 720), (1600, 900)])
def test_the_graph_area_keeps_a_usable_height_at_the_bench_viewports(qtbot, tmp_path, size):
    window = _with_dbc(qtbot, tmp_path, size=size)
    qtbot.wait(20)

    assert window.graph_panel.height() >= GRAPH_MINIMUM_HEIGHT
    assert window.graph_panel.scroll.height() > 0
    assert window.graph_panel.height() > window.trace_panel.height()


def test_the_default_arrangement_gives_the_graph_area_priority(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    sizes = window.center_divider.sizes()
    assert sizes[0] > sizes[1]
    assert sizes[2] == 0
    assert window.graph_panel.minimumHeight() == GRAPH_MINIMUM_HEIGHT
    assert window.trace_panel.minimumHeight() == SECTION_MINIMUM_HEIGHT


def test_the_centre_sections_remain_resizable_and_persisted(qtbot, tmp_path):
    store = ProfileStore(tmp_path / "settings")
    window = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window.resize(1280, 720)
    window.show()
    qtbot.waitExposed(window)

    # The report is hidden in the default combo view, so the resizing that
    # matters here is between the graph area and the trace.
    before = window.center_divider.sizes()
    window.center_divider.setSizes([before[0] - 120, before[1] + 120, 0])
    window._persist_layout()
    adjusted = window.center_divider.sizes()
    assert adjusted != before
    assert adjusted[1] > before[1]

    restored = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(restored)
    restored.resize(1280, 720)
    restored.show()
    qtbot.waitExposed(restored)

    assert restored.center_divider.sizes() == adjusted


def test_the_collapsed_rail_actually_paints_its_title(qtbot, tmp_path):
    """A rotated label is easy to draw off its own widget; only pixels prove it."""
    window = _window(qtbot, tmp_path)
    window.signals_panel.set_collapsed(True)
    qtbot.wait(10)

    rail = window.signals_panel.rail
    image = rail.grab().toImage()
    counts: Counter[str] = Counter()
    for y in range(image.height()):
        for x in range(image.width()):
            counts[image.pixelColor(x, y).name()] += 1

    assert counts[theme.HEADING] > 20
    # The grab of a transparent label carries no panel background, so the
    # legibility check belongs on the tokens the rail actually sits on.
    assert _contrast(QColor(theme.HEADING), QColor(theme.SURFACE)) >= MINIMUM_CONTRAST


def test_the_plot_area_keeps_its_own_minimum_height(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path, size=(1024, 768))
    qtbot.wait(20)

    assert window.graph_panel.scroll.height() >= PLOT_AREA_MINIMUM_HEIGHT
    assert window.measure_table.height() <= window.graph_panel.scroll.height()


def test_multiple_signals_share_one_compact_non_scrolling_time_surface(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path, size=(1280, 720))
    window._selected_signal_names.update({"VehicleStatus.Speed", "VehicleStatus.Rpm"})
    window._sync_graphs()
    qtbot.wait(20)

    panel = window.graph_panel
    plots = list(panel.plots.values())
    assert len(plots) == 2
    assert panel.scroll.objectName() == "graphCanvas"
    assert not isinstance(panel.scroll, QScrollArea)
    assert panel.container_layout.spacing() == 0

    for plot in plots[:-1]:
        assert plot.getAxis("bottom").height() == 0
    assert plots[-1].getAxis("bottom").height() > 0
    assert all(
        plot.getViewBox().linkedView(0) is panel.anchor_plot.getViewBox() for plot in plots[1:]
    )


def test_a_long_readout_never_pushes_its_cluster_past_the_bar(qtbot, tmp_path):
    """Font metrics differ per platform; a readout must not size the cluster.

    Windows fonts made the cursor cluster 731 px wide inside a 601 px bar,
    which overflows rather than wraps. The readout now elides instead.
    """
    window = _with_dbc(qtbot, tmp_path, size=(1024, 768))
    bar = window.graph_panel.controls
    long_text = "A 1234.567s · B 9876.543s · Δ 8641.976s " * 4

    bar.cursor_summary.setText(long_text)
    qtbot.wait(20)

    for group in bar.groups:
        assert group.x() + group.width() <= bar.width() + 1
    # The value itself is not lost: it stays readable through the tooltip.
    assert bar.cursor_summary.text() == long_text
    assert bar.cursor_summary.toolTip() == long_text
    assert bar.cursor_summary.sizeHint().width() <= READOUT_PREFERRED_WIDTH


def test_the_flow_layout_compresses_an_item_wider_than_its_line(qtbot):
    container = QWidget()
    qtbot.addWidget(container)
    layout = FlowLayout(container, spacing=4)
    wide = QLabel("x" * 400)
    layout.addWidget(wide)
    container.resize(200, 60)
    container.show()
    qtbot.waitExposed(container)

    assert wide.width() <= container.width()


def test_graph_commands_stay_in_one_compact_toolbar_row(qtbot):
    """The command surface stays one row instead of turning into two headers."""
    bar = GraphControlsBar()
    qtbot.addWidget(bar)
    bar.setFixedWidth(560)
    bar.show()
    qtbot.waitExposed(bar)

    assert bar.layout().count() == 2
    for control in _leaf_controls(bar):
        assert control.parentWidget().mapTo(bar, control.pos()).y() >= 0
        assert _paints_its_content(control), control.objectName()


@pytest.mark.parametrize("mode", ("combo", "graphs", "trace", "report"))
def test_workspace_mode_selector_is_visible_and_fully_readable_in_every_mode(qtbot, tmp_path, mode):
    window = _window(qtbot, tmp_path)
    window.resize(1280, 720)
    window.show()
    qtbot.waitExposed(window)
    selector = window.workspace_mode_selector
    selector.setCurrentIndex(selector.findData(mode))

    assert selector.isVisible()
    assert selector.width() >= selector.fontMetrics().horizontalAdvance(selector.currentText())


def test_multi_signal_lanes_reserve_an_identical_left_axis_gutter(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path, size=(1280, 720))
    window._selected_signal_names.update({"VehicleStatus.Speed", "VehicleStatus.Rpm"})
    window._sync_graphs()
    qtbot.wait(20)

    plots = list(window.graph_panel.plots.values())
    assert len(plots) == 2
    assert {plot.getAxis("left").width() for plot in plots} == {SHARED_LEFT_AXIS_WIDTH}
    assert len({plot.getViewBox().sceneBoundingRect().left() for plot in plots}) == 1
