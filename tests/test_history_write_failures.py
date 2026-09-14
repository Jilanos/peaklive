"""item_132: a SQLite persistence failure must be contained, not escape a Qt slot.

Before this fix, `HistoricalSignalStore.append_many` raised straight out of
the Qt slot that drains a replay batch (`_drain_replay_batch`): the exception
propagated past `worker.batch_rendered()`, leaking the batch's permit,
leaving the presentation timer/queue in an inconsistent state, and never
reporting the session as failed. These tests reproduce the audit's
`PRAGMA query_only=ON` repro plus a genuinely locked database, and prove the
failure is now contained to one explicit terminal state per session.
"""

from __future__ import annotations

import sqlite3

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis.benchmark import CaptureProfile, synthetic_dbc, write_synthetic_capture
from peaklive.domain import CanFrame
from peaklive.services.profiles import ProfileStore
from peaklive.services.replay_worker import ReplayWorker
from peaklive.ui import MainWindow


def _window(qtbot, tmp_path) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    dbc = tmp_path / "synthetic.dbc"
    dbc.write_text(synthetic_dbc(1), encoding="utf-8")
    window._load_dbc_path(dbc)
    window._selected_signal_names = set(window._catalog.signal_names()[:1])
    return window


def _queue_one_owned_batch(window: MainWindow, worker: ReplayWorker, generation: int) -> None:
    """Inject one pending batch as if `ReplayWorker._dispatch` had sent it."""
    worker._held_permits = 1
    window._replay_generation = generation
    window._pending_replay_batches = [(generation, worker, [CanFrame(0.0, 0x300, bytes(8))])]


def test_a_readonly_failure_does_not_escape_the_drain_slot_and_retires_the_permit_once(
    qtbot, tmp_path
):
    window = _window(qtbot, tmp_path)
    worker = ReplayWorker(tmp_path / "dummy.asc")
    _queue_one_owned_batch(window, worker, generation=7)
    window._history._connection.execute("PRAGMA query_only=ON")

    window._drain_replay_batch()  # must not raise

    assert worker.pending_batch_count == 0
    assert window._pending_replay_batches == []
    assert not window._replay_presentation_timer.isActive()


def test_a_readonly_failure_is_reported_as_one_explicit_terminal_state_not_success(
    qtbot, tmp_path
):
    window = _window(qtbot, tmp_path)
    worker = ReplayWorker(tmp_path / "dummy.asc")
    _queue_one_owned_batch(window, worker, generation=3)
    window._history._connection.execute("PRAGMA query_only=ON")

    window._drain_replay_batch()

    assert window._replay_worker is None
    assert "complete" not in window.status.currentMessage().lower()
    assert window._replay_failed_generation == 3
    assert window._history_failed
    assert window._history_failure_message


def test_after_a_failure_further_batches_do_not_retry_persistence_or_duplicate_facts(
    qtbot, tmp_path
):
    window = _window(qtbot, tmp_path)
    window._history._connection.execute("PRAGMA query_only=ON")

    # First batch trips the failure; frame/fact projection still records it.
    window._ingest_frames([CanFrame(0.0, 0x300, bytes(8))], coalesce=True)
    assert window._history_failed
    assert len(window._trace) == 1

    # Toggle the fault off: if the guard were absent, retrying would now
    # silently succeed and mask that this session's coverage is incomplete.
    window._history._connection.execute("PRAGMA query_only=OFF")
    window._ingest_frames([CanFrame(0.001, 0x300, bytes(8))], coalesce=True)

    assert len(window._trace) == 2  # trace/facts keep growing...
    assert window._history.bounds() is None  # ...but no sample was ever persisted
    assert not window._historical_view_ready


def test_reopening_after_the_fault_clears_succeeds_from_a_fresh_store(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._history._connection.execute("PRAGMA query_only=ON")
    window._ingest_frames([CanFrame(0.0, 0x300, bytes(8))], coalesce=True)
    assert window._history_failed

    window._history._connection.execute("PRAGMA query_only=OFF")
    capture = write_synthetic_capture(tmp_path / "reopen.asc", CaptureProfile("reopen", 200))
    window._open_trace(capture)
    qtbot.waitUntil(lambda: window._replay_worker is None, timeout=15_000)

    assert window.status.currentMessage() == "Trace replay complete"
    assert not window._history_failed
    assert window._history.bounds() is not None
    assert len(window._trace) == 200


def test_a_simulated_disk_full_commit_failure_is_contained_the_same_way(
    qtbot, tmp_path, monkeypatch
):
    window = _window(qtbot, tmp_path)

    def _disk_full(*_args, **_kwargs):
        raise sqlite3.OperationalError("database or disk is full")

    monkeypatch.setattr(window._history, "append_many", _disk_full)

    window._ingest_frames([CanFrame(0.0, 0x300, bytes(8))], coalesce=True)  # must not raise

    assert window._history_failed
    assert "disk is full" in (window._history_failure_message or "")
    assert len(window._trace) == 1


def test_a_genuinely_locked_database_is_contained_the_same_way(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    blocker = sqlite3.connect(window._history.path)
    blocker.execute("BEGIN EXCLUSIVE")
    try:
        worker = ReplayWorker(tmp_path / "dummy.asc")
        _queue_one_owned_batch(window, worker, generation=1)

        window._drain_replay_batch()  # must not raise sqlite3.OperationalError

        assert worker.pending_batch_count == 0
        assert window._history_failed
        assert window._replay_worker is None
    finally:
        blocker.rollback()
        blocker.close()
