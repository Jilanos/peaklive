"""item_144 - what Follow live actually costs, and the bound placed on it.

The operator reported that enabling Follow live makes the whole application
less responsive during ordinary six-curve acquisition, not only at Stop. These
tests measure the follow-related work per configuration on one fixture, so the
comparison is evidence rather than attribution, and then pin the bound the
measurement justified.
"""

from __future__ import annotations

from time import monotonic

import pytest
from PySide6.QtCore import QTimer

from peaklive.adapters import FakeCanAdapter
from peaklive.domain import CanFrame
from peaklive.services.lifecycle import AcquisitionPhase
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow
from peaklive.ui.panels.graph_navigation import FOLLOW_MODE_FULL, FOLLOW_MODE_TRAILING

#: The reported reproduction: six displayed curves on a live session.
LANES = 6
BASE_ID = 0x300

#: The interval the AC is measured at, and the gap it allows.
HEARTBEAT_MS = 50
MAX_HEARTBEAT_GAP_S = 0.250
#: The AC's click-to-feedback budget.
MAX_FEEDBACK_S = 0.200

BENCH_DBC = 'VERSION ""\nNS_ :\nBS_:\nBU_: ECU\n' + "".join(
    f"BO_ {BASE_ID + index} Msg{index:02d}: 8 ECU\n"
    ' SG_ Value : 0|16@1+ (0.1,0) [0|6000] "unit" ECU\n'
    for index in range(LANES)
)


class BurstAdapter(FakeCanAdapter):
    """A saturated bus substitute; no physical CAN adapter is required."""

    def receive(self, timeout: float) -> CanFrame | None:
        if not self.connected:
            return None
        sequence = next(self._sequence)
        return CanFrame(
            timestamp=monotonic(),
            arbitration_id=BASE_ID + sequence % LANES,
            data=sequence.to_bytes(8, "little"),
            channel=self._profile.channel if self._profile else "channel-1",
        )


class Heartbeat:
    """Records UI-thread timer ticks, so 'still responsive' is a measurement."""

    def __init__(self) -> None:
        self.marks = [monotonic()]
        self._timer = QTimer()
        self._timer.setInterval(HEARTBEAT_MS)
        self._timer.timeout.connect(lambda: self.marks.append(monotonic()))
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def max_gap(self, since: float = 0.0) -> float:
        marks = [mark for mark in self.marks if mark >= since] + [monotonic()]
        return max(b - a for a, b in zip(marks, marks[1:], strict=False))


class RangeWork:
    """Counts the axis work one configuration performs over a fixed window."""

    def __init__(self, window: MainWindow) -> None:
        self.refreshes = 0
        self.follow_applications = 0
        self.range_moves = 0
        self.view_notifications = 0
        panel = window.graph_panel
        panel.view_changed.connect(self._note_notification)
        apply_follow = panel._apply_follow
        refresh_data = panel.refresh_data

        def counted_follow(extent):  # type: ignore[no-untyped-def]
            self.follow_applications += 1
            before = panel.visible_window()
            apply_follow(extent)
            if panel.visible_window() != before:
                self.range_moves += 1

        def counted_refresh():  # type: ignore[no-untyped-def]
            self.refreshes += 1
            refresh_data()

        panel._apply_follow = counted_follow
        panel.refresh_data = counted_refresh

    def _note_notification(self) -> None:
        self.view_notifications += 1

    def as_row(self, gap: float) -> tuple[int, int, int, int, float]:
        return (
            self.refreshes,
            self.follow_applications,
            self.range_moves,
            self.view_notifications,
            round(gap, 4),
        )


def _bench_window(qtbot, tmp_path) -> MainWindow:
    tmp_path.mkdir(parents=True, exist_ok=True)
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=BurstAdapter)
    window.selected_profile.recording.enabled = False
    qtbot.addWidget(window)
    path = tmp_path / "bench.dbc"
    path.write_text(BENCH_DBC, encoding="utf-8")
    window._load_dbc_path(path)
    for index in range(LANES):
        window._signal_shown_changed(f"Msg{index:02d}.Value", True)
    return window


