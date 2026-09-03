"""Focused workspace panels composed by the main window."""

from .acquisition_bar import AcquisitionBar
from .dbc_library import DbcLibraryPanel
from .graph_stack import GraphStackPanel
from .inspector import InspectorPanel
from .measurement import MeasurementPanel
from .report import ReportPanel
from .signal_explorer import SignalExplorerPanel
from .trace_filters import TraceFilterBar
from .trace_view import TraceViewPanel
from .workspace_header import WorkspaceHeaderBar

__all__ = [
    "AcquisitionBar",
    "DbcLibraryPanel",
    "GraphStackPanel",
    "InspectorPanel",
    "MeasurementPanel",
    "ReportPanel",
    "SignalExplorerPanel",
    "TraceFilterBar",
    "TraceViewPanel",
    "WorkspaceHeaderBar",
]
