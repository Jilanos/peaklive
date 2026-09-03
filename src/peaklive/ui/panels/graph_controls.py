"""The compact, single-row command bar above the stacked graphs."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from peaklive.i18n import translate
from peaklive.ui.widgets import (
    READOUT_MINIMUM_WIDTH,  # noqa: F401 - re-exported, existing import path
    READOUT_PREFERRED_WIDTH,  # noqa: F401 - re-exported, existing import path
    ElidingLabel,  # noqa: F401 - re-exported, existing import path
)


class GraphControlsBar(QWidget):
    """One dense toolbar for graph navigation, display, cursor, and view mode.

    It deliberately never wraps: wrapping turns a measurement workspace into
    two unrelated headers. Textual state elides in place, while each compact
    action retains an accessible name and tooltip.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("graphControls")
        self.row = QHBoxLayout(self)
        self.row.setContentsMargins(0, 0, 0, 0)
        self.row.setSpacing(4)

        self.mode_selector = QComboBox(objectName="workspaceModeSelector")
        self.mode_selector.setAccessibleName(translate("workspace.mode_accessible"))
        self.mode_selector.setToolTip(translate("workspace.mode_accessible"))
        self.mode_selector.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.empty_state_label = self._readout("graphHeaderEmptyState", "graph.empty")
        self.empty_state_label.setVisible(False)

        self.view_group, view_row = self._group("graphViewGroup")
        self.zoom_in_button = self._nav("zoomInButton", "graph.zoom_in", "+")
        self.zoom_out_button = self._nav("zoomOutButton", "graph.zoom_out", "−")
        self.fit_button = self._nav("fitButton", "graph.fit_xy", "⤢")
        self.fit_y_button = self._nav("fitYButton", "graph.fit_y", "↕")
        view_buttons = (
            self.zoom_in_button, self.zoom_out_button, self.fit_button, self.fit_y_button
        )
        for button in view_buttons:
            view_row.addWidget(button)
        self.window_label = self._readout("windowReadout", "graph.window_empty")
        view_row.addWidget(self.window_label)

        self.display_group, display_row = self._group("graphDisplayGroup")
        self.grid_checkbox = self._toggle("gridCheckbox", "graph.grid", "▦")
        self.follow_checkbox = self._toggle("followCheckbox", "graph.follow", "▶")
        display_row.addWidget(self.grid_checkbox)
        display_row.addWidget(self.follow_checkbox)

        self.cursor_group, cursor_row = self._group("graphCursorGroup")
        self.cursor_a_button = self._nav("cursorAButton", "graph.cursor_a", "A")
        self.cursor_b_button = self._nav("cursorBButton", "graph.cursor_b", "B")
        cursor_row.addWidget(self.cursor_a_button)
        cursor_row.addWidget(self.cursor_b_button)
        self.measurement_visibility_button = self._toggle(
            "measurementVisibilityButton", "measure.toggle_values", "▤"
        )
        cursor_row.addWidget(self.measurement_visibility_button)
        self.cursor_summary = self._readout("cursorSummary", "graph.cursor_summary_empty")
        cursor_row.addWidget(self.cursor_summary)

    # ---- construction -------------------------------------------------

    def _group(self, object_name: str) -> tuple[QWidget, QHBoxLayout]:
        """One compact cluster in the fixed single-row toolbar."""
        group = QWidget(self, objectName=object_name)
        group.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        row = QHBoxLayout(group)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(3)
        self.row.addWidget(group)
        return group, row

    def _nav(self, object_name: str, key: str, glyph: str) -> QToolButton:
        button = QToolButton(objectName=object_name)
        button.setProperty("navButton", True)
        button.setText(glyph)
        button.setAccessibleName(translate(key))
        button.setToolTip(translate(key))
        return button

    def _readout(self, object_name: str, key: str) -> ElidingLabel:
        """A live value stays with the controls that change it."""
        readout = ElidingLabel(translate(key))
        readout.setObjectName(object_name)
        return readout

    def _toggle(self, object_name: str, key: str, glyph: str) -> QToolButton:
        button = self._nav(object_name, key, glyph)
        button.setCheckable(True)
        button.setChecked(True)
        return button

    @property
    def groups(self) -> tuple[QWidget, ...]:
        return (self.view_group, self.display_group, self.cursor_group)

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]  # noqa: N802
        super().resizeEvent(event)
        if self.width() <= 0:
            return
        # A compact screen must retain every action.  Dynamic text can instead
        # step down into its tooltip before a layout is allowed to squeeze it
        # below a readable width (notably with Windows font metrics).
        #
        # cursor_summary is reparented into WorkspaceHeaderBar (item_053 AC6)
        # and manages its own visibility there; touching it here as well would
        # race the two resizeEvent handlers over the same shared widget.
        self.window_label.setVisible(True)
        if self._minimum_row_width() > self.width():
            self.window_label.setVisible(False)

    def _minimum_row_width(self) -> int:
        widgets = self.groups
        return sum(widget.minimumSizeHint().width() for widget in widgets) + (
            self.row.spacing() * (len(widgets) - 1)
        )
