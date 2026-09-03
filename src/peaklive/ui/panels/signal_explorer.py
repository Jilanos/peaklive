"""The signal explorer: DBC-grouped navigation with search and favorites."""

from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from peaklive.analysis.dbc import DbcSignalReference
from peaklive.i18n import translate
from peaklive.ui.panels.signal_row_icons import EYE, STAR, BranchAffordanceTree, RowActionDelegate

SIGNAL_KEY_ROLE = Qt.ItemDataRole.UserRole
ACCESSIBLE_ROLE = Qt.ItemDataRole.AccessibleTextRole

#: Action columns are sized to their pictogram, not to a word, so the signal
#: name keeps the flexible width (item_026 AC1, item_054 AC3). The header
#: still names what each column does.
SHOWN_COLUMN = 1
FAVORITE_COLUMN = 2
ACTION_COLUMN_WIDTH = 28
NAME_COLUMN_MINIMUM = 160


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

        self.tree = BranchAffordanceTree(objectName="signalExplorer")
        self.tree.setAccessibleName(translate("signals.explorer"))
        self.tree.setHeaderLabels(
            [
                translate("signals.column_signal"),
                translate("signals.column_shown"),
                translate("signals.column_favorite"),
            ]
        )
        self.tree.setUniformRowHeights(True)
        self.tree.setIndentation(18)
        self._shown_delegate = RowActionDelegate(EYE, SIGNAL_KEY_ROLE, self.tree)
        self._favorite_delegate = RowActionDelegate(STAR, SIGNAL_KEY_ROLE, self.tree)
        self.tree.setItemDelegateForColumn(SHOWN_COLUMN, self._shown_delegate)
        self.tree.setItemDelegateForColumn(FAVORITE_COLUMN, self._favorite_delegate)
        header = self.tree.header()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(ACTION_COLUMN_WIDTH)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in (SHOWN_COLUMN, FAVORITE_COLUMN):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
            self.tree.setColumnWidth(column, ACTION_COLUMN_WIDTH)
        self.tree.setColumnWidth(0, NAME_COLUMN_MINIMUM)
        header_item = self.tree.headerItem()
        header_item.setToolTip(SHOWN_COLUMN, translate("signals.shown_tooltip"))
        header_item.setToolTip(FAVORITE_COLUMN, translate("signals.favorite_tooltip"))
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
            signal_item = QTreeWidgetItem(message_item, [label, "", ""])
            signal_item.setData(0, SIGNAL_KEY_ROLE, display_name)
            signal_item.setToolTip(0, display_name)
            signal_item.setCheckState(
                SHOWN_COLUMN,
                Qt.CheckState.Checked
                if display_name in shown
                else Qt.CheckState.Unchecked,
            )
            signal_item.setCheckState(
                FAVORITE_COLUMN,
                Qt.CheckState.Checked
                if display_name in favorites
                else Qt.CheckState.Unchecked,
            )
            self._describe(signal_item)
            if first_signal is None:
                first_signal = signal_item
        if first_signal is not None:
            self.tree.setCurrentItem(first_signal)
        self.tree.blockSignals(False)

    def _describe(self, item: QTreeWidgetItem) -> None:
        """Carry the action and its current state without printing it in the row.

        A screen reader and a hovering operator both need to know what the
        checkbox does and where it stands; only the row itself has to stay
        free of the repeated words.
        """
        signal = str(item.data(0, SIGNAL_KEY_ROLE) or "")
        # Writing the description back is itself an item change; without this
        # the toggle signal would be emitted twice per click.
        blocked = self.tree.blockSignals(True)
        for column, key in ((SHOWN_COLUMN, "shown_state"), (FAVORITE_COLUMN, "favorite_state")):
            state = (
                "signals.state_on"
                if item.checkState(column) == Qt.CheckState.Checked
                else "signals.state_off"
            )
            label = translate(f"signals.{key}").format(
                signal=signal, state=translate(state)
            )
            item.setToolTip(column, label)
            item.setData(column, ACCESSIBLE_ROLE, label)
        self.tree.blockSignals(blocked)

    def _item_activated(self, item: QTreeWidgetItem) -> None:
        if not item.data(0, SIGNAL_KEY_ROLE):
            return
        checked = item.checkState(SHOWN_COLUMN) == Qt.CheckState.Checked
        item.setCheckState(
            SHOWN_COLUMN, Qt.CheckState.Unchecked if checked else Qt.CheckState.Checked
        )

    def _item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        key = item.data(0, SIGNAL_KEY_ROLE)
        if not key:
            return
        self._describe(item)
        if column == SHOWN_COLUMN:
            self.shown_changed.emit(
                str(key), item.checkState(SHOWN_COLUMN) == Qt.CheckState.Checked
            )
        elif column == FAVORITE_COLUMN:
            self.favorite_changed.emit(
                str(key), item.checkState(FAVORITE_COLUMN) == Qt.CheckState.Checked
            )
