"""The one-line Graphs/Trace header: view, fit, lifecycle, and cursor actions.

The controls it lays out are still owned and wired by their original panels
(`GraphControlsBar`, `AcquisitionBar`) - this bar only reparents their widgets
into one row, the same pattern the workspace mode selector already used, so
no control gains a second, drifting copy of itself.

Width policy (request AC8): the row never silently clips a control. Controls
registered as required (A/B/delta, Start/Stop, the primary fit action, cursor
placement) always stay directly on the row. Controls registered as
deferrable (the mode selector, Follow live, the secondary Y-only fit, the
measurement-visibility toggle, the empty-state note) move into an overflow
menu, in reverse-priority order, only once the row is too narrow to show
everything at once - so a side-panel-pressured window degrades to an
accessible "more commands" button instead of clipping a timestamp.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QMenu,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from peaklive.i18n import translate


def _width_demand(widget: QWidget) -> int:
    """The width a control actually needs, not just its capped preferred hint.

    `ElidingLabel.sizeHint()` (used by the cursor summary) caps itself at a
    small preferred width and instead forces a real minimum through
    `setMinimumWidth` once it knows its text - a plain `sizeHint()` read
    would under-count exactly the readout AC8 must not clip.
    """
    return max(widget.sizeHint().width(), widget.minimumWidth())


class WorkspaceHeaderBar(QWidget):
    """A single, never-wrapping row above the graph/trace/report stack."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, objectName="workspaceHeaderBar")
        self.row = QHBoxLayout(self)
        self.row.setContentsMargins(0, 0, 0, 0)
        self.row.setSpacing(1)
        self._required: list[QWidget] = []
        # Least-important first: this is the order controls are pushed into
        # the overflow menu when the row runs out of width.
        self._deferrable: list[QWidget] = []
        self._overflow_panel = QWidget(objectName="workspaceHeaderOverflowPanel")
        self._overflow_panel_layout = QVBoxLayout(self._overflow_panel)
        self._overflow_panel_layout.setContentsMargins(6, 6, 6, 6)
        self._overflow_menu = QMenu(self)
        # A single QWidgetAction hosts the panel: deferred controls are
        # reparented into `self._overflow_panel`'s layout, so the very same
        # live widgets (not copies) move between the row and the menu.
        widget_action = QWidgetAction(self._overflow_menu)
        widget_action.setDefaultWidget(self._overflow_panel)
        self._overflow_menu.addAction(widget_action)
        self._overflow_button = QToolButton(self, objectName="workspaceHeaderOverflow")
        self._overflow_button.setText("⋯")
        self._overflow_button.setAccessibleName(translate("workspace.header_overflow"))
        self._overflow_button.setToolTip(translate("workspace.header_overflow"))
        self._overflow_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._overflow_button.setMenu(self._overflow_menu)
        self._overflow_button.setVisible(False)
        self.row.addWidget(self._overflow_button)
        self._refreshing_overflow = False

    def add(self, widget: QWidget, *, deferrable: bool = False) -> QWidget:
        """Register a control on the row.

        `deferrable=True` marks a lower-frequency control that may move into
        the overflow menu under width pressure; everything else is required
        and always stays directly visible.
        """
        self.row.insertWidget(self.row.count() - 1, widget)
        (self._deferrable if deferrable else self._required).append(widget)
        return widget

    def refresh_overflow(self) -> None:
        """Recompute which deferrable controls fit, moving the rest to the menu.

        Called on resize and whenever a required control's own width demand
        changes (e.g. the cursor summary growing to fit a longer timestamp),
        since that can shrink the room left for deferrable controls without
        the header itself being resized.

        `widget.show()`/reparenting inside `_recompute_overflow` trigger
        their own layout and resize events, which would otherwise re-enter
        this method mid-computation with stale widths. A call arriving while
        already refreshing is folded into one more pass after the current
        one settles, instead of being dropped - dropping it can leave a
        control stranded in the overflow menu even once there is genuinely
        room for it again.
        """
        if self._refreshing_overflow:
            self._overflow_dirty = True
            return
        self._refreshing_overflow = True
        try:
            self._overflow_dirty = True
            passes = 0
            while self._overflow_dirty and passes < 4:
                self._overflow_dirty = False
                passes += 1
                self._recompute_overflow()
        finally:
            self._refreshing_overflow = False

    def _available_width(self) -> int:
        """The row's real width budget, not just this widget's current size.

        `self.width()` on its own is circular: it mirrors whatever this
        widget currently asks for (its own sizeHint), so once a control is
        deferred the row shrinks to match the remaining content and the very
        same comparison keeps finding "not enough room" forever, even after
        the window has plenty of space again. The host title row's own
        width, driven entirely by the outer splitter and independent of what
        this bar shows, is the real constraint; only the title and the
        collapse toggle's own space needs subtracting from it.
        """
        parent = self.parentWidget()
        header_layout = getattr(parent, "header_layout", None)
        if parent is None or header_layout is None or parent.width() <= 0:
            return self.width()
        reserved = 0
        for index in range(header_layout.count()):
            sibling = header_layout.itemAt(index).widget()
            if sibling is not None and sibling is not self:
                reserved += sibling.sizeHint().width()
        reserved += header_layout.spacing() * max(header_layout.count() - 1, 0)
        return max(parent.width() - reserved, 0)

    def _recompute_overflow(self) -> None:
        available = self._available_width()
        if available <= 0:
            return
        for widget in self._deferrable:
            if widget.parent() is not self:
                self.row.insertWidget(self.row.count() - 1, widget)
                # Reparenting always leaves Qt's own hidden flag set; this
                # widget is meant to be shown once it is back on the row.
                widget.show()
        spacing = self.row.spacing()
        # A control that is already explicitly hidden (e.g. the empty-state
        # note outside the empty state) claims no row width and never needs
        # to be moved into overflow - only widgets actually competing for
        # space count towards the budget.
        required = [widget for widget in self._required if not widget.isHidden()]
        deferrable = [widget for widget in self._deferrable if not widget.isHidden()]
        required_width = sum(_width_demand(widget) for widget in required)
        required_width += spacing * max(len(required) - 1, 0)
        overflowed: list[QWidget] = []
        total = required_width
        if deferrable:
            total += spacing
            total += sum(_width_demand(widget) for widget in deferrable)
            total += spacing * (len(deferrable) - 1)
        for widget in deferrable:
            if total <= available:
                break
            total -= _width_demand(widget) + spacing
            self.row.removeWidget(widget)
            self._overflow_panel_layout.addWidget(widget)
            overflowed.append(widget)
        self._overflow_button.setVisible(bool(overflowed))

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        self.refresh_overflow()
