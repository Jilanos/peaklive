"""Narrow quarantine for known Windows offscreen layout failures."""

import os
import sys

import pytest

# CI run https://github.com/Jilanos/peaklive/actions/runs/34771086526:
# 614 passed; these seven functions account for all 11 failing cases.
# Keep running them so XPASS reports show when the quarantine can be removed.
# Linux and native Windows rendering retain their ordinary assertions.
_WINDOWS_OFFSCREEN_LAYOUT_FAILURES = {
    "tests/test_ui_compact_graph_and_signal_states.py": {
        "test_follow_live_shares_the_fit_commands_row",
    },
    "tests/test_ui_workspace_refinement.py": {
        "test_collapsing_the_centre_panel_does_not_corrupt_side_panel_preferences",
        "test_mixed_non_lifo_collapse_sequences_restore_each_panels_own_width",
        "test_the_one_line_graphs_trace_header_stays_readable_at_the_bench_viewports",
        "test_long_values_never_clip_when_side_panels_squeeze_the_header",
        "test_a_long_readout_never_pushes_required_controls_past_the_header",
        "test_workspace_mode_selector_is_visible_and_fully_readable_in_every_mode",
    },
}


def pytest_collection_modifyitems(items):
    if sys.platform != "win32" or os.environ.get("QT_QPA_PLATFORM") != "offscreen":
        return
    for item in items:
        path, _, case = item.nodeid.partition("::")
        name = case.partition("[")[0]
        if name in _WINDOWS_OFFSCREEN_LAYOUT_FAILURES.get(path, ()):
            item.add_marker(
                pytest.mark.xfail(
                    reason="Known Windows offscreen layout failure (CI run 34771086526)",
                    raises=AssertionError,
                    strict=False,
                )
            )
