"""item_132/item_133: a historical persistence failure must be contained.

Before item_132, `HistoricalSignalStore.append_many` raised straight out of
the Qt slot that drains a replay batch: the exception propagated past
`worker.batch_rendered()`, leaking the batch's permit and never reporting
the session as failed. item_133 then moved the actual write onto a
background `HistoryWriter` thread, so a failure can now be discovered either
synchronously (a full write queue that never drains) or asynchronously (the
writer's own `write_failed` signal, arriving after `submit()` already
returned). These tests cover both, and prove the outcome converges on one
explicit terminal state either way.
"""

from __future__ import annotations

import sqlite3

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis.benchmark import CaptureProfile, synthetic_dbc, write_synthetic_capture
from peaklive.analysis.history import HistoricalSignalStore
from peaklive.domain import CanFrame
from peaklive.services.history_writer import HistoryWriter
from peaklive.services.profiles import ProfileStore
from peaklive.services.replay_worker import ReplayWorker
from peaklive.ui import MainWindow
from peaklive.ui.worker_lifecycle import abandon_worker


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
    window._replay_worker = worker
    window._replay_generation = generation
    window._pending_replay_batches = [(generation, worker, [CanFrame(0.0, 0x300, bytes(8))])]


def _install_readonly_writer(window: MainWindow, qtbot) -> None:
    """Replace the session's writer with one whose own connection is read-only.

    `PRAGMA query_only` is per-connection, so it must be set on the writer
    thread's own connection from that same thread - `on_ready` is the only
    safe way to reach it (sqlite3 forbids cross-thread connection use).
    """
    old = window._history_writer
    if old is not None:
        old.request_stop()
        abandon_worker(old)
    writer = HistoryWriter(
        window._history.path,
        on_ready=lambda store: store._connection.execute("PRAGMA query_only=ON"),
    )
    writer.write_failed.connect(window._fail_history)
    writer.settled.connect(window._history_settled)
    window._history_writer = writer
    writer.start()
    qtbot.waitUntil(lambda: writer.store is not None, timeout=5_000)


def test_a_readonly_failure_does_not_escape_the_drain_slot_and_retires_the_permit_once(
    qtbot, tmp_path
):
    window = _window(qtbot, tmp_path)
    _install_readonly_writer(window, qtbot)
    worker = ReplayWorker(tmp_path / "dummy.asc")
    _queue_one_owned_batch(window, worker, generation=7)

    window._drain_replay_batch()  # must not raise

    assert worker.pending_batch_count == 0
    qtbot.waitUntil(lambda: window._history_failed, timeout=5_000)
    assert window._pending_replay_batches == []
    assert not window._replay_presentation_timer.isActive()


def test_a_readonly_failure_is_reported_as_one_explicit_terminal_state_not_success(
    qtbot, tmp_path
):
    window = _window(qtbot, tmp_path)
    _install_readonly_writer(window, qtbot)
    worker = ReplayWorker(tmp_path / "dummy.asc")
    _queue_one_owned_batch(window, worker, generation=3)

    window._drain_replay_batch()

    qtbot.waitUntil(lambda: window._history_failed, timeout=5_000)
    assert window._replay_worker is None
    assert "complete" not in window.status.currentMessage().lower()
    assert window._replay_failed_generation == 3
    assert window._history_failure_message


def test_after_a_failure_further_batches_do_not_retry_persistence_or_duplicate_facts(
    qtbot, tmp_path
):
    window = _window(qtbot, tmp_path)
    _install_readonly_writer(window, qtbot)

    # First batch trips the failure; frame/fact projection still records it.
    window._ingest_frames([CanFrame(0.0, 0x300, bytes(8))], coalesce=True)
    qtbot.waitUntil(lambda: window._history_failed, timeout=5_000)
    assert len(window._trace) == 1

    # The writer stays failed even though nothing about its connection
    # changed: if the no-retry guard were absent, this second batch would
    # submit() again and could mask that this session's coverage is
    # incomplete.
    window._ingest_frames([CanFrame(0.001, 0x300, bytes(8))], coalesce=True)

    assert len(window._trace) == 2  # trace/facts keep growing...
    assert window._history.bounds() is None  # ...but no sample was ever persisted
    assert not window._historical_view_ready


def test_reopening_after_the_fault_clears_succeeds_from_a_fresh_store(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    _install_readonly_writer(window, qtbot)
    window._ingest_frames([CanFrame(0.0, 0x300, bytes(8))], coalesce=True)
    qtbot.waitUntil(lambda: window._history_failed, timeout=5_000)

    # Reopening allocates a brand-new store and writer (see
    # _reset_history_store): the old, poisoned writer's connection is simply
    # abandoned rather than reused, so its stuck PRAGMA cannot follow here.
    capture = write_synthetic_capture(tmp_path / "reopen.asc", CaptureProfile("reopen", 200))
    window._open_trace(capture)
    qtbot.waitUntil(lambda: window._replay_worker is None, timeout=15_000)
    qtbot.waitUntil(lambda: window._history.bounds() is not None, timeout=15_000)

    assert window.status.currentMessage() == "Trace replay complete"
    assert not window._history_failed
    assert len(window._trace) == 200


def test_a_simulated_disk_full_commit_failure_is_contained_the_same_way(
    qtbot, tmp_path, monkeypatch
):
    window = _window(qtbot, tmp_path)
    qtbot.waitUntil(lambda: window._history_writer.store is not None, timeout=5_000)

    def _disk_full(*_args, **_kwargs):
        raise sqlite3.OperationalError("database or disk is full")

    # Patched at the class level: the write happens on the background
    # writer's own HistoricalSignalStore instance, not window._history.
    monkeypatch.setattr(HistoricalSignalStore, "append_many", _disk_full)

    window._ingest_frames([CanFrame(0.0, 0x300, bytes(8))], coalesce=True)  # must not raise

    qtbot.waitUntil(lambda: window._history_failed, timeout=5_000)
    assert "disk is full" in (window._history_failure_message or "")
    assert len(window._trace) == 1


def test_a_genuinely_locked_database_is_contained_the_same_way(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    qtbot.waitUntil(lambda: window._history_writer.store is not None, timeout=5_000)
    # isolation_level=None (autocommit) so this BEGIN EXCLUSIVE takes the
    # lock immediately rather than being deferred by sqlite3's own implicit
    # transaction handling.
    blocker = sqlite3.connect(window._history.path, isolation_level=None)
    blocker.execute("BEGIN EXCLUSIVE")
    try:
        worker = ReplayWorker(tmp_path / "dummy.asc")
        _queue_one_owned_batch(window, worker, generation=1)

        window._drain_replay_batch()  # must not raise sqlite3.OperationalError

        assert worker.pending_batch_count == 0
        qtbot.waitUntil(lambda: window._history_failed, timeout=5_000)
        assert window._replay_worker is None
    finally:
        blocker.execute("ROLLBACK")
        blocker.close()
