"""Tracks worker threads the shell has stopped listening to but not destroyed.

Qt aborts the process if a running `QThread` is destroyed, so a worker whose
window has moved on (a stale generation, a shutdown budget that ran out) has
to keep living somewhere until it actually lands. This module is that
somewhere, plus the one further, bounded chance it gets at process exit.
"""

from __future__ import annotations

from time import monotonic

from PySide6.QtCore import QThread

from peaklive.diagnostics import logger

#: How long the exit-time drain gives every still-abandoned worker together,
#: so a stuck driver cannot hold the process open forever.
EXIT_DRAIN_TIMEOUT_MS = 5_000

#: Worker threads the shell has stopped listening to but that are still
#: running. Membership here is the only reference keeping one alive; each
#: worker removes itself when it finally lands.
_ABANDONED_WORKERS: set[QThread] = set()


def abandon_worker(worker: QThread | None) -> None:
    """Stop caring about a worker's result without destroying it mid-flight.

    The signal is connected before the finished check, not after: a worker
    that lands between the two would otherwise never fire the connected
    callback and would sit in the set forever, looking abandoned-but-active
    when it has actually already completed.
    """
    if worker is None:
        return
    _ABANDONED_WORKERS.add(worker)
    worker.finished.connect(lambda: _ABANDONED_WORKERS.discard(worker))
    if worker.isFinished():
        _ABANDONED_WORKERS.discard(worker)


def _worker_identity(worker: QThread) -> str:
    """A short, worker-type-appropriate description for exit diagnostics."""
    bits = [type(worker).__name__]
    generation = getattr(worker, "generation", None)
    if generation is not None:
        bits.append(f"generation={generation}")
    path = getattr(worker, "_path", None)
    if path is not None:
        bits.append(f"path={path}")
    return " ".join(bits)


def drain_abandoned_workers_at_exit(timeout_ms: int = EXIT_DRAIN_TIMEOUT_MS) -> None:
    """Give every still-abandoned worker one last, bounded chance to land.

    Called once as the application is about to quit - after every window's
    own closeEvent budget has already run out - so a worker still stuck at
    that point gets one shared, explicit final budget rather than being left
    for the interpreter to tear down mid-run, which aborts the process.
    Whatever is still running once the budget is spent is logged with its
    identity as evidence; it is deliberately never force-destroyed here.
    """
    deadline = monotonic() + timeout_ms / 1000
    for worker in list(_ABANDONED_WORKERS):
        if not worker.isRunning():
            continue
        remaining_ms = max(0, int((deadline - monotonic()) * 1000))
        worker.wait(remaining_ms)
        if worker.isRunning():
            logger().warning("worker still running at exit: %s", _worker_identity(worker))
