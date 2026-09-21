"""Small shared widgets: collapsible instrument panels and state notes."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from peaklive.i18n import render, translate

#: Width of a collapsed panel: the toggle plus the rotated title, nothing more.
#: Everything beyond it goes back to the splitter.
RAIL_WIDTH = 34

#: Qt's own UNBOUNDED_WIDTH, which PySide6 does not export. Restoring it is how
#: a widget says "no maximum" again.
UNBOUNDED_WIDTH = 16_777_215

#: What a readout asks for, and the least it will accept. A readout must never
#: size its cluster to the longest string it might ever hold: font metrics
#: differ per platform, and a cluster wider than its row overflows rather than
#: wraps.
READOUT_PREFERRED_WIDTH = 96
READOUT_MINIMUM_WIDTH = 40


class ElidingLabel(QLabel):
    """A readout that shortens its text to the width it was given.

    `text()` keeps the full value - the shortening happens at paint time - so
    callers and tests still read what the readout means, and the tooltip
    carries the untruncated string.
    """

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setToolTip(text)
        self._preferred_width: int | None = None

    def setText(self, text: str) -> None:  # noqa: N802 - Qt override
        super().setText(text)
        self.setToolTip(text)

    def set_preferred_width(self, width: int) -> None:
        """Ask for this much room without refusing to shorten below it.

        A readout that must be fully legible when there is room asks here
        rather than through `setMinimumWidth`: a minimum is a refusal to
        shrink, and on a row too narrow for every documented command that
        refusal is paid by a command losing its place instead of by the text
        eliding, with the untruncated value one hover away.
        """
        preferred = width or None
        if self._preferred_width == preferred:
            return
        self._preferred_width = preferred
        self.updateGeometry()

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override
        hint = super().sizeHint()
        if self._preferred_width is not None:
            return QSize(self._preferred_width, hint.height())
        return QSize(min(hint.width(), READOUT_PREFERRED_WIDTH), hint.height())

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - Qt override
        return QSize(READOUT_MINIMUM_WIDTH, super().minimumSizeHint().height())

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]  # noqa: N802
        painter = QPainter(self)
        painter.setPen(self.palette().color(self.foregroundRole()))
        elided = self.fontMetrics().elidedText(
            self.text(), Qt.TextElideMode.ElideRight, self.width()
        )
        painter.drawText(self.rect(), int(self.alignment()), elided)
        painter.end()


class VerticalLabel(QLabel):
    """A label painted bottom-to-top, so a collapsed rail still names itself."""

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override
        hint = super().sizeHint()
        return QSize(hint.height(), hint.width())

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - Qt override
        hint = super().minimumSizeHint()
        return QSize(hint.height(), hint.width())

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]  # noqa: N802
        painter = QPainter(self)
        # Rotate about the bottom-left corner, then draw into a rect whose
        # width is the widget's height: the text reads bottom-to-top.
        painter.translate(0, self.height())
        painter.rotate(-90.0)
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.drawText(
            0, 0, self.height(), self.width(), int(Qt.AlignmentFlag.AlignCenter), self.text()
        )
        painter.end()


class CollapsiblePanel(QFrame):
    """An instrument frame whose body can be collapsed without losing state.

    Collapsing only hides the body widget: every child keeps its selection,
    check state, and data, so a collapsed panel restores exactly as it was.
    """

    collapsed_changed = Signal(bool)
    #: Emitted with the new hidden state whenever `set_hidden` actually
    #: changes it, mirroring `collapsed_changed`.
    visibility_changed = Signal(bool)

    def __init__(
        self, title: str, key: str, parent: QWidget | None = None, *, title_key: str = ""
    ) -> None:
        super().__init__(parent, objectName="instrument")
        self.key = key
        self._title = title
        #: The catalog key the title came from, so the panel can rename itself
        #: in another language without the shell re-reaching into its widgets.
        self.title_key = title_key
        # Explicit state: a panel inside a window that was never shown is not
        # collapsed, it is simply not on screen yet.
        self._collapsed = False
        # Explicit state, independent of `QWidget.isVisible()`, which also
        # reflects whether the top-level window itself has been shown yet.
        self._hidden = False
        layout = QVBoxLayout(self)
        self._layout = layout
        self._expanded_margins = layout.contentsMargins()
        header = QHBoxLayout()
        self._header = header
        self.heading = ElidingLabel(title.upper())
        self.heading.setObjectName("panelHeading")
        header.addWidget(self.heading, 1)
        self.toggle = QToolButton(objectName="collapseButton")
        self.toggle.setAccessibleName(translate("panel.collapse").format(panel=title))
        self.toggle.setToolTip(translate("panel.collapse").format(panel=title))
        self.toggle.setText("−")
        header.addWidget(self.toggle)
        layout.addLayout(header)
        self.body = QWidget()
        body_layout = QVBoxLayout(self.body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.body, 1)
        # The rail is what a collapsed panel leaves on screen: its name and the
        # control that brings it back. It is created once and simply hidden.
        self.rail = VerticalLabel(title.upper())
        self.rail.setObjectName("panelRail")
        self.rail.setAccessibleName(translate("panel.rail").format(panel=title))
        self.rail.setVisible(False)
        layout.addWidget(self.rail, 1)
        self.toggle.clicked.connect(self._toggle)

    @property
    def body_layout(self) -> QVBoxLayout:
        layout = self.body.layout()
        assert isinstance(layout, QVBoxLayout)
        return layout

    @property
    def header_layout(self) -> QHBoxLayout:
        """The panel's own title row, so a caller can extend it in place.

        Inserting before the collapse toggle keeps that control last no
        matter how many widgets a panel adds to its header.
        """
        return self._header

    def insert_into_header(self, widget: QWidget) -> None:
        self._header.insertWidget(self._header.count() - 1, widget)

    @property
    def is_collapsed(self) -> bool:
        return self._collapsed

    def set_collapsed(self, collapsed: bool) -> None:
        if collapsed == self._collapsed:
            self._sync_toggle()
            return
        self._collapsed = collapsed
        self.body.setVisible(not collapsed)
        self.rail.setVisible(collapsed)
        self.heading.setVisible(not collapsed)
        # A normal instrument header has comfortable margins. Keeping those
        # margins in a 34 px rail leaves less room than the button itself, so
        # Qt clips its plus glyph. The compact rail gets a centred 18 px
        # control and only two-pixel side gutters.
        if collapsed:
            self._layout.setContentsMargins(2, 4, 2, 4)
            self._header.setContentsMargins(0, 0, 0, 0)
            self.toggle.setFixedSize(18, 18)
            self._header.setAlignment(self.toggle, Qt.AlignmentFlag.AlignHCenter)
        else:
            self._layout.setContentsMargins(self._expanded_margins)
            self.toggle.setMaximumSize(UNBOUNDED_WIDTH, UNBOUNDED_WIDTH)
            self.toggle.setMinimumSize(0, 0)
            self._header.setAlignment(self.toggle, Qt.AlignmentFlag.AlignRight)
        # Capping the width is what actually releases the column: a splitter
        # honours a child's maximum, so the space goes to the neighbours.
        self.setMaximumWidth(RAIL_WIDTH if collapsed else UNBOUNDED_WIDTH)
        self.setMinimumWidth(RAIL_WIDTH if collapsed else 0)
        self._sync_toggle()
        self.collapsed_changed.emit(collapsed)

    def _toggle(self) -> None:
        self.set_collapsed(not self.is_collapsed)

    @property
    def is_hidden(self) -> bool:
        return self._hidden

    def set_hidden(self, hidden: bool) -> None:
        """Remove the panel, rail included, or restore it.

        Independent of `set_collapsed`: the collapsed/expanded state is
        preserved underneath and reapplied exactly as it was the moment the
        panel becomes visible again.
        """
        if hidden == self._hidden:
            return
        self._hidden = hidden
        self.setVisible(not hidden)
        self.visibility_changed.emit(hidden)

    def retranslate(self) -> None:
        """Rename the panel, its rail and its toggle in the active language."""
        if self.title_key:
            self._title = translate(self.title_key)
            self.heading.setText(self._title.upper())
            self.rail.setText(self._title.upper())
        self.rail.setAccessibleName(translate("panel.rail").format(panel=self._title))
        self._sync_toggle()

    def _sync_toggle(self) -> None:
        collapsed = self.is_collapsed
        self.toggle.setProperty("collapsed", collapsed)
        self.toggle.setText("+" if collapsed else "−")
        key = "panel.expand" if collapsed else "panel.collapse"
        label = translate(key).format(panel=self._title)
        self.toggle.setAccessibleName(label)
        self.toggle.setToolTip(label)
        self.toggle.style().unpolish(self.toggle)
        self.toggle.style().polish(self.toggle)


class StateNote(QLabel):
    """A panel-local empty, loading, warning, or error message.

    Unlike a status-bar message this stays visible until the condition that
    produced it is resolved, which is the point: an operator watching the trace
    must not lose a DBC conflict to the next incoming frame.
    """

    LEVELS = {
        "info": "stateNote",
        "warning": "warningNote",
        "error": "errorNote",
    }

    def __init__(self, text: str = "", parent: QWidget | None = None, *, key: str = "") -> None:
        super().__init__(text, parent, objectName="stateNote")
        self.setWordWrap(True)
        self.level = "info"
        self._key = key
        self._params: dict[str, object] = {}
        self.setVisible(bool(text))

    def show_message(self, text: str, level: str = "info") -> None:
        """Show prose the caller already rendered; forgets any retained key."""
        self._key = ""
        self._params = {}
        self._apply(text, level)

    def show_key(self, key: str, level: str = "info", **params: object) -> None:
        """Show a catalog entry and remember it, so a language change re-renders it.

        Parameters stay semantic — a name, a count, a driver's own message — so
        re-rendering never has to parse prose that was already formatted.
        """
        self._key = key
        self._params = params
        self._apply(render(key, **params), level)

    def retranslate(self) -> None:
        if self._key:
            self._apply(render(self._key, **self._params), self.level)

    def _apply(self, text: str, level: str) -> None:
        self.level = level if level in self.LEVELS else "info"
        self.setObjectName(self.LEVELS[self.level])
        self.setText(text)
        self.setVisible(bool(text))
        self.style().unpolish(self)
        self.style().polish(self)

    def clear_message(self) -> None:
        self.level = "info"
        self._key = ""
        self._params = {}
        self.setObjectName(self.LEVELS["info"])
        self.setText("")
        self.setVisible(False)
