"""Historical readers must survive cancellation and session file teardown."""

import sqlite3
import sys
from threading import Event

import pytest

from peaklive.analysis.history import HistoricalSignalStore
from peaklive.services import history_worker
from peaklive.services.history_worker import HistoryViewportWorker


@pytest.mark.parametrize("count", [20, 100])
def test_viewport_reader_never_writes_to_the_session_cache(tmp_path, count):
    # Cover both precomputed summaries and the raw-sample fallback.
    with HistoricalSignalStore(tmp_path / "history.sqlite3") as owner:
        owner.append_many(("speed", float(i), i, None) for i in range(count))
        with HistoricalSignalStore(owner.path, read_only=True) as reader:
            points = reader.overview("speed", 0, count - 1, max_points=16)
            assert points[0] == (0, 0)
            assert points[-1] == (count - 1, count - 1)
            assert reader._connection.total_changes == 0
        assert owner._connection.execute("SELECT COUNT(*) FROM overview_cache").fetchone() == (0,)


def test_a_reader_does_not_recreate_a_deleted_session(tmp_path):
    path = tmp_path / "removed.sqlite3"
    with pytest.raises(sqlite3.OperationalError):
        HistoricalSignalStore(path, read_only=True)
    assert not path.exists()


def test_worker_reports_an_unavailable_database_without_escaping_qt(qtbot, tmp_path):
    worker = HistoryViewportWorker(tmp_path / "missing.sqlite3", ("speed",), (0, 9), (0, 9), 7)
    completed = []
    failures = []
    worker.completed.connect(lambda *args: completed.append(args))
    worker.failed.connect(lambda *args: failures.append(args))
    with qtbot.waitSignal(worker.finished, timeout=5_000):
        worker.start()
    qtbot.waitUntil(lambda: bool(failures))
    assert completed == []
    assert failures[0][1] == 7
    assert not worker._path.exists()


def test_cancelled_worker_finishes_after_its_session_owner_closes(qtbot, monkeypatch):
    owner = HistoricalSignalStore()
    owner.append_many(("speed", float(i), i, None) for i in range(100))
    entered, release = Event(), Event()
    original = history_worker.historical_points

    def paused_read(*args):
        entered.set()
        if not release.wait(5):
            raise TimeoutError("Test did not release the historical reader")
        return original(*args)

    monkeypatch.setattr(history_worker, "historical_points", paused_read)
    worker = HistoryViewportWorker(owner.path, ("speed",), (0, 99), (0, 99), 1)
    results, failures = [], []
    worker.completed.connect(lambda *args: results.append(args))
    worker.failed.connect(lambda *args: failures.append(args))
    worker.start()
    try:
        qtbot.waitUntil(entered.is_set, timeout=5_000)
        worker.request_cancel()
        owner.close()
        if sys.platform != "win32":
            assert not owner.path.exists()
        with qtbot.waitSignal(worker.finished, timeout=5_000):
            release.set()
        assert results == failures == []
    finally:
        release.set()
        worker.wait(5_000)
        owner.close()
