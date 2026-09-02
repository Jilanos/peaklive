"""A stable widget-addressing surface over the workspace panels.

The panels own their widgets. This mixin gives the shell — and the acceptance
tests and operator automation that address it — one flat set of names that does
not move when a panel is refactored.
"""

from __future__ import annotations


class WorkspaceAddressing:
    """Flat accessors for the widgets the workspace exposes by name."""

    @property
    def profile_selector(self):
        return self.acquisition_bar.profile_selector

    @property
    def channel_selector(self):
        return self.acquisition_bar.channel_selector

    @property
    def bitrate_selector(self):
        return self.acquisition_bar.bitrate_selector

    @property
    def capture_format_selector(self):
        return self.acquisition_bar.capture_format_selector

    @property
    def controller_mode_selector(self):
        return self.acquisition_bar.controller_mode_selector

    @property
    def mode_label(self):
        return self.acquisition_bar.mode_label

    @property
    def load_dbc_button(self):
        return self.acquisition_bar.load_dbc_button

    @property
    def open_trace_button(self):
        return self.acquisition_bar.open_trace_button

    @property
    def start_button(self):
        return self.acquisition_bar.start_button

    @property
    def stop_button(self):
        return self.acquisition_bar.stop_button

    @property
    def dbc_library(self):
        return self.dbc_panel.tree

    @property
    def remove_dbc_button(self):
        return self.dbc_panel.remove_button

    @property
    def conflict_selector(self):
        return self.dbc_panel.conflict_selector

    @property
    def signal_filter(self):
        return self.explorer_panel.search

    @property
    def shown_only_checkbox(self):
        return self.explorer_panel.shown_only

    @property
    def favorites_only_checkbox(self):
        return self.explorer_panel.favorites_only

    @property
    def signal_explorer(self):
        return self.explorer_panel.tree

    @property
    def trace_table(self):
        return self.trace_panel.table

    @property
    def graph_scroll(self):
        return self.graph_panel.scroll

    @property
    def cursor_summary(self):
        return self.graph_panel.cursor_summary

    @property
    def signals_body(self):
        return self.signals_panel.body

    @property
    def trace_graph_body(self):
        return self.trace_graph_panel.body

    @property
    def inspector_body(self):
        return self.inspector_panel.body

    @property
    def live_plot(self):
        return next(iter(self.graph_panel.plots.values()))

    @property
    def _plot_widgets(self):
        return self.graph_panel.plots

    @property
    def _plot_curves(self):
        return self.graph_panel.curves

    @property
    def _plot_curve(self):
        return next(iter(self.graph_panel.curves.values()))

    @property
    def measure_table(self):
        return self.graph_panel.measurement.table

    @property
    def report_view(self):
        return self.report_panel.view

    @property
    def bus_state(self) -> str:
        return self.acquisition_bar.bus_state
