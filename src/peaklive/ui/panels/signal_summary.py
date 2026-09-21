"""The displayed-signals summary: currently shown signals and their latest value.

Replaces the DBC library tree that used to sit above the signal explorer
(item_136): DBC activation and management now live entirely in the DBC menu,
and this panel leads Signals with what the operator actually cares about while
watching a live session - which signals are on screen right now, and what they
last read.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from peaklive.analysis import SeriesStore
from peaklive.analysis.dbc import signal_display_title
from peaklive.i18n import translate

SIGNAL_SUMMARY_KEY_ROLE = Qt.ItemDataRole.UserRole + 1


class SignalSummaryPanel(QWidget):
    """A compact, deterministically ordered table of shown signals and values."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._store: SeriesStore | None = None
        self._shown: set[str] = set()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tree = QTreeWidget(objectName="signalSummary")
        self.tree.setAccessibleName(translate("signals.summary_accessible"))
        self.tree.setRootIsDecorated(False)
        self.tree.setHeaderLabels(
            [
                translate("signals.summary_column_signal"),
                translate("signals.summary_column_value"),
                translate("signals.summary_column_unit"),
            ]
        )
        layout.addWidget(self.tree)

    def refresh(self, store: SeriesStore | None, shown_signal_names: set[str]) -> None:
        """Rebuild the summary rows from the currently shown signals.

        Ordered by display title so the row order stays stable regardless of
        the order signals were selected in, matching the deterministic
        ordering the backlog calls for.
        """
        self._store = store
        self._shown = set(shown_signal_names)
        self.tree.clear()
        for name in sorted(shown_signal_names, key=signal_display_title):
            title = signal_display_title(name)
            series = store.series(name) if store is not None else None
            if series is not None and len(series):
                value_text = _format_value(series.values[-1])
                unit = series.unit or ""
            else:
                value_text = translate("signals.summary_unavailable")
                unit = ""
            item = QTreeWidgetItem([title, value_text, unit])
            item.setData(0, SIGNAL_SUMMARY_KEY_ROLE, name)
            self.tree.addTopLevelItem(item)


    def retranslate(self) -> None:
        self.tree.setAccessibleName(translate("signals.summary_accessible"))
        self.tree.setHeaderLabels(
            [
                translate("signals.summary_column_signal"),
                translate("signals.summary_column_value"),
                translate("signals.summary_column_unit"),
            ]
        )
        self.refresh(self._store, self._shown)


def _format_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)
