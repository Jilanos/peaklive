"""item_145 - whole-application qualification of Follow live under real load.

Two kinds of case live here.

The lane matrix is short enough for ordinary CI: it runs the reported
configuration and its neighbours - no lanes, one, six and nine, measurements
shown and hidden, recording on and off - and checks the interaction budgets
and exact data integrity on each.

The sustained case is not. It runs a real event loop for five minutes so that
at least ten 30-second look-ahead boundaries are crossed, which is the only
way boundary spikes can show up at all; averages over a six-second fixture
cannot. CI's per-test faulthandler timeout is 120 s, so it is opt-in through
`PEAKLIVE_QUALIFY=1` and its measurements are recorded in the task evidence
rather than produced on every run.

Nothing here establishes anything about Windows or the operator's machine: it
is a synthetic Linux fixture, and the packaged-executable and operator gates
are tracked separately and remain open.
"""

from __future__ import annotations

import os
from statistics import quantiles
from time import monotonic

import pytest
from PySide6.QtCore import QTimer

from peaklive.adapters import FakeCanAdapter
from peaklive.domain import CanFrame
from peaklive.services.lifecycle import AcquisitionPhase
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow
from peaklive.ui.panels.graph_navigation import (
    FOLLOW_LOOK_AHEAD_SECONDS,
    FOLLOW_MODE_FULL,
    FOLLOW_MODE_TRAILING,
)

BASE_ID = 0x300

#: The interval the AC is measured at, and the gap it allows.
HEARTBEAT_MS = 50
MAX_HEARTBEAT_GAP_S = 0.250
#: The AC's click-to-feedback budget.
MAX_FEEDBACK_S = 0.200
#: The AC's bound on how stale the newest displayed point may be.
MAX_POINT_AGE_S = 0.500

#: Long enough to cross at least ten look-ahead boundaries.
SUSTAINED_SECONDS = 10 * FOLLOW_LOOK_AHEAD_SECONDS

QUALIFY = os.environ.get("PEAKLIVE_QUALIFY") == "1"
sustained = pytest.mark.skipif(
    not QUALIFY, reason="set PEAKLIVE_QUALIFY=1 to run the five-minute qualification"
)


def _dbc(lanes: int) -> str:
    return 'VERSION ""\nNS_ :\nBS_:\nBU_: ECU\n' + "".join(
        f"BO_ {BASE_ID + index} Msg{index:02d}: 8 ECU\n"
        ' SG_ Value : 0|16@1+ (0.1,0) [0|6000] "unit" ECU\n'
        for index in range(max(lanes, 1))
    )


def _burst_adapter(lanes: int):
    """A saturated bus substitute; no physical CAN adapter is required."""

    span = max(lanes, 1)

    class BurstAdapter(FakeCanAdapter):
        def receive(self, timeout: float) -> CanFrame | None:
            if not self.connected:
                return None
            sequence = next(self._sequence)
            return CanFrame(
                timestamp=monotonic(),
                arbitration_id=BASE_ID + sequence % span,
                data=sequence.to_bytes(8, "little"),
                channel=self._profile.channel if self._profile else "channel-1",
            )

    return BurstAdapter


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

    def gaps(self, since: float = 0.0) -> list[float]:
        marks = [mark for mark in self.marks if mark >= since] + [monotonic()]
        return [b - a for a, b in zip(marks, marks[1:], strict=False)]

    def max_gap(self, since: float = 0.0) -> float:
        return max(self.gaps(since))

    def p95_gap(self, since: float = 0.0) -> float:
        values = sorted(self.gaps(since))
        if len(values) < 20:
            return max(values)
        return quantiles(values, n=20)[-1]


def _window(qtbot, tmp_path, *, lanes: int, recording: bool, measurements: bool) -> MainWindow:
    tmp_path.mkdir(parents=True, exist_ok=True)
    window = MainWindow(
        ProfileStore(tmp_path / "settings"), adapter_factory=_burst_adapter(lanes)
    )
    window.selected_profile.recording.enabled = recording
    qtbot.addWidget(window)
    path = tmp_path / "bench.dbc"
    path.write_text(_dbc(lanes), encoding="utf-8")
    window._load_dbc_path(path)
    for index in range(lanes):
        window._signal_shown_changed(f"Msg{index:02d}.Value", True)
    window.graph_panel.set_measurement_values_visible(measurements)
    window.graph_panel.set_follow_live(True)
    window.graph_panel.set_follow_live_mode(FOLLOW_MODE_FULL)
    return window


def _acquire(qtbot, window, *, seconds: float) -> None:
    window._start_acquisition()
    qtbot.waitUntil(lambda: window._lifecycle.phase is AcquisitionPhase.RUNNING, timeout=5_000)
    qtbot.wait(int(seconds * 1000))


def _settle(qtbot, window) -> None:
    window._stop_acquisition()
    qtbot.waitUntil(
        lambda: window._worker is None and window._finalizing_generation is None,
        timeout=120_000,
    )


def _point_age(window) -> float:
    """Seconds of session data between the newest sample and the newest drawn point.

    Sample time advances with wall time in a live session, so this is the lag
    between a point being accepted and a point being on screen.
    """
    bounds = window._series.bounds()
    curve = next(iter(window.graph_panel.curves.values()), None)
    if bounds is None or curve is None:
        return 0.0
    times = curve.getData()[0]
    if times is None or not len(times):
        return 0.0
    return max(0.0, float(bounds[1]) - float(times[-1]))


