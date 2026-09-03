"""The one-line Graphs/Trace header: view, fit, lifecycle, and cursor actions.

The controls it lays out are still owned and wired by their original panels
(`GraphControlsBar`, `AcquisitionBar`) - this bar only reparents their widgets
into one row, the same pattern the workspace mode selector already used, so
no control gains a second, drifting copy of itself.
"""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QWidget

#: The one readout that carries no control of its own steps aside first when
#: the row cannot hold everything at once - the same graceful-degradation
#: contract GraphControlsBar already applies to its own readouts.
#:
#: `empty_state_label` is deliberately excluded: unlike a readout that always
#: has something to say, its visibility is business state owned by
#: `GraphStackPanel.refresh_data()` (there is or is not a sample). Forcing it
#: visible here just to measure it would show a "no plot yet" message while a
#: session is running, and count its 40px against the budget it does not
#: actually occupy while hidden.
SHRINK_PRIORITY = ("cursor_summary",)


class WorkspaceHeaderBar(QWidget):
    """A single, never-wrapping row above the graph/trace/report stack."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, objectName="workspaceHeaderBar")
        self.row = QHBoxLayout(self)
        self.row.setContentsMargins(0, 0, 0, 0)
        self.row.setSpacing(4)
        self._named: dict[str, QWidget] = {}

    def add(self, widget: QWidget, *, name: str | None = None) -> QWidget:
        self.row.addWidget(widget)
        if name is not None:
            self._named[name] = widget
        return widget

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]  # noqa: N802
        super().resizeEvent(event)
        if self.width() <= 0:
            return
        shrinkable = [self._named[name] for name in SHRINK_PRIORITY if name in self._named]
        for widget in shrinkable:
            widget.setVisible(True)
        for widget in shrinkable:
            if self._minimum_row_width() > self.width():
                widget.setVisible(False)

    def _minimum_row_width(self) -> int:
        widgets = [
            self.row.itemAt(index).widget()
            for index in range(self.row.count())
            if self.row.itemAt(index).widget() is not None
        ]
        visible = [widget for widget in widgets if widget.isVisibleTo(self)]
        if not visible:
            return 0
        return sum(widget.minimumSizeHint().width() for widget in visible) + (
            self.row.spacing() * (len(visible) - 1)
        )
