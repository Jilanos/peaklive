"""Language-change handling for the stacked graph panel.

Kept beside `graph_stack` rather than inside it: the stack module is already at
this layer's stated line budget, and re-captioning is a concern of its own.
"""

from __future__ import annotations

from peaklive.i18n import translate
from peaklive.ui import theme
from peaklive.ui.panels import graph_controls
from peaklive.ui.panels.graph_lane_header import anchor_lane_title, lane_identity


class GraphStackText:
    """Re-captions the lanes and their chrome without rebuilding any plot.

    Nothing here touches a curve, a cursor position or the viewport: a language
    change must leave the measurement exactly where the operator left it.
    """

    def retranslate(self) -> None:
        self.controls.retranslate()
        self.measurement.retranslate()
        self.refresh_measurements()
        self.note.retranslate()
        for index, (signal_name, plot) in enumerate(self._plots.items()):
            title, detail = lane_identity(self._store, signal_name)
            colour = theme.TRACE_PALETTE[index % len(theme.TRACE_PALETTE)]
            plot.setAccessibleName(translate("graph.plot_accessible"))
            plot.setToolTip(
                translate("graph.trace_colour").format(signal=title, colour=colour)
            )
            header = self._lane_headers.get(signal_name)
            if header is not None:
                header.setToolTip(detail)
                header.setAccessibleName(detail)
                anchor_lane_title(plot, header, title)
        plots = list(self._plots.values())
        if plots:
            plots[-1].setLabel("bottom", translate("graph.time_axis"), units="s")
        if self.empty_state_label.isVisible():
            self.empty_state_label.setText(translate("graph.empty"))
        self._refresh_cursor_summary()

    def _refresh_cursor_summary(self) -> None:
        """Write the A/B readout, sizing the label to the text it now holds."""
        if self.cursor_a is None and self.cursor_b is None:
            self.cursor_summary.setText(translate("graph.cursor_summary_empty"))
            self.cursor_summary.set_preferred_width(0)
            return
        text = translate("graph.cursor_summary").format(
            cursor_a=graph_controls.format_cursor_time(self.cursor_a),
            cursor_b=graph_controls.format_cursor_time(self.cursor_b),
            delta=graph_controls.format_cursor_delta(self.cursor_a, self.cursor_b),
        )
        self.cursor_summary.setText(text)
        width = self.cursor_summary.fontMetrics().horizontalAdvance(text) + 4
        self.cursor_summary.set_preferred_width(width)
