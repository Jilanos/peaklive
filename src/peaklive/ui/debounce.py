"""A minimal reset-on-each-call debounce for high-frequency UI input.

Typing in a filter box, dragging a graph cursor, or dragging a splitter each
fire far more UI signals than the expensive work behind them - a full trace
recompute, a signal-tree rebuild, a profile write - should ever run for. A
`Debouncer` coalesces a burst of triggers into exactly one call, once the
burst goes quiet for `delay_ms`.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QTimer

#: Coalescing window for interactive recomputation (filters, signal search,
#: cursor-drag measurements): short enough that typing still feels immediate.
INTERACTIVE_DEBOUNCE_MS = 120

#: Coalescing window for profile persistence: a disk write is heavier than a
#: recompute, so bursts get a little more room to settle before it runs.
SAVE_DEBOUNCE_MS = 300


class Debouncer(QObject):
    """Runs `callback` at most once per burst of `trigger()` calls."""

    def __init__(
        self, delay_ms: int, callback: Callable[[], None], parent: QObject | None = None
    ) -> None:
        super().__init__(parent)
        self._callback = callback
        self._pending = False
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(delay_ms)
        self._timer.timeout.connect(self._fire)

    def trigger(self) -> None:
        """Ask for `callback` to run after `delay_ms` of quiet, restarting the wait."""
        self._pending = True
        self._timer.start()

    def flush(self) -> None:
        """Run a pending callback immediately instead of waiting out the timer.

        Safe to call unconditionally: a no-op when nothing is pending.
        """
        if not self._pending:
            return
        self._timer.stop()
        self._fire()

    def _fire(self) -> None:
        self._pending = False
        self._callback()
