"""item_145 - exact boundary semantics for the reserved Follow-live axis.

The look-ahead policy is a rule about *when* the axis is allowed to move, so
it is qualified here by driving the extent directly rather than by waiting on
a real acquisition: sample time is the only clock that decides a boundary, and
these cases pin what happens at, before and after each one. Wall-clock
behaviour under a real event loop is measured separately, in
`test_follow_live_qualification.py`.
"""

from __future__ import annotations

import pytest

from peaklive.analysis import SeriesStore
from peaklive.ui.panels.graph_navigation import (
    FOLLOW_LOOK_AHEAD_SECONDS,
    FOLLOW_MODE_FULL,
    FOLLOW_MODE_TRAILING,
)
from peaklive.ui.panels.graph_stack import RAW_PREVIEW, GraphStackPanel


@pytest.fixture
def panel(qtbot) -> GraphStackPanel:
    widget = GraphStackPanel()
    qtbot.addWidget(widget)
    return widget


def _live(panel: GraphStackPanel) -> SeriesStore:
    """A live session with one lane and no samples yet.

    `SeriesStore` times every sample from the session's own first one, so the
    values driven here are already the session-relative seconds the axis reads.
    """
    store = SeriesStore()
    panel.sync(store, {RAW_PREVIEW})
    panel.begin_session(live=True)
    store.append(RAW_PREVIEW, 0.0, 0.0)
    return store


def _advance(panel: GraphStackPanel, store: SeriesStore, newest: float) -> None:
    """Append one sample at `newest` and let the follow policy react to it."""
    store.append(RAW_PREVIEW, newest, 1.0)
    panel.refresh_data()


def _right_edge(panel: GraphStackPanel) -> float:
    window = panel.visible_window()
    assert window is not None
    return window[1]


def _span(panel: GraphStackPanel) -> float:
    window = panel.visible_window()
    assert window is not None
    return window[1] - window[0]


# --------------------------------------------------------------------------
# Full mode: [0, newest + 30 s], held until data reaches the reserved edge
# --------------------------------------------------------------------------


def test_the_first_sample_reserves_thirty_seconds_and_anchors_at_zero(panel):
    store = _live(panel)

    _advance(panel, store, 0.5)

    window = panel.visible_window()
    assert window == pytest.approx((0.0, 0.5 + FOLLOW_LOOK_AHEAD_SECONDS), abs=1e-6)


def test_the_axis_does_not_move_again_until_data_reaches_the_reserved_edge(panel):
    store = _live(panel)
    _advance(panel, store, 0.5)
    reserved = _right_edge(panel)

    for newest in (1.0, 5.0, 17.5, reserved - 0.001):
        _advance(panel, store, newest)
        assert _right_edge(panel) == pytest.approx(reserved, abs=1e-6), newest


def test_reaching_the_reserved_edge_advances_it_once_by_a_full_look_ahead(panel):
    store = _live(panel)
    _advance(panel, store, 0.5)
    reserved = _right_edge(panel)

    _advance(panel, store, reserved + 0.25)

    assert _right_edge(panel) == pytest.approx(
        reserved + 0.25 + FOLLOW_LOOK_AHEAD_SECONDS, abs=1e-6
    )


def test_a_large_timestamp_jump_is_absorbed_in_one_update(panel):
    """Not one catch-up step per missed interval."""
    store = _live(panel)
    _advance(panel, store, 0.5)
    moves = []
    original = panel._apply_follow
    panel._apply_follow = lambda extent: (moves.append(extent), original(extent))

    _advance(panel, store, 10_000.0)

    assert len(moves) == 1
    assert _right_edge(panel) == pytest.approx(10_000.0 + FOLLOW_LOOK_AHEAD_SECONDS, abs=1e-6)


def test_an_idle_session_neither_fabricates_data_nor_advances_the_extent(panel):
    store = _live(panel)
    _advance(panel, store, 2.0)
    reserved = _right_edge(panel)

    for _ in range(5):
        panel.refresh_data()

    assert _right_edge(panel) == pytest.approx(reserved, abs=1e-6)
    # Reserved canvas is display only: the navigable extent stops at the data.
    assert panel.global_extent() == pytest.approx((0.0, 2.0), abs=1e-6)
    assert store.bounds() == pytest.approx((0.0, 2.0), abs=1e-6)


def test_an_empty_session_reserves_nothing(panel):
    store = SeriesStore()
    panel.sync(store, {RAW_PREVIEW})
    panel.begin_session(live=True)

    panel.refresh_data()

    assert panel.global_extent() is None
    assert panel._reserved_axis_end is None


