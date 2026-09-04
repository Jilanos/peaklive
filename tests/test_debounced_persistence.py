"""item_067 coverage: bursts coalesce into one expensive projection and save.

Each keystroke or pointer-drag tick used to trigger a full trace/signal-tree
rebuild and a synchronous profiles.json write. A burst of N such triggers
must now cost at most one of each, landing only once the burst goes quiet -
and a pending one must never survive a profile switch or window close.
"""

from __future__ import annotations

from peaklive.adapters import FakeCanAdapter
from peaklive.domain import CanFrame
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow
from peaklive.ui.debounce import Debouncer


def _window(qtbot, tmp_path) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    window.selected_profile.recording.enabled = False
    qtbot.addWidget(window)
    return window


# ---- Debouncer itself ------------------------------------------------------


def test_a_burst_of_triggers_runs_the_callback_once_on_flush():
    calls: list = []
    debouncer = Debouncer(50, lambda: calls.append(True))

    for _ in range(10):
        debouncer.trigger()

    assert calls == []
    debouncer.flush()
    assert calls == [True]


def test_flush_with_nothing_pending_is_a_no_op():
    calls: list = []
    debouncer = Debouncer(50, lambda: calls.append(True))

    debouncer.flush()

    assert calls == []


def test_a_trigger_after_a_flush_schedules_a_fresh_call():
    calls: list = []
    debouncer = Debouncer(50, lambda: calls.append(True))

    debouncer.trigger()
    debouncer.flush()
    debouncer.trigger()
    debouncer.flush()

    assert calls == [True, True]


# ---- profile persistence ---------------------------------------------------


def test_a_burst_of_layout_edits_saves_at_most_once(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    saves: list = []
    window._save = lambda: saves.append(True)  # type: ignore[method-assign]

    for _ in range(20):
        window._persist_layout()

    assert saves == []
    window._flush_save()
    assert saves == [True]


def test_a_burst_of_signal_selection_edits_saves_at_most_once(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    saves: list = []
    window._save = lambda: saves.append(True)  # type: ignore[method-assign]

    for index in range(10):
        window._persist_signal_state((f"Signal.{index}",))

    assert saves == []
    window._flush_save()
    assert saves == [True]


def test_switching_profiles_flushes_a_pending_save_first(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window.profile_selector.addItem("Second")
    window._state.profiles.append(window.selected_profile.duplicate("Second"))
    saves: list = []
    window._save = lambda: saves.append(True)  # type: ignore[method-assign]

    window._persist_layout()
    assert saves == []
    window._profile_changed(1)

    # One flush for the pending edit on the profile being left, one for the
    # switch itself - never zero, and never left dangling in the debouncer.
    assert saves == [True, True]


def test_closing_the_window_flushes_a_pending_save(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    saves: list = []
    window._save = lambda: saves.append(True)  # type: ignore[method-assign]

    window._persist_layout()
    assert saves == []
    window.close()

    assert saves == [True]


# ---- trace filter recompute -------------------------------------------------


def test_a_burst_of_filter_keystrokes_recomputes_the_table_once(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._render_frames([CanFrame(float(i), 0x100 + i, b"\x01") for i in range(5)])
    panel = window.trace_panel
    refreshes: list = []
    original_refresh = panel.refresh
    panel.refresh = lambda: (refreshes.append(True), original_refresh())[1]  # type: ignore[method-assign]

    for digit in "0x100":
        panel.id_filter.setText(panel.id_filter.text() + digit)

    assert refreshes == []
    panel._filters_debouncer.flush()
    assert refreshes == [True]
    assert panel.table.rowCount() == 1


# ---- signal search recompute ------------------------------------------------


def test_a_burst_of_search_keystrokes_rebuilds_the_tree_once(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    refreshes: list = []
    original = window._refresh_signal_explorer
    window._refresh_signal_explorer = lambda: (  # type: ignore[method-assign]
        refreshes.append(True),
        original(),
    )[1]

    for letter in "speed":
        window.signal_filter.setText(window.signal_filter.text() + letter)

    assert refreshes == []
    window._signal_explorer_debouncer.flush()
    assert refreshes == [True]


# ---- cursor-drag measurement recompute --------------------------------------


def test_a_burst_of_cursor_drag_ticks_recomputes_measurements_once(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._render_frames([CanFrame(float(i), 0x100, b"\x01") for i in range(5)])
    panel = window.graph_panel
    panel.cursor_a = 0.0
    panel.cursor_b = 1.0
    refreshes: list = []
    original = panel.refresh_measurements
    panel.refresh_measurements = lambda: (refreshes.append(True), original())[1]  # type: ignore[method-assign]

    class _FakeLine:
        def __init__(self, value: float) -> None:
            self._value = value

        def value(self) -> float:
            return self._value

    for tick in range(10):
        panel._cursor_dragged("a", _FakeLine(float(tick) / 10))

    assert refreshes == []
    panel._flush_measurements()
    assert refreshes == [True]
