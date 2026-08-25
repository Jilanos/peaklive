"""Small shared widgets: collapsible instrument panels and state notes."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from peaklive.i18n import translate


class CollapsiblePanel(QFrame):
    """An instrument frame whose body can be collapsed without losing state.

    Collapsing only hides the body widget: every child keeps its selection,
    check state, and data, so a collapsed panel restores exactly as it was.
    """

    collapsed_changed = Signal(bool)

    def __init__(self, title: str, key: str, parent: QWidget | None = None) -> None:
        super().__init__(parent, objectName="instrument")
        self.key = key
        self._title = title
        # Explicit state: a panel inside a window that was never shown is not
        # collapsed, it is simply not on screen yet.
        self._collapsed = False
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        self.heading = QLabel(title.upper(), objectName="panelHeading")
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
        self.toggle.clicked.connect(self._toggle)

    @property
    def body_layout(self) -> QVBoxLayout:
        layout = self.body.layout()
        assert isinstance(layout, QVBoxLayout)
        return layout

    @property
    def is_collapsed(self) -> bool:
        return self._collapsed

    def set_collapsed(self, collapsed: bool) -> None:
        if collapsed == self._collapsed:
            self._sync_toggle()
            return
        self._collapsed = collapsed
        self.body.setVisible(not collapsed)
        self._sync_toggle()
        self.collapsed_changed.emit(collapsed)

    def _toggle(self) -> None:
        self.set_collapsed(not self.is_collapsed)

    def _sync_toggle(self) -> None:
        collapsed = self.is_collapsed
        self.toggle.setText("+" if collapsed else "−")
        key = "panel.expand" if collapsed else "panel.collapse"
        label = translate(key).format(panel=self._title)
        self.toggle.setAccessibleName(label)
        self.toggle.setToolTip(label)


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

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent, objectName="stateNote")
        self.setWordWrap(True)
        self.level = "info"
        self.setVisible(bool(text))

    def show_message(self, text: str, level: str = "info") -> None:
        self.level = level if level in self.LEVELS else "info"
        self.setObjectName(self.LEVELS[self.level])
        self.setText(text)
        self.setVisible(bool(text))
        self.style().unpolish(self)
        self.style().polish(self)

    def clear_message(self) -> None:
        self.level = "info"
        self.setObjectName(self.LEVELS["info"])
        self.setText("")
        self.setVisible(False)