# --------------------------------------------------------------------------
# Trailing mode: span W preserved, look-ahead capped at W/4
# --------------------------------------------------------------------------


def _trailing(panel: GraphStackPanel, store: SeriesStore, span: float, newest: float) -> None:
    """Adopt trailing mode over a deliberately chosen window of width `span`."""
    _advance(panel, store, newest)
    panel.set_follow_live_mode(FOLLOW_MODE_TRAILING)
    panel._applying_range = True
    panel.anchor_plot.getViewBox().setXRange(newest - span, newest, padding=0)
    panel._applying_range = False
    panel._window_chosen = True
    panel._release_reserved_axis()
    panel.refresh_data()


def test_a_short_trailing_window_reserves_only_a_quarter_of_itself(panel):
    store = _live(panel)

    _trailing(panel, store, span=8.0, newest=100.0)

    assert _span(panel) == pytest.approx(8.0, abs=1e-6)
    assert _right_edge(panel) == pytest.approx(100.0 + 2.0, abs=1e-6)


def test_a_long_trailing_window_is_capped_at_thirty_seconds(panel):
    store = _live(panel)

    _trailing(panel, store, span=600.0, newest=1_000.0)

    assert _span(panel) == pytest.approx(600.0, abs=1e-6)
    assert _right_edge(panel) == pytest.approx(1_000.0 + FOLLOW_LOOK_AHEAD_SECONDS, abs=1e-6)


def test_a_trailing_window_keeps_its_width_across_a_boundary(panel):
    store = _live(panel)
    _trailing(panel, store, span=8.0, newest=100.0)
    reserved = _right_edge(panel)

    _advance(panel, store, reserved + 0.5)

    assert _span(panel) == pytest.approx(8.0, abs=1e-6)
    assert _right_edge(panel) == pytest.approx(reserved + 0.5 + 2.0, abs=1e-6)


def test_the_newest_sample_is_never_clipped_by_the_trailing_window(panel):
    store = _live(panel)
    _trailing(panel, store, span=8.0, newest=100.0)

    for newest in (101.0, 102.0, 103.5, 110.0, 130.0):
        _advance(panel, store, newest)
        window = panel.visible_window()
        assert window is not None and window[0] <= newest <= window[1], newest


# --------------------------------------------------------------------------
# Mode, session and navigation transitions reset the reserved edge
# --------------------------------------------------------------------------


def test_switching_mode_recomputes_the_reserved_edge(panel):
    store = _live(panel)
    _advance(panel, store, 5.0)
    assert _right_edge(panel) == pytest.approx(5.0 + FOLLOW_LOOK_AHEAD_SECONDS, abs=1e-6)

    panel.set_follow_live_mode(FOLLOW_MODE_TRAILING)
    panel.set_follow_live_mode(FOLLOW_MODE_FULL)

    assert _right_edge(panel) == pytest.approx(5.0 + FOLLOW_LOOK_AHEAD_SECONDS, abs=1e-6)


def test_a_new_session_cannot_inherit_the_previous_reserved_edge(panel):
    store = _live(panel)
    _advance(panel, store, 500.0)

    fresh = _live(panel)
    _advance(panel, fresh, 1.0)

    assert _right_edge(panel) == pytest.approx(1.0 + FOLLOW_LOOK_AHEAD_SECONDS, abs=1e-6)


def test_re_enabling_follow_catches_up_at_once_rather_than_at_the_old_edge(panel):
    store = _live(panel)
    _advance(panel, store, 5.0)
    panel.zoom(0.25)
    assert not panel.follow_live
    chosen = panel.visible_window()

    _advance(panel, store, 400.0)
    assert panel.visible_window() == chosen, "a stopped follow must not move the viewport"

    panel.set_follow_live(True)
    panel.refresh_data()

    assert _right_edge(panel) >= 400.0


def test_fit_shows_the_real_extent_and_following_does_not_undo_it(panel):
    store = _live(panel)
    _advance(panel, store, 5.0)

    panel.fit()
    fitted = panel.visible_window()
    for _ in range(3):
        panel.refresh_data()

    assert fitted is not None
    assert panel.visible_window() == fitted
    assert fitted[1] < 5.0 + FOLLOW_LOOK_AHEAD_SECONDS


def test_a_capture_reserves_no_future_at_all(panel):
    store = SeriesStore()
    for index in range(200):
        store.append(RAW_PREVIEW, index * 0.1, float(index))
    panel.sync(store, {RAW_PREVIEW})
    panel.begin_session(live=False)

    panel.refresh_data()

    window = panel.visible_window()
    assert window is not None
    assert window[1] < 19.9 + FOLLOW_LOOK_AHEAD_SECONDS
