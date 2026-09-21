"""The one-line Graphs/Trace header: view, fit, lifecycle, and cursor actions.

The controls it lays out are still owned and wired by their original panels
(`GraphControlsBar`, `AcquisitionBar`) - this bar only reparents their widgets
into one row, the same pattern the workspace mode selector already used, so
no control gains a second, drifting copy of itself.

Order and width policy: controls sit in the order the request documents -
view selector; Play, Stop, bus state; Follow live and the two fits; the
cursors and what they measure - separated by a rule per group, and a control
returning from the overflow menu is restored by that rank rather than
appended, so no sequence of resizes can permute the row.

The row never silently clips a control. Required controls (every one of those
commands, plus the A/B/delta reading) always stay directly on the row.
Deferrable ones - the measurement-values toggle and the view selector - move
into an overflow menu, least important first, once the row runs out of width.
When even that is not enough, decoration and prose give way before a command
does: the group rules disappear and elidable text shortens in place, with its
untruncated value on its own tooltip.
"""

from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMenu,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from peaklive.i18n import translate
from peaklive.ui.icons import BUTTON_BOX

#: Box width of the rule that separates one group of header actions from the
#: next: a margin, the one-pixel line the stylesheet draws, and a margin.
GROUP_RULE_WIDTH = 7


def _width_demand(widget: QWidget) -> int:
    """The width a control actually needs, not just its capped preferred hint.

    `ElidingLabel.sizeHint()` (used by the cursor summary) caps itself at a
    small preferred width and instead forces a real minimum through
    `setMinimumWidth` once it knows its text - a plain `sizeHint()` read
    would under-count exactly the readout AC8 must not clip. A control with
    a fixed box, on the other hand, can never be wider than that box however
    large its own content hint is, so the cap is honoured too.
    """
    return min(
        max(widget.sizeHint().width(), widget.minimumWidth()),
        widget.maximumWidth(),
    )


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
        # The canonical left-to-right order, independent of which controls
        # happen to be folded right now. A control returning from the
        # overflow menu is re-inserted by this rank rather than appended, so
        # the row reads the same however it got to its current width.
        self._order: list[QWidget] = []
        self._rules: list[QWidget] = []
        # Text that is allowed to shorten in place rather than push a control
        # off the row: its demand is what it needs to stay readable elided.
        self._elidable: set[QWidget] = set()
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
        # The same box every other header action uses, so the width it always
        # reserves is the contract's box and not whatever its own glyph and
        # the platform's padding happen to add up to.
        self._overflow_button.setProperty("headerIcon", True)
        self._overflow_button.setFixedSize(BUTTON_BOX, BUTTON_BOX)
        self._overflow_button.setVisible(False)
        self.row.addWidget(self._overflow_button)
        self._refreshing_overflow = False

    def retranslate(self) -> None:
        self._overflow_button.setAccessibleName(translate("workspace.header_overflow"))
        self._overflow_button.setToolTip(translate("workspace.header_overflow"))

    def add(
        self, widget: QWidget, *, deferrable: bool = False, elidable: bool = False
    ) -> QWidget:
        """Register a control on the row, in its canonical left-to-right place.

        `deferrable=True` marks a lower-frequency control that may move into
        the overflow menu under width pressure; everything else is required
        and always stays directly visible. `elidable=True` marks explanatory
        text that shortens in place instead, so it claims only what it needs
        to stay readable rather than its full preferred width.
        """
        self._order.append(widget)
        self.row.insertWidget(self.row.count() - 1, widget)
        (self._deferrable if deferrable else self._required).append(widget)
        if elidable:
            self._elidable.add(widget)
        return widget

    def _demand(self, widget: QWidget) -> int:
        if widget in self._elidable:
            return min(widget.minimumSizeHint().width(), _width_demand(widget))
        return _width_demand(widget)

    def add_group_rule(self) -> QWidget:
        """Mark where one group of actions ends and the next begins.

        It disappears whenever everything on one of its sides has folded into
        the overflow menu, so a rule never ends up floating against the edge
        of the row or doubled against another rule.
        """
        # Drawn by the stylesheet as a left border rather than by QFrame's
        # own VLine shape: a styled QFrame ignores its frame shape, so the
        # shape would render nothing at all here.
        rule = QFrame(self, objectName="workspaceHeaderGroupRule")
        rule.setFixedWidth(GROUP_RULE_WIDTH)
        self._rules.append(rule)
        return self.add(rule)

    def _sync_group_rules(self, available: int) -> None:
        """Show the rules only while they cost no control its place on the row."""
        spacing = self.row.spacing()
        crowded = self._required_floor_width() + len(self._rules) * (
            GROUP_RULE_WIDTH + spacing
        ) > available
        for rule in self._rules:
            rank = self._order.index(rule)
            rule.setVisible(
                not crowded
                and self._any_on_row(self._order[:rank])
                and self._any_on_row(self._order[rank + 1 :])
            )

    def _any_on_row(self, widgets: list[QWidget]) -> bool:
        return any(
            widget.parent() is self and not widget.isHidden()
            for widget in widgets
            if widget not in self._rules
        )

    def _restore_to_row(self, widget: QWidget) -> None:
        """Put a returning control back at its canonical place, not at the end.

        Appending it instead is what made the row's order depend on the
        sequence of width changes it happened to live through: fold the mode
        selector, widen the window, and it came back on the far right of the
        cursor readout it is supposed to precede.
        """
        rank = self._order.index(widget)
        position = 0
        for index in range(self.row.count()):
            other = self.row.itemAt(index).widget()
            if other is None or other is self._overflow_button:
                continue
            if other in self._order and self._order.index(other) < rank:
                position = index + 1
        self.row.insertWidget(position, widget)

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

    def _required_floor_width(self) -> int:
        """The row's true, non-negotiable floor: required controls only.

        This must never depend on which *deferrable* controls happen to be
        on the row right now, or on the overflow button's current
        visibility. `minimumSizeHint()` below feeds straight into
        `reflow_widths`'s idea of the centre panel's minimum width
        (`_reflow_workspace` reads `panel.minimumSizeHint()`); if that
        number could shrink whenever something folds into the overflow
        menu, the centre panel would be allocated less room on the next
        reflow, which shrinks `_available_width()` further, folding more -
        a runaway collapse down to nothing. Reserving the overflow button's
        own width unconditionally (not only when it happens to be visible)
        keeps this floor a fixed point: once every deferrable control has
        folded, there is nothing left that can still shrink it.
        """
        spacing = self.row.spacing()
        required = self._visible_required()
        width = sum(self._demand(widget) for widget in required)
        width += spacing * len(required)
        width += _width_demand(self._overflow_button)
        return width

    def _visible_required(self) -> list[QWidget]:
        """Required controls competing for row width right now.

        The group rules are decoration, not content: they are dropped before
        anything else when the row is crowded (see `_sync_group_rules`), so
        they never contribute to the width the centre column is obliged to
        provide.
        """
        return [
            widget
            for widget in self._required
            if not widget.isHidden() and widget not in self._rules
        ]

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - Qt override
        return QSize(self._required_floor_width(), super().minimumSizeHint().height())

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
                self._restore_to_row(widget)
                # Reparenting always leaves Qt's own hidden flag set; this
                # widget is meant to be shown once it is back on the row.
                widget.show()
        self._sync_group_rules(available)
        spacing = self.row.spacing()
        # A control that is already explicitly hidden (e.g. the empty-state
        # note outside the empty state) claims no row width and never needs
        # to be moved into overflow - only widgets actually competing for
        # space count towards the budget.
        required = [widget for widget in self._required if not widget.isHidden()]
        deferrable = [widget for widget in self._deferrable if not widget.isHidden()]
        required_width = sum(self._demand(widget) for widget in required)
        required_width += spacing * max(len(required) - 1, 0)
        overflowed: list[QWidget] = []
        total = required_width
        if deferrable:
            total += spacing
            total += sum(self._demand(widget) for widget in deferrable)
            total += spacing * (len(deferrable) - 1)
        if total > available and deferrable:
            # The overflow button is about to appear and claims row width of
            # its own; folding against the budget it will actually leave
            # behind - rather than the button-less budget above - is what
            # keeps the button's own rect from landing on top of a control
            # this pass judged as already fitting.
            available = max(available - spacing - _width_demand(self._overflow_button), 0)
        for widget in deferrable:
            if total <= available:
                break
            total -= self._demand(widget) + spacing
            self.row.removeWidget(widget)
            self._overflow_panel_layout.addWidget(widget)
            overflowed.append(widget)
        self._overflow_button.setVisible(bool(overflowed))

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        self.refresh_overflow()

    def showEvent(self, event) -> None:  # noqa: N802 - Qt override
        """Re-settle the fold decision once real, on-screen geometry exists.

        The very first `refresh_overflow()` call (from `WorkspaceCenter`,
        during `MainWindow.__init__`) necessarily runs before the window is
        ever shown, when every ancestor's width is still whatever a fresh,
        unlaid-out `QWidget` reports - not the real splitter-applied width
        `_available_width()` is meant to read. `resizeEvent` alone is not a
        reliable second chance: once that early call folds something out of
        `self.row`, `self`'s own size can shrink to match, and if the
        surrounding layout pass settles without `self`'s own size crossing
        a value Qt considers a "change", no further `resizeEvent` follows to
        correct it. `showEvent` fires once real geometry is finally in
        place regardless, so it is the one point guaranteed to see the true
        picture at least once.
        """
        super().showEvent(event)
        self.refresh_overflow()
