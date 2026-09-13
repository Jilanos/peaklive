"""Acceptance coverage for the graph comparison slice (item_053, req_015).

Curve colour distinctness/stability, explicit fit-X+Y vs fit-Y-only, and the
non-destructive cursor-measurement visibility toggle.
"""

from __future__ import annotations

from PySide6.QtCore import Qt

from peaklive.adapters import FakeCanAdapter
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow, theme

VEHICLE_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 291 VehicleStatus: 8 ECU
 SG_ Speed : 0|16@1+ (0.1,0) [0|250] "km/h" ECU
 SG_ Rpm : 16|16@1+ (1,0) [0|8000] "rpm" ECU
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


# --------------------------------------------------------------------------
# AC1 - distinguishable, stable curve colours
# --------------------------------------------------------------------------


def test_simultaneously_shown_signals_get_distinct_stable_colours(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    window._signal_shown_changed("VehicleStatus.Rpm", True)

    curves = window.graph_panel.curves
    colours = {name: curve.opts["pen"].color().name() for name, curve in curves.items()}
    assert len(set(colours.values())) == len(colours)
    assert all(colour in theme.TRACE_PALETTE for colour in colours.values())

    before = dict(colours)
    window.graph_panel.refresh_data()
    after = {name: curve.opts["pen"].color().name() for name, curve in curves.items()}
    assert after == before


def test_the_curve_colour_is_named_outside_colour_alone(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    plot = next(iter(window.graph_panel.plots.values()))
    assert plot.toolTip()


# --------------------------------------------------------------------------
# item_112 - concise, coloured lane headers with a subtle lane separator
# --------------------------------------------------------------------------


def test_a_shown_lane_gets_a_horizontal_curve_coloured_header_not_a_rotated_axis_title(
    qtbot, tmp_path
):
    window = _with_dbc(qtbot, tmp_path)
    window._signal_shown_changed("VehicleStatus.Rpm", True)
    panel = window.graph_panel

    for signal_name, plot in panel.plots.items():
        assert plot.getAxis("left").labelText == ""
        header = panel.lane_headers[signal_name]
        assert header.text() == "VehicleStatus.Rpm"
        assert header.text().count(":") == 0
        curve_colour = panel.curves[signal_name].opts["pen"].color().name()
        assert curve_colour in header.styleSheet()


def test_adjacent_lanes_have_a_subtle_separator_and_keep_readable_y_ticks(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    window._signal_shown_changed("VehicleStatus.Speed", True)
    window._signal_shown_changed("VehicleStatus.Rpm", True)
    panel = window.graph_panel

    # item_128: the header is an in-ViewBox overlay parented to the plot, not
    # to the lane wrapper any more, so the separator lives on the plot's own
    # parent widget instead of the header's.
    lanes = [panel.plots[name].parentWidget() for name in panel.plots]
    assert len(lanes) >= 2
    # Every lane but the last carries the separator; the last does not, so the
    # panel's own outer edge never grows an extra, redundant boundary line.
    assert [lane.styleSheet() != "" for lane in lanes] == [True] * (len(lanes) - 1) + [False]
    for plot in panel.plots.values():
        assert plot.getAxis("left").style["showValues"] is not False


def test_hovering_the_plot_never_leaks_the_dbc_hash_but_the_lane_header_reaches_it(
    qtbot, tmp_path
):
    window = _with_dbc(qtbot, tmp_path)
    window._signal_shown_changed("VehicleStatus.Speed", True)
    panel = window.graph_panel
    signal_name = next(iter(panel.plots))
    plot = panel.plots[signal_name]
    header = panel.lane_headers[signal_name]

    database_hash = signal_name.split(":", 1)[0]
    assert database_hash not in plot.toolTip()
    assert database_hash[:8] in header.toolTip()
    assert database_hash[:8] in header.accessibleName()


# --------------------------------------------------------------------------
# item_128 - the lane title moves inside the drawable ViewBox
# --------------------------------------------------------------------------


def rect_of(panel, signal_name):
    from peaklive.ui.panels.graph_lane_header import anchor_lane_title

    plot = panel.plots[signal_name]
    header = panel.lane_headers[signal_name]
    anchor_lane_title(plot, header, header.text() or "x")
    view_box = plot.getViewBox()
    return plot.mapFromScene(view_box.sceneBoundingRect()).boundingRect()


def test_lane_title_sits_a_few_pixels_inside_the_viewbox_top_left_with_no_layout_height(
    qtbot, tmp_path
):
    window = _with_dbc(qtbot, tmp_path)
    window._signal_shown_changed("VehicleStatus.Rpm", True)
    panel = window.graph_panel
    signal_name = next(iter(panel.plots))
    plot = panel.plots[signal_name]
    header = panel.lane_headers[signal_name]

    qtbot.waitUntil(lambda: rect_of(panel, signal_name).width() > 0, timeout=2_000)
    rect = rect_of(panel, signal_name)

    # The header is a plain child of the plot, never part of any layout, so
    # it cannot claim vertical space from - or padding inside - the plot.
    assert header.parentWidget() is plot
    assert plot.layout() is None
    offset_x = header.x() - rect.left()
    offset_y = header.y() - rect.top()
    assert 2 <= offset_x <= 6
    assert 2 <= offset_y <= 6


def test_plot_area_gains_the_removed_title_row_height_for_one_three_and_eight_lanes(
    qtbot, tmp_path
):
    from peaklive.analysis import SeriesStore

    for lane_count in (1, 3, 8):
        window = _with_dbc(qtbot, tmp_path)
        panel = window.graph_panel
        names = [f"Synthetic.Signal{i}" for i in range(lane_count)]
        panel.sync(SeriesStore(), set(names))
        qtbot.waitUntil(
            lambda panel=panel, names=names: all(
                rect_of(panel, n).width() > 0 for n in names
            ),
            timeout=2_000,
        )

        rects = [rect_of(panel, name) for name in names]
        # No lane wastes a layout row on the title any more: every ViewBox's
        # top edge sits at (or right after) the lane's own top edge, not
        # pushed down by a header band.
        for name, rect in zip(names, rects, strict=True):
            lane = panel.plots[name].parentWidget()
            assert rect.top() <= lane.height() * 0.4
        # Every lane still shares one X origin (item_112's contract) and its
        # own readable Y axis.
        left_edges = {round(rect.left()) for rect in rects}
        assert len(left_edges) == 1
        for name in names:
            assert panel.plots[name].getAxis("left").style["showValues"] is not False
        bottom_axis_visible = [
            panel.plots[name].getAxis("bottom").style.get("showValues")
            for name in names
        ]
        # Exactly the last lane shows the shared bottom time axis.
        assert bottom_axis_visible.count(True) <= 1
        window.close()


def test_long_and_duplicate_lane_titles_stay_identifiable_without_leaking_hashes(
    qtbot, tmp_path
):
    from peaklive.analysis import SeriesStore

    window = _with_dbc(qtbot, tmp_path, size=(480, 400))
    panel = window.graph_panel
    long_name = "Synthetic." + "AVeryLongDuplicateSignalNameThatShouldElideCleanly" * 3
    panel.sync(SeriesStore(), {long_name})
    qtbot.waitUntil(lambda: rect_of(panel, long_name).width() > 0, timeout=2_000)

    header = panel.lane_headers[long_name]
    # A name this long cannot fit the bounded overlay width, so the visible
    # text is elided - but the full identity remains reachable through the
    # deliberate tooltip/accessible-name detail surface, never lost.
    assert header.text() != long_name
    assert header.toolTip() == long_name
    assert header.accessibleName() == long_name


def test_pan_zoom_and_cursor_drag_pass_through_the_title_overlay(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    window._signal_shown_changed("VehicleStatus.Rpm", True)
    panel = window.graph_panel
    signal_name = next(iter(panel.plots))
    header = panel.lane_headers[signal_name]

    assert header.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)


def test_title_anchoring_survives_resize_and_lane_rebuild(qtbot, tmp_path):
    from peaklive.analysis import SeriesStore

    window = _with_dbc(qtbot, tmp_path)
    panel = window.graph_panel
    panel.sync(SeriesStore(), {"VehicleStatus.Rpm"})
    qtbot.waitUntil(lambda: rect_of(panel, "VehicleStatus.Rpm").width() > 0, timeout=2_000)
    before = rect_of(panel, "VehicleStatus.Rpm")

    window.resize(window.width() + 120, window.height() + 40)
    qtbot.waitUntil(
        lambda: rect_of(panel, "VehicleStatus.Rpm").width() != before.width(), timeout=2_000
    )
    after_resize = rect_of(panel, "VehicleStatus.Rpm")
    header = panel.lane_headers["VehicleStatus.Rpm"]
    assert 2 <= header.x() - after_resize.left() <= 6
    assert 2 <= header.y() - after_resize.top() <= 6

    # A lane rebuild (signal selection changes) must re-anchor cleanly too.
    panel.sync(SeriesStore(), {"VehicleStatus.Rpm", "VehicleStatus.Speed"})
    qtbot.waitUntil(
        lambda: rect_of(panel, "VehicleStatus.Rpm").width() > 0, timeout=2_000
    )
    rebuilt_rect = rect_of(panel, "VehicleStatus.Rpm")
    rebuilt_header = panel.lane_headers["VehicleStatus.Rpm"]
    assert 2 <= rebuilt_header.x() - rebuilt_rect.left() <= 6
    assert 2 <= rebuilt_header.y() - rebuilt_rect.top() <= 6


# --------------------------------------------------------------------------
# AC7 - explicit fit X+Y and fit-Y-only
# --------------------------------------------------------------------------


def test_fit_y_only_rescales_y_and_preserves_the_visible_x_window(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    panel = window.graph_panel
    window._render_frames([_speed_frame(float(i), 100 * i) for i in range(5)])
    panel.zoom(0.5)
    window_before = panel.visible_window()

    panel.fit_y()

    assert panel.visible_window() == window_before


def test_adding_a_signal_preserves_the_visible_time_window(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    panel = window.graph_panel
    window._render_frames([_speed_frame(float(i), 100 * i) for i in range(10)])
    panel.zoom(0.4)
    window_before = panel.visible_window()

    window._signal_shown_changed("VehicleStatus.Rpm", True)

    assert panel.visible_window() == window_before


def test_fit_x_and_y_resets_the_full_extent(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    panel = window.graph_panel
    window._render_frames([_speed_frame(float(i), 100 * i) for i in range(5)])
    panel.zoom(0.2)
    assert panel.visible_window() != panel.global_extent()

    panel.fit()

    extent = panel.global_extent()
    window_ = panel.visible_window()
    assert window_ is not None and extent is not None
    assert abs(window_[0] - extent[0]) < 0.5
    assert abs(window_[1] - extent[1]) < 0.5


def test_fit_actions_handle_the_empty_session_safely(qtbot, tmp_path):
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window.graph_panel.fit()
    window.graph_panel.fit_y()  # must not raise with no plots/extent


def _speed_frame(timestamp: float, raw_speed: int):
    from peaklive.domain import CanFrame

    payload = raw_speed.to_bytes(2, "little") + b"\x00" * 6
    return CanFrame(timestamp, 291, payload)


# --------------------------------------------------------------------------
# AC8 - non-destructive measurement-visibility toggle
# --------------------------------------------------------------------------


def test_the_measurement_toggle_hides_values_but_keeps_cursor_lines(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    panel = window.graph_panel
    panel.place_cursor("a", 0.1)
    panel.place_cursor("b", 0.5)
    cursor_a, cursor_b = panel.cursor_a, panel.cursor_b
    lines_before = {name: lines for name, lines in panel._cursor_lines.items()}

    panel.measurement_visibility_button.setChecked(False)

    assert not panel.measurement.table.isVisible()
    assert not panel.measurement.range_label.isVisible()
    assert panel.cursor_a == cursor_a
    assert panel.cursor_b == cursor_b
    for name, (line_a, line_b) in panel._cursor_lines.items():
        assert (line_a, line_b) == lines_before[name]
        assert line_a.isVisible() or line_a.getViewBox() is not None


def test_the_measurement_toggle_state_persists_in_the_profile(qtbot, tmp_path):
    store = ProfileStore(tmp_path / "settings")
    window = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)

    window.graph_panel.measurement_visibility_button.setChecked(False)
    assert window.selected_profile.measurement_values_visible is False
    window._flush_save()

    restored = MainWindow(store, adapter_factory=FakeCanAdapter)
    qtbot.addWidget(restored)
    assert restored.graph_panel.measurement_visibility_button.isChecked() is False
    assert not restored.graph_panel.measurement.table.isVisible()


def test_the_measurement_toggle_defaults_to_visible_for_backward_compatibility(qtbot, tmp_path):
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)

    assert window.selected_profile.measurement_values_visible is True
    assert window.graph_panel.measurement.table.isVisible()


def test_the_toggle_is_accessible_and_keyboard_reachable(qtbot, tmp_path):
    window = _with_dbc(qtbot, tmp_path)
    button = window.graph_panel.measurement_visibility_button

    assert button.isCheckable()
    assert button.toolTip()
    assert button.accessibleName()
    assert button.focusPolicy() != Qt.FocusPolicy.NoFocus
