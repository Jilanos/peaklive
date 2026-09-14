"""item_136 coverage: the displayed-signals summary panel."""

from __future__ import annotations

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis import SeriesStore
from peaklive.i18n import translate
from peaklive.services.profiles import ProfileStore
from peaklive.services.signal_decode_worker import DecodedSeries
from peaklive.ui import MainWindow
from peaklive.ui.panels.signal_summary import SignalSummaryPanel


def _row_texts(panel: SignalSummaryPanel) -> list[tuple[str, str, str]]:
    return [
        (
            panel.tree.topLevelItem(index).text(0),
            panel.tree.topLevelItem(index).text(1),
            panel.tree.topLevelItem(index).text(2),
        )
        for index in range(panel.tree.topLevelItemCount())
    ]


def test_the_summary_orders_rows_deterministically_by_display_title(qtbot):
    panel = SignalSummaryPanel()
    qtbot.addWidget(panel)
    store = SeriesStore()
    store.append("Zebra.Signal", 0.0, 1.0, unit="km/h")
    store.append("Alpha.Signal", 0.0, 2.0, unit="rpm")

    panel.refresh(store, {"Zebra.Signal", "Alpha.Signal"})

    names = [row[0] for row in _row_texts(panel)]
    assert names == sorted(names)
    assert names[0].startswith("Alpha")


def test_a_shown_signal_with_no_sample_is_marked_unavailable(qtbot):
    panel = SignalSummaryPanel()
    qtbot.addWidget(panel)
    store = SeriesStore()

    panel.refresh(store, {"Alpha.Signal"})

    rows = _row_texts(panel)
    assert len(rows) == 1
    assert rows[0][1] == translate("signals.summary_unavailable")
    assert rows[0][2] == ""


def test_the_summary_shows_the_latest_value_and_unit(qtbot):
    panel = SignalSummaryPanel()
    qtbot.addWidget(panel)
    store = SeriesStore()
    store.append("Alpha.Signal", 0.0, 10.0, unit="km/h")
    store.append("Alpha.Signal", 1.0, 20.0, unit="km/h")

    panel.refresh(store, {"Alpha.Signal"})

    rows = _row_texts(panel)
    assert rows[0][1] == "20"
    assert rows[0][2] == "km/h"


def test_removing_a_signal_from_shown_drops_its_row(qtbot):
    panel = SignalSummaryPanel()
    qtbot.addWidget(panel)
    store = SeriesStore()
    store.append("Alpha.Signal", 0.0, 1.0)

    panel.refresh(store, {"Alpha.Signal"})
    assert panel.tree.topLevelItemCount() == 1

    panel.refresh(store, set())
    assert panel.tree.topLevelItemCount() == 0


def test_the_shell_refreshes_the_summary_immediately_then_coalesces_bursts(qtbot, tmp_path):
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    refreshes: list[int] = []
    original_refresh = window.signal_summary_panel.refresh

    def counted_refresh(*args, **kwargs):
        refreshes.append(1)
        return original_refresh(*args, **kwargs)

    window.signal_summary_panel.refresh = counted_refresh  # type: ignore[method-assign]
    # Construction already primed and started the coalescing timer; stop it so
    # the next mark below is the "first mark after idle" the test means to check.
    window._signal_summary_timer.stop()
    window._signal_summary_dirty = False

    window._mark_signal_summary_dirty()
    assert len(refreshes) == 1  # the first mark after idle refreshes right away

    window._mark_signal_summary_dirty()
    window._mark_signal_summary_dirty()
    window._mark_signal_summary_dirty()
    assert len(refreshes) == 1  # further marks inside the same second are coalesced

    window._flush_signal_summary()
    assert len(refreshes) == 2  # the coalesced tick flushes exactly once


def _idle_summary(window):
    window._mark_signal_summary_dirty()
    window._flush_signal_summary()
    window._flush_signal_summary()
    assert not window._signal_summary_timer.isActive()


def test_backfill_completion_updates_an_idle_summary(qtbot, tmp_path):
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window._selected_signal_names = {"Alpha.Signal"}
    _idle_summary(window)
    assert _row_texts(window.signal_summary_panel)[0][1] == translate("signals.summary_unavailable")

    window._signal_backfill_completed(
        window._signal_decode_generation,
        DecodedSeries("Alpha.Signal", ((1.0, 42.0),), "rpm", 0, False, 1),
    )
    window._flush_signal_summary()

    assert _row_texts(window.signal_summary_panel)[0][1:] == ("42", "rpm")


def test_reset_session_discards_the_previous_summary_values(qtbot, tmp_path):
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    window._selected_signal_names = {"Alpha.Signal"}
    window._series.append("Alpha.Signal", 1.0, 42.0, unit="rpm")
    _idle_summary(window)
    assert _row_texts(window.signal_summary_panel)[0][1] == "42"

    window._reset_session("next.asc")
    window._flush_signal_summary()

    assert _row_texts(window.signal_summary_panel)[0][1:] == (
        translate("signals.summary_unavailable"), ""
    )
