"""Full-capture replay and zero-based live navigation (req_009, item_038).

The three viewport ideas the slice separates are asserted separately: what
there is to navigate (the extent), what is shown (fit), and what happens as new
data arrives (follow-tail).
"""

from __future__ import annotations

from time import sleep

import pytest

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis import SeriesStore
from peaklive.analysis.benchmark import CaptureProfile, synthetic_dbc, write_synthetic_capture
from peaklive.analysis.history import HistoricalSignalStore
from peaklive.domain import CanFrame
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow
from peaklive.ui.panels.graph_stack import RAW_PREVIEW, GraphStackPanel

SIGNAL = "Synth0.Counter0"
CAPTURE = CaptureProfile("navigation", 4_000, message_count=1)


@pytest.fixture
def panel(qtbot) -> GraphStackPanel:
    widget = GraphStackPanel()
    qtbot.addWidget(widget)
    return widget


def _filled(panel: GraphStackPanel, samples: list[tuple[float, float]]) -> SeriesStore:
    store = SeriesStore()
    for timestamp, value in samples:
        store.append(RAW_PREVIEW, timestamp, value)
    panel.sync(store, {RAW_PREVIEW})
    return store


def _window(qtbot, tmp_path) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    return window


# --------------------------------------------------------------------------
# AC5 - a completed capture opens showing all of itself
# --------------------------------------------------------------------------


def test_a_capture_extent_is_the_span_of_its_retained_samples(panel):
    panel.begin_session(live=False)
    store = _filled(panel, [(index * 0.5, index) for index in range(200)])

    assert panel.global_extent() == store.bounds()