def _interaction_latencies(window) -> dict[str, float]:
    """Time the ordinary controls the operator reported as sluggish."""
    latencies: dict[str, float] = {}
    for name, action in (
        ("follow_off", lambda: window.graph_panel.set_follow_live(False)),
        ("follow_on", lambda: window.graph_panel.set_follow_live(True)),
        ("mode_trailing", lambda: window.graph_panel.set_follow_live_mode(FOLLOW_MODE_TRAILING)),
        ("mode_full", lambda: window.graph_panel.set_follow_live_mode(FOLLOW_MODE_FULL)),
        ("fit", window.graph_panel.fit),
        ("fit_y", window.graph_panel.fit_y),
        ("menu", lambda: window.menuBar().actions()[0].menu().actions()),
    ):
        started = monotonic()
        action()
        latencies[name] = monotonic() - started
    return latencies


# --------------------------------------------------------------------------
# AC1/AC2 - the reported configuration and its neighbours, on one fixture
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("lanes", "recording", "measurements"),
    [
        (0, False, True),
        (1, False, True),
        (6, True, True),  # the operator-reported reproduction
        (6, True, False),  # the same with the measurement table hidden
        (9, False, True),
    ],
)
def test_following_holds_its_budgets_across_the_lane_matrix(
    qtbot, tmp_path, lanes, recording, measurements
):
    window = _window(
        qtbot,
        tmp_path / f"lanes-{lanes}-{recording}-{measurements}",
        lanes=lanes,
        recording=recording,
        measurements=measurements,
    )
    heartbeat = Heartbeat()
    started = monotonic()

    _acquire(qtbot, window, seconds=3.0)
    latencies = _interaction_latencies(window)
    age = _point_age(window)
    gap = heartbeat.max_gap(started)
    heartbeat.stop()
    accepted = window._facts.report().frame_count
    _settle(qtbot, window)

    context = f"{lanes} lane(s), recording={recording}, measurements={measurements}"
    assert gap <= MAX_HEARTBEAT_GAP_S, f"{context}: event loop stalled {gap:.3f}s"
    slowest = max(latencies.items(), key=lambda item: item[1])
    assert slowest[1] <= MAX_FEEDBACK_S, f"{context}: {slowest[0]} took {slowest[1]:.3f}s"
    assert age <= MAX_POINT_AGE_S, f"{context}: newest point was {age:.3f}s stale"
    # Nothing was dropped to achieve any of the above.
    assert window._facts.report().frame_count >= accepted
    assert not window._history_failed, window._history_failure_message


def test_a_stopped_session_exposes_its_real_final_extent(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, lanes=6, recording=True, measurements=True)

    _acquire(qtbot, window, seconds=2.0)
    _settle(qtbot, window)
    qtbot.wait(300)

    extent = window.graph_panel.global_extent()
    visible = window.graph_panel.visible_window()
    assert extent is not None and visible is not None
    # No reserved future survives the stop, and the axis is no longer moving.
    assert visible[1] < extent[1] + FOLLOW_LOOK_AHEAD_SECONDS
    settled = window.graph_panel.visible_window()
    qtbot.wait(300)
    assert window.graph_panel.visible_window() == settled


def test_repeated_start_stop_cycles_keep_following_and_stay_exact(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, lanes=6, recording=False, measurements=True)

    for _ in range(3):
        _acquire(qtbot, window, seconds=1.0)
        _settle(qtbot, window)
        assert window.graph_panel.follow_live, "a wind-down must not clear the preference"
        assert not window._history_failed, window._history_failure_message
        assert window._facts.report().frame_count > 0


# --------------------------------------------------------------------------
# AC2/AC4 - sustained operation across at least ten real boundaries
# --------------------------------------------------------------------------


@sustained
def test_five_minutes_of_following_crosses_ten_boundaries_within_budget(qtbot, tmp_path):
    window = _window(qtbot, tmp_path, lanes=6, recording=True, measurements=True)
    moves: list[float] = []
    original = window.graph_panel._apply_follow

    def counted(extent):  # type: ignore[no-untyped-def]
        before = window.graph_panel.visible_window()
        original(extent)
        if window.graph_panel.visible_window() != before:
            moves.append(monotonic())

    window.graph_panel._apply_follow = counted
    ages: list[float] = []
    sampler = QTimer()
    sampler.setInterval(250)
    sampler.timeout.connect(lambda: ages.append(_point_age(window)))
    sampler.start()

    heartbeat = Heartbeat()
    started = monotonic()
    _acquire(qtbot, window, seconds=SUSTAINED_SECONDS)
    latencies = _interaction_latencies(window)
    gap, p95 = heartbeat.max_gap(started), heartbeat.p95_gap(started)
    heartbeat.stop()
    sampler.stop()
    frames = window._facts.report().frame_count
    _settle(qtbot, window)

    print(
        f"\nsustained {SUSTAINED_SECONDS:.0f}s, 6 lanes, recording on:"
        f"\n  frames accepted:      {frames}"
        f"\n  axis moves:           {len(moves)}"
        f"\n  heartbeat max / p95:  {gap:.3f}s / {p95:.3f}s"
        f"\n  point age max / mean: {max(ages):.3f}s / {sum(ages) / len(ages):.3f}s"
        f"\n  slowest control:      {max(latencies.items(), key=lambda i: i[1])}"
    )
    # Ten boundaries is the point of running this long at all.
    assert len(moves) >= 10, f"only {len(moves)} axis moves in {SUSTAINED_SECONDS:.0f}s"
    assert gap <= MAX_HEARTBEAT_GAP_S, f"event loop stalled {gap:.3f}s"
    assert max(ages) <= MAX_POINT_AGE_S, f"newest point reached {max(ages):.3f}s stale"
    slowest = max(latencies.items(), key=lambda item: item[1])
    assert slowest[1] <= MAX_FEEDBACK_S, f"{slowest[0]} took {slowest[1]:.3f}s"
    assert not window._history_failed, window._history_failure_message