def _acquire(qtbot, window, *, seconds: float) -> None:
    window._start_acquisition()
    qtbot.waitUntil(lambda: window._lifecycle.phase is AcquisitionPhase.RUNNING, timeout=5_000)
    qtbot.wait(int(seconds * 1000))


def _settle(qtbot, window) -> None:
    window._stop_acquisition()
    qtbot.waitUntil(
        lambda: window._worker is None and window._finalizing_generation is None,
        timeout=60_000,
    )


# --------------------------------------------------------------------------
# AC1 - isolate the dominant work, and say whether Follow off removes it
# --------------------------------------------------------------------------


def test_follow_off_full_and_trailing_are_measured_on_one_fixture(qtbot, tmp_path):
    """Record the off/full/trailing comparison the request asks for."""
    measured: dict[tuple[bool, str], tuple[int, int, int, int, float]] = {}
    for index, (follow, mode) in enumerate(
        ((False, FOLLOW_MODE_FULL), (True, FOLLOW_MODE_FULL), (True, FOLLOW_MODE_TRAILING))
    ):
        window = _bench_window(qtbot, tmp_path / f"follow-{index}")
        window.graph_panel.set_follow_live(follow)
        window.graph_panel.set_follow_live_mode(mode)
        if mode == FOLLOW_MODE_TRAILING:
            window.graph_panel._window_chosen = True
        work = RangeWork(window)

        heartbeat = Heartbeat()
        started = monotonic()
        _acquire(qtbot, window, seconds=3.0)
        gap = heartbeat.max_gap(started)
        heartbeat.stop()
        _settle(qtbot, window)
        measured[(follow, mode)] = work.as_row(gap)
        window.close()

    print("\nfollow/mode -> (refreshes, follow calls, axis moves, view signals, max gap s)")
    for key, value in measured.items():
        print(f"  {key}: {value}")
    for key, row in measured.items():
        gap = row[-1]
        assert gap <= MAX_HEARTBEAT_GAP_S, f"{key} stalled for {gap:.3f}s; all: {measured}"
    # Following must not cost an axis move per refresh: the reserved look-ahead
    # keeps the axis still between boundaries, so each following configuration
    # stays within the same order of magnitude as not following at all.
    off_moves = measured[(False, FOLLOW_MODE_FULL)][2]
    for follow, mode in ((True, FOLLOW_MODE_FULL), (True, FOLLOW_MODE_TRAILING)):
        assert measured[(follow, mode)][2] <= max(off_moves, 1) * 20, measured


# --------------------------------------------------------------------------
# AC2 - the delivered policy holds the interaction and freshness budgets
# --------------------------------------------------------------------------


def test_following_a_six_lane_session_keeps_controls_within_budget(qtbot, tmp_path):
    window = _bench_window(qtbot, tmp_path)
    window.graph_panel.set_follow_live(True)
    window.graph_panel.set_follow_live_mode(FOLLOW_MODE_FULL)

    heartbeat = Heartbeat()
    started = monotonic()
    _acquire(qtbot, window, seconds=3.0)
    clicked = monotonic()
    window.graph_panel.set_follow_live(False)
    window.graph_panel.set_follow_live(True)
    feedback = monotonic() - clicked
    gap = heartbeat.max_gap(started)
    heartbeat.stop()
    _settle(qtbot, window)

    assert feedback <= MAX_FEEDBACK_S, f"follow toggle took {feedback:.3f}s"
    assert gap <= MAX_HEARTBEAT_GAP_S, f"event loop stalled for {gap:.3f}s"


