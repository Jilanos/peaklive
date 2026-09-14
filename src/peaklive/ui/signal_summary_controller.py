"""Coalesced refresh for the displayed-signals summary panel (item_136).

Kept as its own small mixin, rather than folded into the ingest or catalog
controllers, so both stay under the workspace's per-module line budget while
the summary's one concern - refresh at most once a second - stays easy to
find on its own.
"""

from __future__ import annotations

from PySide6.QtCore import QTimer

SIGNAL_SUMMARY_REFRESH_INTERVAL_MS = 1000


class WorkspaceSignalSummary:
    """Coalesces every summary-affecting change into at most one refresh/second."""

    def _init_signal_summary_refresh(self) -> None:
        self._signal_summary_dirty = False
        self._signal_summary_timer = QTimer(self)
        self._signal_summary_timer.setInterval(SIGNAL_SUMMARY_REFRESH_INTERVAL_MS)
        self._signal_summary_timer.timeout.connect(self._flush_signal_summary)

    def _mark_signal_summary_dirty(self) -> None:
        """Ask for a summary refresh, coalesced to at most once per second.

        The first mark after an idle period refreshes immediately, so an
        operator opening a trace or toggling a shown signal sees the summary
        update right away; any further marks inside that second are folded
        into the next tick instead of repainting the tree per sample.
        """
        self._signal_summary_dirty = True
        if not self._signal_summary_timer.isActive():
            self._flush_signal_summary()
            self._signal_summary_timer.start()

    def _flush_signal_summary(self) -> None:
        if not self._signal_summary_dirty:
            self._signal_summary_timer.stop()
            return
        self._signal_summary_dirty = False
        self.signal_summary_panel.refresh(self._series, self._selected_signal_names)
