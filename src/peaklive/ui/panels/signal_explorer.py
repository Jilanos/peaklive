"""The signal explorer: DBC-grouped navigation with search and favorites."""

from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from peaklive.analysis.dbc import DbcSignalReference
from peaklive.i18n import translate

SIGNAL_KEY_ROLE = Qt.ItemDataRole.UserRole


class SignalExplorerPanel(QWidget):
    """Groups signals by DBC and message, with search, shown, and favorites."""

    filters_changed = Signal()
    shown_changed = Signal(str, bool)
    favorite_changed = Signal(str, bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.search = QLineEdit(objectName="signalFilter")
        self.search.setAccessibleName(translate("signals.search"))
        self.search.setToolTip(translate("signals.search"))
        self.search.setPlaceholderText(translate("signals.search_placeholder"))
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.filters_changed)
        layout.addWidget(self.search)

        toggles = QHBoxLayout()
        self.shown_only = QCheckBox(translate("signals.shown_only"), objectName="shownOnlyCheckbox")
        self.shown_only.setToolTip(translate("signals.shown_only"))
        self.shown_only.setAccessibleName(translate("signals.shown_only"))
        self.shown_only.toggled.connect(self.filters_changed)
        toggles.addWidget(self.shown_only)
        self.favorites_only = QCheckBox(
            translate("signals.favorites_only"), objectName="favoritesOnlyCheckbox"
        )
        self.favorites_only.setToolTip(translate("signals.favorites_only"))
        self.favorites_only.setAccessibleName(translate("signals.favorites_only"))
        self.favorites_only.toggled.connect(self.filters_changed)
        toggles.addWidget(self.favorites_only)
        layout.addLayout(toggles)

        self.tree = QTreeWidget(objectName="signalExplorer")
        self.tree.setAccessibleName(translate("signals.explorer"))
        self.tree.setHeaderLabels(
            [
                translate("signals.column_signal"),
                translate("signals.column_shown"),
                translate("signals.column_favorite"),
            ]
        )
        self.tree.itemChanged.connect(self._item_changed)
        self.tree.itemActivated.connect(self._item_activated)
        layout.addWidget(self.tree, 1)

    @property
    def query(self) -> str:
        return self.search.text().strip().casefold()

    def filtered(
        self,
        references: Iterable[DbcSignalReference],
        shown: set[str],
        favorites: set[str],
    ) -> list[DbcSignalReference]:
        """Intersect the text search with the shown-only and favorites-only views."""
        query = self.query
        shown_only = self.shown_only.isChecked()
        favorites_only = self.favorites_only.isChecked()
        matched: list[DbcSignalReference] = []
        for reference in references:
            display_name = reference.display_name
            haystack = " ".join(
                (
                    reference.database_name,
                    reference.message_name,
                    reference.signal_name,
                    display_name,
                )
            ).casefold()
            if query and query not in haystack:
                continue
            if shown_only and display_name not in shown:
                continue
            if favorites_only and display_name not in favorites:
                continue
            matched.append(reference)
        return matched

    def refresh(
        self,
        references: Iterable[DbcSignalReference],
        shown: set[str],
        favorites: set[str],
    ) -> None:
        self.tree.blockSignals(True)
        self.tree.clear()
        matched = self.filtered(references, shown, favorites)
        if not matched:
            empty = QTreeWidgetItem([translate("signals.empty"), "", ""])
            empty.setDisabled(True)
            self.tree.addTopLevelItem(empty)
            self.tree.blockSignals(False)
            return
        dbc_items: dict[str, QTreeWidgetItem] = {}
        message_items: dict[tuple[str, str], QTreeWidgetItem] = {}
        first_signal: QTreeWidgetItem | None = None
        for reference in matched:
            dbc_item = dbc_items.get(reference.database_hash)
            if dbc_item is None:
                dbc_item = QTreeWidgetItem(
                    [f"{reference.database_name} · {reference.database_hash[:8]}", "", ""]
                )
                dbc_item.setExpanded(True)
                dbc_items[reference.database_hash] = dbc_item
                self.tree.addTopLevelItem(dbc_item)
            message_key = (reference.database_hash, reference.message_name)
            message_item = message_items.get(message_key)
            if message_item is None:
                message_item = QTreeWidgetItem(
                    dbc_item,
                    [f"{reference.message_name} · 0x{reference.frame_id:03X}", "", ""],
                )
                message_item.setExpanded(True)
                message_items[message_key] = message_item
            display_name = reference.display_name
            label = reference.signal_name + (f" [{reference.unit}]" if reference.unit else "")
            signal_item = QTreeWidgetItem(message_item, [label, "shown", "fav"])
            signal_item.setData(0, SIGNAL_KEY_ROLE, display_name)
            signal_item.setToolTip(1, translate("signals.shown_tooltip"))
            signal_item.setToolTip(2, translate("signals.favorite_tooltip"))
            signal_item.setCheckState(
                1,
                Qt.CheckState.Checked
                if display_name in shown
                else Qt.CheckState.Unchecked,
            )
            signal_item.setCheckState(
                2,
                Qt.CheckState.Checked
                if display_name in favorites
                else Qt.CheckState.Unchecked,
            )
            if first_signal is None:
                first_signal = signal_item
        if first_signal is not None:
            self.tree.setCurrentItem(first_signal)
        self.tree.blockSignals(False)

    def _item_activated(self, item: QTreeWidgetItem) -> None:
        if not item.data(0, SIGNAL_KEY_ROLE):
            return
        checked = item.checkState(1) == Qt.CheckState.Checked
        item.setCheckState(1, Qt.CheckState.Unchecked if checked else Qt.CheckState.Checked)

    def _item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        key = item.data(0, SIGNAL_KEY_ROLE)
        if not key:
            return
        if column == 1:
            self.shown_changed.emit(str(key), item.checkState(1) == Qt.CheckState.Checked)
        elif column == 2:
            self.favorite_changed.emit(str(key), item.checkState(2) == Qt.CheckState.Checked)