def test_a_completed_replay_opens_on_the_whole_capture(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    dbc = tmp_path / "synthetic.dbc"
    dbc.write_text(synthetic_dbc(CAPTURE.message_count), encoding="utf-8")
    window._load_dbc_path(dbc)
    window._selected_signal_names = {SIGNAL}
    window._sync_graphs()

    window._open_trace(write_synthetic_capture(tmp_path / "navigation.asc", CAPTURE))
    qtbot.waitUntil(lambda: window._replay_worker is None, timeout=120_000)
    # The decoder may finish before the background writer persists its tail.
    # The complete graph extent is published only after that writer settles.
    qtbot.waitUntil(lambda: window._historical_view_ready, timeout=120_000)

    extent = window.graph_panel.global_extent()
    low, high = window.graph_panel.visible_window()
    span = extent[1] - extent[0]
    assert span == pytest.approx((CAPTURE.frames - 1) * 0.001, rel=0.01)
    # The whole capture is visible, not merely its newest seconds.
    assert low <= extent[0]
    assert high >= extent[1]


def test_the_full_extent_waits_for_the_background_writer_to_settle(
    qtbot, tmp_path, monkeypatch
):
    """item_133: parsing/decoding finishing must not be mistaken for the
    complete history actually being on disk - a slow writer must not let the
    graph show a partial extent as if it were the whole capture."""
    window = _window(qtbot, tmp_path)
    dbc = tmp_path / "synthetic.dbc"
    dbc.write_text(synthetic_dbc(CAPTURE.message_count), encoding="utf-8")
    window._load_dbc_path(dbc)
    window._selected_signal_names = {SIGNAL}
    window._sync_graphs()

    original_append_many = HistoricalSignalStore.append_many

    def slow_append_many(self, samples):
        sleep(0.02)
        return original_append_many(self, samples)

    # Patched at the class level: the write runs on the background writer's
    # own store instance, not window._history.
    monkeypatch.setattr(HistoricalSignalStore, "append_many", slow_append_many)

    window._open_trace(write_synthetic_capture(tmp_path / "slow-write.asc", CAPTURE))
    qtbot.waitUntil(lambda: window._replay_worker is None, timeout=120_000)
    # Parsing/decoding is done here, but the deliberately slowed writer is
    # not guaranteed to have drained every accepted batch yet; only waiting
    # for _historical_view_ready (not just worker completion) may show the
    # true, complete extent below.
    qtbot.waitUntil(lambda: window._historical_view_ready, timeout=120_000)

    extent = window.graph_panel.global_extent()
    assert extent[1] - extent[0] == pytest.approx((CAPTURE.frames - 1) * 0.001, rel=0.01)
    assert window._history_batches_submitted == window._history_batches_settled


def test_an_explicit_zoom_outranks_the_full_extent_on_completion(panel):
    panel.begin_session(live=False)
    _filled(panel, [(index * 0.1, index) for index in range(500)])
    panel.fit()

    panel.zoom(0.1)
    zoomed = panel.visible_window()
    panel.show_full_extent()

    assert panel.follow_live is False
    assert panel.visible_window() == zoomed


def test_follow_tail_is_an_explicit_control_that_restores_the_extent(panel):
    panel.begin_session(live=False)
    _filled(panel, [(index * 0.1, index) for index in range(500)])
    panel.zoom(0.1)
    assert panel.follow_live is False

    panel.follow_checkbox.setChecked(True)

    assert panel.follow_live is True
    low, high = panel.visible_window()
    extent = panel.global_extent()
    # A window narrower than the extent now tracks the newest data.
    assert high >= extent[1] - 1e-6


def test_a_manual_range_change_disables_follow_live(panel):
    """A direct viewbox range change is exactly what pyqtgraph's own wheel
    zoom and drag-pan handling do internally - not `panel.zoom()`, which
    already goes through `set_follow_live(False)` explicitly."""
    panel.begin_session(live=True)
    _filled(panel, [(index * 0.1, index) for index in range(50)])
    assert panel.follow_live is True

    panel.anchor_plot.getViewBox().setXRange(1.0, 2.0, padding=0)

    assert panel.follow_live is False


def test_a_manual_zoom_remains_visible_after_the_next_refresh(panel):
    panel.begin_session(live=True)
    store = _filled(panel, [(index * 0.1, index) for index in range(50)])

    panel.anchor_plot.getViewBox().setXRange(1.0, 2.0, padding=0)
    zoomed = panel.visible_window()
    store.append(RAW_PREVIEW, 10.0, 1)
    panel.refresh_data()

    # A follow-live update would have moved this to track the new sample;
    # a manual zoom must be left exactly where the operator put it.
    assert panel.visible_window() == pytest.approx(zoomed)


def test_re_following_after_a_manual_zoom_restores_live_extent(panel):
    panel.begin_session(live=True)
    store = _filled(panel, [(index * 0.1, index) for index in range(50)])
    panel.anchor_plot.getViewBox().setXRange(1.0, 2.0, padding=0)
    assert panel.follow_live is False

    panel.follow_checkbox.setChecked(True)
    store.append(RAW_PREVIEW, 10.0, 1)
    panel.refresh_data()

    assert panel.follow_live is True
    _, high = panel.visible_window()
    extent = panel.global_extent()
    assert high >= extent[1] - 1e-6


def test_the_first_data_landing_on_a_fresh_plot_never_disables_follow_live(qtbot, tmp_path):
    """pyqtgraph auto-ranges a new plot the instant `setData` lands the first
    sample; that internal auto-fit must never be mistaken for a manual zoom."""
    window = _window(qtbot, tmp_path)

    window._render_frames([CanFrame(0.0, 0x100, b"\x01")])

    assert window.graph_panel.follow_live is True


def test_fit_does_not_itself_disable_follow_live(panel):
    """Fit is a deliberate view action, not a manual-zoom navigation choice."""
    panel.begin_session(live=False)
    _filled(panel, [(index * 0.1, index) for index in range(200)])
    assert panel.follow_live is True

    panel.fit()

    assert panel.follow_live is True


# --------------------------------------------------------------------------
# AC6 - a live session starts at zero and expands monotonically
# --------------------------------------------------------------------------


def test_a_live_session_starts_its_axis_at_zero(panel):
    panel.begin_session(live=True)
    _filled(panel, [(100.0 + index, index) for index in range(10)])

    assert panel.global_extent() == (0.0, 9.0)
    low, _ = panel.visible_window()
    assert low <= 0.0


def test_a_live_extent_only_ever_grows(panel):
    panel.begin_session(live=True)
    store = SeriesStore()
    panel.sync(store, {RAW_PREVIEW})
    ends = []
    for index in range(30):
        store.append(RAW_PREVIEW, index * 0.5, index)
        panel.refresh_data()
        ends.append(panel.global_extent()[1])

    assert ends == sorted(ends)
    assert all(panel.global_extent()[0] == 0.0 for _ in ends)


def test_a_bounded_series_dropping_its_oldest_samples_never_shrinks_the_axis(panel):
    panel.begin_session(live=True)
    store = SeriesStore(capacity=50)
    panel.sync(store, {RAW_PREVIEW})
    for index in range(200):
        store.append(RAW_PREVIEW, index * 0.1, index)
    panel.refresh_data()

    # The retained samples no longer reach back to the session start ...
    assert store.bounds()[0] > 0.0
    # ... but the operator's view of elapsed session time still does.
    assert panel.global_extent() == (0.0, pytest.approx(19.9))


def test_opening_a_capture_after_a_live_session_adopts_capture_semantics(panel):
    panel.begin_session(live=True)
    _filled(panel, [(index * 1.0, index) for index in range(10)])
    assert panel.global_extent() == (0.0, 9.0)

    panel.begin_session(live=False)
    store = _filled(panel, [(50.0 + index, index) for index in range(10)])

    assert panel.global_extent() == store.bounds()


def test_a_live_acquisition_shows_a_zero_based_axis_end_to_end(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    window._start_acquisition()
    qtbot.waitUntil(lambda: len(window._series.names) > 0, timeout=30_000)
    window._flush_presentation()
    extent = window.graph_panel.global_extent()
    window._stop_acquisition()
    qtbot.waitUntil(lambda: window.start_button.isEnabled(), timeout=30_000)

    assert extent[0] == 0.0
    low, high = window.graph_panel.visible_window()
    assert low <= 0.0
    assert high >= extent[1]


# --------------------------------------------------------------------------
# AC7 - the surrounding graph controls keep working
# --------------------------------------------------------------------------


def test_the_menu_bar_offers_full_and_trailing_follow_live_modes(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    actions = window._follow_live_mode_actions
    assert set(actions) == {"full", "trailing"}
    assert actions["full"].isChecked()
    assert not actions["trailing"].isChecked()
    assert window.graph_panel.follow_live_mode == "full"


def test_choosing_trailing_mode_restores_the_pinned_narrow_window_on_follow(panel):
    panel.begin_session(live=False)
    _filled(panel, [(index * 0.1, index) for index in range(500)])
    panel.zoom(0.1)
    zoomed_span = panel.visible_window()[1] - panel.visible_window()[0]
    panel.set_follow_live_mode("trailing")

    panel.follow_checkbox.setChecked(True)

    low, high = panel.visible_window()
    extent = panel.global_extent()
    assert high >= extent[1] - 1e-6
    assert high - low == pytest.approx(zoomed_span)


def test_full_mode_shows_the_whole_extent_even_after_a_narrow_zoom(panel):
    panel.begin_session(live=False)
    _filled(panel, [(index * 0.1, index) for index in range(500)])
    panel.zoom(0.1)
    assert panel.follow_live_mode == "full"

    panel.follow_checkbox.setChecked(True)

    low, high = panel.visible_window()
    extent = panel.global_extent()
    assert low <= extent[0]
    assert high >= extent[1]


# --------------------------------------------------------------------------
# item_137 AC1/AC2 - a shared clamp bounds every manual pan/zoom
# --------------------------------------------------------------------------


def test_manual_navigation_cannot_travel_far_past_either_data_edge(panel):
    panel.begin_session(live=False)
    _filled(panel, [(index * 0.1, index) for index in range(1000)])
    extent = panel.global_extent()
    span = extent[1] - extent[0]

    panel.anchor_plot.getViewBox().setXRange(-1000.0, -900.0, padding=0)

    low, high = panel.visible_window()
    assert low >= extent[0] - span * 0.05 - 1e-9
    assert high <= extent[1] + span * 0.05 + 1e-9
    # Snapped back to something overlapping real data, not left stranded blank.
    assert high > extent[0]


def test_the_clamp_stays_finite_and_non_degenerate_for_a_single_sample(panel):
    panel.begin_session(live=False)
    _filled(panel, [(5.0, 1)])

    panel.anchor_plot.getViewBox().setXRange(100.0, 200.0, padding=0)

    low, high = panel.visible_window()
    assert high > low
    assert low == low  # not NaN
    assert high == high  # not NaN


def test_the_clamp_stays_finite_and_non_degenerate_for_an_empty_extent(panel):
    panel.begin_session(live=False)
    panel.sync(SeriesStore(), {RAW_PREVIEW})

    # No data at all: nothing to clamp against, and no crash either.
    panel.anchor_plot.getViewBox().setXRange(100.0, 200.0, padding=0)
    assert panel.global_extent() is None


def test_manual_navigation_within_bounds_is_left_untouched(panel):
    panel.begin_session(live=False)
    _filled(panel, [(index * 0.1, index) for index in range(100)])
    extent = panel.global_extent()

    panel.anchor_plot.getViewBox().setXRange(*extent, padding=0)
    requested = panel.visible_window()

    assert requested == pytest.approx(extent)


def test_fit_zoom_and_cursors_still_operate_on_the_extent(panel):
    panel.begin_session(live=False)
    _filled(panel, [(index * 0.1, index) for index in range(100)])
    panel.fit()
    fitted = panel.visible_window()

    panel.zoom(0.5)
    zoomed = panel.visible_window()
    panel.place_cursor("a", 1.0)
    panel.place_cursor("b", 5.0)
    panel.fit_button.click()

    assert zoomed[1] - zoomed[0] < fitted[1] - fitted[0]
    assert panel.cursor_range == (1.0, 5.0)
    assert panel.visible_window() == pytest.approx(fitted)
