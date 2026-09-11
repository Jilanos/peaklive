from pathlib import Path

from peaklive.analysis import HistoricalSignalStore, SeriesStore
from peaklive.ui.panels.graph_stack import GraphStackPanel


def test_historical_summary_and_worker_budget_scales_to_eight_lanes(qtbot, tmp_path: Path):
    history = HistoricalSignalStore(tmp_path / "history.sqlite3")
    samples = [(f"Bus.Signal{i}", float(t), float((t % 17) - 8), None)
               for i in range(8) for t in range(2000)]
    history.append_many(samples)
    panel = GraphStackPanel()
    qtbot.addWidget(panel)
    panel._history = history
    panel.sync(SeriesStore(), {f"Bus.Signal{i}" for i in range(8)})
    panel._history_generation += 1
    panel.request_view_refresh()
    qtbot.wait(150)
    assert panel._viewport_refresh_timer.isActive() is False
    assert panel._history_result_cache_points <= panel._history_result_cache_limit
    worker = panel._history_worker
    panel.cancel_history_refresh()
    if worker is not None:
        worker.wait(5000)
