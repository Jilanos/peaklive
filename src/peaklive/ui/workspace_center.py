"""The centre column: the view selector over the graph, trace, and report stack.

Keeping the composition here rather than in the shell is what lets the graph
area own its own vertical priority — minimum heights and stretch factors that
say the graphs are the workspace and the other two sections resize around them.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QSplitter

from peaklive.i18n import translate
from peaklive.ui.layout_reflow import (
    DEFAULT_DIVIDER_SIZES,
    GRAPH_MINIMUM_HEIGHT,
    SECTION_MINIMUM_HEIGHT,
)
from peaklive.ui.panels import GraphStackPanel, ReportPanel, TraceViewPanel, WorkspaceHeaderBar

WORKSPACE_MODES = (
    ("combo", "workspace.mode_combo"),
    ("graphs", "workspace.mode_graphs"),
    ("trace", "workspace.mode_trace"),
    ("report", "workspace.mode_report"),
)


class WorkspaceCenter:
    """Builds the graph/trace/report stack under its view selector."""

    def _build_center_panel(self) -> None:
        layout = self.trace_graph_panel.body_layout
        self.graph_panel = GraphStackPanel()
        controls = self.graph_panel.controls
        self.workspace_mode_selector = controls.mode_selector
        # Every control below is still owned and wired by GraphControlsBar or
        # AcquisitionBar - only the widget is reparented, the same pattern the
        # mode selector already used, so nothing gains a second, drifting copy.
        self.workspace_header = WorkspaceHeaderBar(self.trace_graph_panel)
        for source_row, widget in (
            (controls.row, self.workspace_mode_selector),
            (controls.row, controls.empty_state_label),
            (controls.view_group.layout(), controls.zoom_in_button),
            (controls.view_group.layout(), controls.zoom_out_button),
            (controls.view_group.layout(), controls.fit_button),
            (controls.view_group.layout(), controls.fit_y_button),
            (self.acquisition_bar.layout(), self.acquisition_bar.start_button),
            (self.acquisition_bar.layout(), self.acquisition_bar.stop_button),
            (controls.cursor_group.layout(), controls.cursor_a_button),
            (controls.cursor_group.layout(), controls.cursor_b_button),
            (controls.cursor_group.layout(), controls.measurement_visibility_button),
            (controls.cursor_group.layout(), controls.cursor_summary),
        ):
            source_row.removeWidget(widget)
            widget.setParent(self.workspace_header)
        self.workspace_mode_selector.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )
        self.workspace_mode_selector.setMinimumContentsLength(4)
        for value, key in WORKSPACE_MODES:
            self.workspace_mode_selector.addItem(translate(key), value)
        self.workspace_mode_selector.currentIndexChanged.connect(self._workspace_mode_changed)
        self.workspace_header.add(self.workspace_mode_selector)
        self.workspace_header.add(controls.empty_state_label, name="empty_state_label")
        for button in (
            controls.zoom_in_button,
            controls.zoom_out_button,
            controls.fit_button,
            controls.fit_y_button,
        ):
            self.workspace_header.add(button)
        self.workspace_header.add(self.acquisition_bar.start_button)
        self.workspace_header.add(self.acquisition_bar.stop_button)
        self.workspace_header.add(controls.cursor_a_button)
        self.workspace_header.add(controls.cursor_b_button)
        self.workspace_header.add(controls.measurement_visibility_button)
        self.workspace_header.add(controls.cursor_summary, name="cursor_summary")
        self.trace_graph_panel.insert_into_header(self.workspace_header)

        self.center_divider = QSplitter(Qt.Orientation.Vertical, objectName="centerDivider")
        self.graph_panel.cursors_changed.connect(self._persist_layout)
        self.graph_panel.measurement_visibility_changed.connect(
            self._persist_measurement_visibility
        )
        self.trace_panel = TraceViewPanel()
        self.trace_panel.set_buffer(self._trace)
        self.trace_panel.filters_changed.connect(self._persist_trace_filters)
        self.trace_panel.record_selected.connect(self._trace_record_selected)
        self.trace_panel.columns_requested.connect(self._open_columns_dialog)
        self.report_panel = ReportPanel()
        self.report_panel.refresh_requested.connect(self._refresh_report)
        self.report_panel.export_requested.connect(self._export_report)
        self.center_divider.addWidget(self.graph_panel)
        self.center_divider.addWidget(self.trace_panel)
        self.center_divider.addWidget(self.report_panel)
        # The graph area is the workspace; trace and report resize around it.
        self.graph_panel.setMinimumHeight(GRAPH_MINIMUM_HEIGHT)
        self.trace_panel.setMinimumHeight(SECTION_MINIMUM_HEIGHT)
        self.report_panel.setMinimumHeight(0)
        for index, stretch in enumerate((3, 1, 1)):
            self.center_divider.setStretchFactor(index, stretch)
        self.center_divider.setSizes(DEFAULT_DIVIDER_SIZES)
        self.center_divider.splitterMoved.connect(lambda *_: self._persist_layout())
        layout.addWidget(self.center_divider, 1)
