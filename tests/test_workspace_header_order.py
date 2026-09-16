"""item_142 - one documented header order, one icon contract.

Fit used to precede the lifecycle controls, Follow live reused the same play
triangle as Start, and every action's apparent size depended on whatever font
the platform resolved for its pictogram. These pin the order the request
documents, the shared box and canvas every action now uses, and the fact that
resizing can no longer permute the row.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QImage

from peaklive.adapters import FakeCanAdapter
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow
from peaklive.ui.icons import BUTTON_BOX, ICON_CANVAS, header_icon

VEHICLE_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 291 VehicleStatus: 8 ECU
 SG_ Speed : 0|16@1+ (0.1,0) [0|250] "km/h" ECU
'''

BENCH_VIEWPORTS = [(1024, 768), (1280, 720), (1600, 900)]


def _window(qtbot, tmp_path, size=(1600, 900)) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window.resize(*size)
    window.show()
    qtbot.waitExposed(window)
    path = tmp_path / "vehicle.dbc"
    path.write_text(VEHICLE_DBC, encoding="utf-8")
    window._load_dbc_path(path)
    qtbot.wait(20)
    return window


def _canonical(window: MainWindow) -> list:
    controls = window.graph_panel.controls
    return [
        window.workspace_mode_selector,
        window.acquisition_bar.start_button,
        window.acquisition_bar.stop_button,
        window.acquisition_bar.bus_state_frame,
        controls.follow_checkbox,
        controls.fit_button,
        controls.fit_y_button,
        controls.cursor_a_button,
        controls.cursor_b_button,
        controls.measurement_visibility_button,
        controls.cursor_summary,
    ]


def _row_order(window: MainWindow) -> list:
    row = window.workspace_header.row
    known = set(_canonical(window))
    return [
        row.itemAt(index).widget()
        for index in range(row.count())
        if row.itemAt(index).widget() in known
    ]


def _always_on_the_row(window: MainWindow) -> list:
    controls = window.graph_panel.controls
    return [
        window.acquisition_bar.start_button,
        window.acquisition_bar.stop_button,
        controls.follow_checkbox,
        controls.fit_button,
        controls.fit_y_button,
        controls.cursor_a_button,
        controls.cursor_b_button,
    ]


# --------------------------------------------------------------------------
# AC1 - the documented order, and it stays that order
# --------------------------------------------------------------------------


def test_the_header_lays_the_controls_out_in_the_documented_order(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    order = _row_order(window)
    expected = [control for control in _canonical(window) if control in order]

    assert order == expected
    assert len(order) == len(_canonical(window))


def test_the_groups_are_separated_on_the_row(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    # With the side panels out of the way the row has room for its
    # decoration; under width pressure the rules are the first thing dropped,
    # which is a separate contract from the order they sit in.
    window.signals_panel.set_collapsed(True)
    window.inspector_panel.set_collapsed(True)
    qtbot.wait(50)
    row = window.workspace_header.row
    rules = [rule for rule in window.workspace_header._rules if rule.isVisible()]
    positions = [row.indexOf(rule) for rule in rules]

    assert len(rules) == 3
    assert positions == sorted(positions)
    for rule, control in zip(
        rules,
        (
            window.acquisition_bar.start_button,
            window.graph_panel.controls.follow_checkbox,
            window.graph_panel.controls.cursor_a_button,
        ),
        strict=True,
    ):
        assert row.indexOf(rule) == row.indexOf(control) - 1


def test_the_order_survives_repeated_narrow_and_wide_resizes(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    before = _row_order(window)

    for _ in range(3):
        window.resize(1024, 768)
        qtbot.wait(20)
        narrow = _row_order(window)
        assert narrow == [control for control in _canonical(window) if control in narrow]
        window.resize(1600, 900)
        qtbot.wait(20)

    assert _row_order(window) == before


def test_the_order_survives_switching_the_centre_view(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    before = _row_order(window)

    for mode in ("graphs", "trace", "report", "combo"):
        window._apply_workspace_mode(mode)
        qtbot.wait(10)

    assert _row_order(window) == before


# --------------------------------------------------------------------------
# AC2 - one box, one canvas, seven controls on one line at every bench size
# --------------------------------------------------------------------------


@pytest.mark.parametrize("size", BENCH_VIEWPORTS)
def test_the_primary_controls_stay_on_one_line_at_every_bench_viewport(qtbot, tmp_path, size):
    window = _window(qtbot, tmp_path, size=size)
    header = window.workspace_header

    for control in _always_on_the_row(window):
        assert control.parent() is header, control.objectName()
        assert control.isVisible(), control.objectName()
        left = control.mapTo(header, control.rect().topLeft()).x()
        right = control.mapTo(header, control.rect().topRight()).x()
        assert 0 <= left <= right <= header.width(), control.objectName()


@pytest.mark.parametrize("size", BENCH_VIEWPORTS)
def test_no_two_header_controls_overlap_at_any_bench_viewport(qtbot, tmp_path, size):
    window = _window(qtbot, tmp_path, size=size)
    header = window.workspace_header
    row = header.row
    rects = []
    for index in range(row.count()):
        widget = row.itemAt(index).widget()
        if widget is None or widget.isHidden():
            continue
        rects.append((widget, widget.geometry()))
    for first in range(len(rects)):
        for second in range(first + 1, len(rects)):
            assert not rects[first][1].intersects(rects[second][1]), (
                rects[first][0].objectName(),
                rects[second][0].objectName(),
            )


def test_every_header_action_uses_the_shared_box_and_icon_canvas(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    for control in _always_on_the_row(window) + [
        window.graph_panel.controls.measurement_visibility_button
    ]:
        assert control.size() == QSize(BUTTON_BOX, BUTTON_BOX), control.objectName()
        assert control.iconSize() == QSize(ICON_CANVAS, ICON_CANVAS), control.objectName()
        assert not control.icon().isNull(), control.objectName()
        assert control.text() == "", control.objectName()


# --------------------------------------------------------------------------
# AC3 - distinct meanings, named, reachable from the keyboard
# --------------------------------------------------------------------------


def _bytes(name: str, size: int = ICON_CANVAS, mode=QIcon.Mode.Normal) -> bytes:
    """The drawn pixels, copied out so two icons can actually be compared."""
    pixmap = header_icon(name).pixmap(QSize(size, size), mode, QIcon.State.Off)
    image = pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
    return bytes(image.constBits())


def test_play_and_follow_live_no_longer_share_one_pictogram(qtbot, tmp_path):
    del qtbot, tmp_path
    assert _bytes("play") != _bytes("follow_live")


def test_the_two_fit_actions_are_drawn_differently(qtbot, tmp_path):
    del qtbot, tmp_path
    assert _bytes("fit_xy") != _bytes("fit_y")


def test_every_icon_redraws_for_the_size_it_is_asked_for(qtbot, tmp_path):
    del qtbot, tmp_path
    for name in ("play", "stop", "follow_live", "fit_xy", "fit_y", "cursor_a", "cursor_b"):
        small = header_icon(name).pixmap(QSize(16, 16))
        large = header_icon(name).pixmap(QSize(32, 32))
        # Device pixels, so the raw sizes follow whatever ratio the screen
        # reports; what matters is that a larger request is painted larger
        # rather than served from one cached bitmap.
        assert not small.isNull() and not large.isNull()
        assert large.width() >= small.width() * 2 - 1
        assert _bytes(name, 16) != _bytes(name, 32)


def test_a_disabled_action_is_drawn_in_the_disabled_foreground(qtbot, tmp_path):
    del qtbot, tmp_path
    assert _bytes("play") != _bytes("play", mode=QIcon.Mode.Disabled)


def test_every_header_action_keeps_a_name_a_tooltip_and_keyboard_focus(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    for control in _always_on_the_row(window):
        assert control.accessibleName(), control.objectName()
        assert control.toolTip(), control.objectName()
        assert control.focusPolicy() != Qt.FocusPolicy.NoFocus, control.objectName()

    controls = window.graph_panel.controls
    assert controls.follow_checkbox.accessibleName() != window.start_button.accessibleName()
    assert controls.fit_button.toolTip() != controls.fit_y_button.toolTip()


def test_follow_live_still_reads_as_checked_or_unchecked(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    follow = window.graph_panel.controls.follow_checkbox

    assert follow.isCheckable()
    follow.setChecked(True)
    assert follow.isChecked()
    follow.setChecked(False)
    assert not follow.isChecked()


def test_stop_reads_as_active_only_while_it_can_stop_something(qtbot, tmp_path):
    from peaklive.services.lifecycle import AcquisitionPhase

    window = _window(qtbot, tmp_path)
    stop = window.stop_button

    window.acquisition_bar.set_lifecycle_phase(AcquisitionPhase.RUNNING)
    assert stop.property("active") is True
    assert stop.isEnabled()

    window.acquisition_bar.set_lifecycle_phase(AcquisitionPhase.STOPPED)
    assert stop.property("active") is False
    assert not stop.isEnabled()
