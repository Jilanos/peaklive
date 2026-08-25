"""The DBC library panel: loaded databases, state, conflicts, and errors."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from peaklive.analysis import DbcCatalog
from peaklive.i18n import translate
from peaklive.ui.widgets import StateNote

DBC_HASH_ROLE = Qt.ItemDataRole.UserRole + 1


class DbcLibraryPanel(QWidget):
    """Shows every loaded DBC with its state, conflicts, and load diagnostics.

    Enable and disable update the affected row in place. Rebuilding the tree
    from inside its own `itemChanged` emission deletes the item Qt is still
    holding, which crashes the process, so the rebuild is never done there.
    """

    enabled_changed = Signal(str, bool)
    remove_requested = Signal(str)
    conflict_resolved = Signal(int, str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tree = QTreeWidget(objectName="dbcLibrary")
        self.tree.setAccessibleName(translate("dbc.library"))
        self.tree.setHeaderLabels(
            [
                translate("dbc.column_dbc"),
                translate("dbc.column_state"),
                translate("dbc.column_signals"),
            ]
        )
        self.tree.itemChanged.connect(self._item_changed)
        layout.addWidget(self.tree)

        self.note = StateNote(translate("dbc.empty"))
        layout.addWidget(self.note)

        actions = QHBoxLayout()
        self.remove_button = QPushButton(translate("dbc.remove"), objectName="removeDbcButton")
        self.remove_button.setAccessibleName(translate("dbc.remove"))
        self.remove_button.setToolTip(translate("dbc.remove_tooltip"))
        self.remove_button.clicked.connect(self._remove_current)
        actions.addWidget(self.remove_button)

        self.conflict_selector = QComboBox(objectName="dbcConflictSelector")
        self.conflict_selector.setAccessibleName(translate("dbc.conflict_accessible"))
        self.conflict_selector.setToolTip(translate("dbc.conflict_accessible"))
        self.conflict_selector.currentIndexChanged.connect(self._conflict_changed)
        actions.addWidget(self.conflict_selector, 1)
        layout.addLayout(actions)

    def refresh(self, catalog: DbcCatalog) -> None:
        """Rebuild the library rows from the catalog, outside any item signal."""
        self.tree.blockSignals(True)
        self.tree.clear()
        signal_counts = _signal_counts(catalog)
        for definition in catalog.definitions:
            enabled = catalog.is_enabled(definition.content_hash)
            item = QTreeWidgetItem(
                [
                    f"{definition.path.name} · {definition.short_hash}",
                    translate("dbc.enabled") if enabled else translate("dbc.disabled"),
                    str(signal_counts.get(definition.content_hash, 0)),
                ]
            )
            item.setData(0, DBC_HASH_ROLE, definition.content_hash)
            item.setToolTip(0, str(definition.path))
            item.setCheckState(
                0, Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked
            )
            self.tree.addTopLevelItem(item)
        self.tree.blockSignals(False)
        self._refresh_conflicts(catalog)
        self._refresh_note(catalog)

    def set_row_state(self, content_hash: str, enabled: bool) -> None:
        """Update one row's state text in place, without touching the tree shape."""
        for index in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(index)
            if item.data(0, DBC_HASH_ROLE) == content_hash:
                item.setText(1, translate("dbc.enabled") if enabled else translate("dbc.disabled"))
                return

    def show_error(self, message: str) -> None:
        self.note.show_message(message, "error")

    def _refresh_note(self, catalog: DbcCatalog) -> None:
        if not catalog.definitions:
            self.note.show_message(translate("dbc.empty"), "info")
            return
        conflicts = catalog.conflicts()
        unresolved = [
            conflict
            for conflict in conflicts
            if conflict.arbitration_id not in catalog.resolutions
        ]
        if unresolved:
            self.note.show_message(
                translate("dbc.conflict_pending").format(count=len(unresolved)), "warning"
            )
        else:
            self.note.clear_message()

    def _refresh_conflicts(self, catalog: DbcCatalog) -> None:
        self.conflict_selector.blockSignals(True)
        self.conflict_selector.clear()
        self.conflict_selector.addItem(translate("dbc.conflict_none"), None)
        for conflict in catalog.conflicts():
            for definition in conflict.candidates:
                self.conflict_selector.addItem(
                    translate("dbc.conflict_entry").format(
                        arbitration_id=conflict.arbitration_id, name=definition.path.name
                    ),
                    (conflict.arbitration_id, definition.content_hash),
                )
        self.conflict_selector.blockSignals(False)

    def _item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        if column != 0:
            return
        content_hash = item.data(0, DBC_HASH_ROLE)
        if not content_hash:
            return
        enabled = item.checkState(0) == Qt.CheckState.Checked
        item.setText(1, translate("dbc.enabled") if enabled else translate("dbc.disabled"))
        self.enabled_changed.emit(str(content_hash), enabled)

    def _remove_current(self) -> None:
        item = self.tree.currentItem()
        if item is None:
            return
        content_hash = item.data(0, DBC_HASH_ROLE)
        if content_hash:
            self.remove_requested.emit(str(content_hash))

    def _conflict_changed(self) -> None:
        data = self.conflict_selector.currentData()
        if data is None:
            return
        arbitration_id, content_hash = data
        self.conflict_resolved.emit(int(arbitration_id), str(content_hash))


def _signal_counts(catalog: DbcCatalog) -> dict[str, int]:
    counts: dict[str, int] = {}
    for definition in catalog.definitions:
        counts[definition.content_hash] = sum(
            len(message.signals) for message in definition.database.messages
        )
    return counts
