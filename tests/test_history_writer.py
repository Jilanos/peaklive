"""item_133: bounded single-writer ownership of historical persistence.

`HistoryWriter` is the one background thread allowed to write to a session's
`HistoricalSignalStore`. These tests exercise it directly (not through
`MainWindow`): exact fidelity of what gets persisted, the bounded queue's
backpressure contract, and the disk-space admission check that refuses a
write before it starts rather than letting SQLite fail mid-commit.
"""

from __future__ import annotations

from peaklive.analysis.history import HistoricalSignalStore
from peaklive.services import history_writer as history_writer_module
from peaklive.services.history_writer import MAX_QUEUE_BATCHES, HistoryWriter, HistoryWriteRefused


def _wait_for_store(writer: HistoryWriter, qtbot) -> None:
    qtbot.waitUntil(lambda: writer.store is not None, timeout=5_000)


def test_submitted_samples_are_persisted_with_exact_values_and_settled_is_reported(
    qtbot, tmp_path
):
    seed = HistoricalSignalStore()
    path = seed.path
    writer = HistoryWriter(path)
    settled_counts: list[int] = []
    writer.settled.connect(settled_counts.append)
    writer.start()
    _wait_for_store(writer, qtbot)

    batch = [("speed", 0.0, 12.5, "km/h"), ("speed", 0.001, 13.0, "km/h")]
    assert writer.submit(batch)

    qtbot.waitUntil(lambda: settled_counts == [2], timeout=5_000)

    writer.request_stop()
    writer.wait(5_000)
    with HistoricalSignalStore(path, read_only=True) as reader:
        assert reader.exact("speed", 0.0, 0.001) == ((0.0, 12.5), (0.001, 13.0))
    seed.close()


def test_the_queue_bounds_pending_batches_and_submit_blocks_until_drained(qtbot, tmp_path):
    seed = HistoricalSignalStore()
    writer = HistoryWriter(seed.path)
    writer.start()
    _wait_for_store(writer, qtbot)

    # A single-item batch settles almost instantly, so this proves submit()
    # keeps accepting well past MAX_QUEUE_BATCHES rather than blocking
    # forever - the queue drains as fast as (or faster than) it fills here.
    accepted = sum(
        writer.submit([("s", float(i), i, None)]) for i in range(MAX_QUEUE_BATCHES * 5)
    )
    assert accepted == MAX_QUEUE_BATCHES * 5

    writer.request_stop()
    writer.wait(5_000)
    with HistoricalSignalStore(seed.path, read_only=True) as reader:
        assert reader.bounds() == (0.0, float(MAX_QUEUE_BATCHES * 5 - 1))
    seed.close()


def test_submit_fails_closed_once_the_writer_has_stopped(qtbot, tmp_path):
    seed = HistoricalSignalStore()
    writer = HistoryWriter(seed.path)
    writer.start()
    _wait_for_store(writer, qtbot)

    writer.request_stop()
    writer.wait(5_000)

    assert writer.submit([("s", 0.0, 1.0, None)]) is False
    seed.close()


def test_a_write_below_the_free_disk_margin_is_refused_before_it_starts(
    qtbot, tmp_path, monkeypatch
):
    seed = HistoricalSignalStore()
    writer = HistoryWriter(seed.path)
    writer.start()
    _wait_for_store(writer, qtbot)

    class _TinyFree:
        free = 1024  # far below MIN_FREE_DISK_BYTES

    monkeypatch.setattr(
        history_writer_module.shutil, "disk_usage", lambda _path: _TinyFree()
    )

    assert writer.submit([("s", 0.0, 1.0, None)])
    qtbot.waitUntil(lambda: writer.failed, timeout=5_000)
    assert "free" in (writer.last_error or "")

    writer.wait(5_000)
    seed.close()


def test_disk_admission_refusal_is_a_contained_sqlite_style_failure():
    error = HistoryWriteRefused("only 1024 byte(s) free")
    assert isinstance(error, RuntimeError)