def test_incoming_points_stay_visible_between_axis_moves(qtbot, tmp_path):
    """The axis steps; the curves do not wait for it (req_034 AC6)."""
    window = _bench_window(qtbot, tmp_path)
    window.graph_panel.set_follow_live(True)
    window.graph_panel.set_follow_live_mode(FOLLOW_MODE_FULL)

    _acquire(qtbot, window, seconds=1.0)
    window_before = window.graph_panel.visible_window()
    newest_before = window._series.bounds()[1]
    qtbot.wait(700)
    newest_after = window._series.bounds()[1]
    _settle(qtbot, window)

    assert newest_after > newest_before, "acquisition stopped producing samples"
    assert window_before is not None
    # The newest sample is inside the reserved window, so it is on screen
    # without the axis having had to move for it.
    assert window_before[0] <= newest_after <= window_before[1]


# --------------------------------------------------------------------------
# AC3 - truthful bounds, manual navigation, modes and finalization
# --------------------------------------------------------------------------


def test_reserved_future_space_never_invents_samples_or_bounds(qtbot, tmp_path):
    window = _bench_window(qtbot, tmp_path)
    window.graph_panel.set_follow_live(True)

    _acquire(qtbot, window, seconds=1.0)
    _settle(qtbot, window)
    visible = window.graph_panel.visible_window()
    extent = window.graph_panel.global_extent()
    newest = window._series.bounds()[1]

    assert visible is not None and extent is not None
    # Display padding is display only: the navigable extent and the real
    # sample bounds both stop at the newest acquired sample.
    assert extent[1] <= newest + 1e-6


def test_manual_navigation_cancels_following_and_re_enabling_catches_up(qtbot, tmp_path):
    window = _bench_window(qtbot, tmp_path)
    window.graph_panel.set_follow_live(True)

    _acquire(qtbot, window, seconds=1.0)
    window.graph_panel.zoom(0.25)
    assert not window.graph_panel.follow_live
    chosen = window.graph_panel.visible_window()
    qtbot.wait(400)
    assert window.graph_panel.visible_window() == chosen

    window.graph_panel.set_follow_live(True)
    window.graph_panel.refresh_data()
    caught_up = window.graph_panel.visible_window()
    newest = window._series.bounds()[1]
    _settle(qtbot, window)

    assert caught_up is not None and chosen is not None
    assert caught_up != chosen
    assert caught_up[1] >= newest


def test_a_short_trailing_window_is_never_silently_widened(qtbot, tmp_path):
    window = _bench_window(qtbot, tmp_path)
    window.graph_panel.set_follow_live_mode(FOLLOW_MODE_TRAILING)

    _acquire(qtbot, window, seconds=3.0)
    # Choose a window narrower than the acquired extent, the way a manual
    # zoom does; the trailing policy only applies to such a window.
    panel = window.graph_panel
    newest = window._series.bounds()[1]
    chosen_span = newest / 3
    panel._applying_range = True
    panel.anchor_plot.getViewBox().setXRange(newest - chosen_span, newest, padding=0)
    panel._applying_range = False
    panel._window_chosen = True
    panel.set_follow_live(True)
    panel.refresh_data()
    following = panel.visible_window()
    newest_now = window._series.bounds()[1]
    _settle(qtbot, window)

    assert following is not None
    # The selected span is preserved; only where it sits may change, and the
    # look-ahead it reserves is a quarter of it at most.
    assert following[1] - following[0] == pytest.approx(chosen_span, abs=1e-6)
    assert following[1] - newest_now <= chosen_span / 4 + 1e-6


def test_a_stopped_session_settles_on_its_real_final_extent(qtbot, tmp_path):
    window = _bench_window(qtbot, tmp_path)
    window.graph_panel.set_follow_live(True)

    _acquire(qtbot, window, seconds=1.0)
    _settle(qtbot, window)
    qtbot.wait(200)
    visible = window.graph_panel.visible_window()
    extent = window.graph_panel.global_extent()

    assert visible is not None and extent is not None
    # No reserved future space survives the stop: the axis shows what the
    # session actually holds.
    assert visible[1] <= extent[1] + max((extent[1] - extent[0]) * 0.05, 0.5)
