"""item_065 coverage: abandoned workers are drained safely, not leaked or crashed.

`abandon_worker` keeps a still-running QThread referenced so Qt never has to
destroy it mid-run; the gaps this closes are a race that can leave an
already-completed worker stuck in the set forever, and the total absence of
any final, bounded, evidenced drain before the interpreter tears the process
down.
"""

from __future__ import annotations

from peaklive.ui.worker_lifecycle import (
    _ABANDONED_WORKERS,
    abandon_worker,
    drain_abandoned_workers_at_exit,
)


class _FakeSignal:
    """A minimal stand-in for a Qt signal: records the connected callback."""

    def __init__(self) -> None:
        self._callback = None

    def connect(self, callback) -> None:
        self._callback = callback

    def emit(self) -> None:
        if self._callback is not None:
            self._callback()


class _FakeWorker:
    def __init__(self, *, running: bool) -> None:
        self._running = running
        self.finished = _FakeSignal()

    def isRunning(self) -> bool:  # noqa: N802 - matches QThread's own casing
        return self._running

    def isFinished(self) -> bool:  # noqa: N802 - matches QThread's own casing
        return not self._running

    def wait(self, timeout_ms: int) -> bool:
        return not self._running


class _RaceySignal:
    """Simulates a worker completing in the gap before `connect()` lands."""

    def __init__(self, worker: _RaceyWorker) -> None:
        self._worker = worker

    def connect(self, callback) -> None:
        # The real finished signal already fired before this subscription
        # existed, so it can never invoke `callback` - the worker only looks
        # done via `isFinished()` from here on, exactly as it would in the
        # real race this closes.
        self._worker._running = False


class _RaceyWorker(_FakeWorker):
    def __init__(self) -> None:
        super().__init__(running=True)
        self.finished = _RaceySignal(self)  # type: ignore[assignment]


def setup_function() -> None:
    _ABANDONED_WORKERS.clear()


def teardown_function() -> None:
    _ABANDONED_WORKERS.clear()


def test_abandon_worker_tracks_a_running_worker_until_it_finishes():
    worker = _FakeWorker(running=True)

    abandon_worker(worker)
    assert worker in _ABANDONED_WORKERS

    worker._running = False
    worker.finished.emit()
    assert worker not in _ABANDONED_WORKERS


def test_abandon_worker_never_tracks_an_already_finished_worker():
    worker = _FakeWorker(running=False)

    abandon_worker(worker)

    assert worker not in _ABANDONED_WORKERS


def test_abandon_worker_closes_the_race_where_completion_lands_during_subscription():
    """A worker landing between being added and its signal connecting must not stick."""
    worker = _RaceyWorker()

    abandon_worker(worker)

    assert worker not in _ABANDONED_WORKERS


def test_drain_removes_a_worker_that_finishes_within_the_budget():
    worker = _FakeWorker(running=True)
    _ABANDONED_WORKERS.add(worker)

    def landing_wait(timeout_ms: int) -> bool:
        worker._running = False
        return True

    worker.wait = landing_wait  # type: ignore[method-assign]

    drain_abandoned_workers_at_exit(timeout_ms=1_000)

    assert not worker.isRunning()


class _FakeLogger:
    def __init__(self, calls: list) -> None:
        self._calls = calls

    def warning(self, *args, **kwargs) -> None:
        self._calls.append(args)


def test_drain_logs_and_leaves_untouched_a_worker_still_running_past_the_budget(
    monkeypatch,
):
    worker = _FakeWorker(running=True)
    worker.wait = lambda timeout_ms: False  # type: ignore[method-assign]
    _ABANDONED_WORKERS.add(worker)
    warnings: list = []
    monkeypatch.setattr(
        "peaklive.ui.worker_lifecycle.logger", lambda: _FakeLogger(warnings)
    )

    drain_abandoned_workers_at_exit(timeout_ms=1)

    assert worker.isRunning()
    assert worker in _ABANDONED_WORKERS
    assert len(warnings) == 1
    assert "FakeWorker" in warnings[0][1]


def test_drain_never_calls_wait_on_a_worker_that_already_finished():
    worker = _FakeWorker(running=False)

    def fail_if_called(timeout_ms: int) -> bool:
        raise AssertionError("wait() must not be called on a worker that already landed")

    worker.wait = fail_if_called  # type: ignore[method-assign]
    _ABANDONED_WORKERS.add(worker)

    drain_abandoned_workers_at_exit(timeout_ms=1_000)
