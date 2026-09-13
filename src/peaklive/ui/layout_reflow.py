"""Splitter arithmetic for collapsing, restoring, and rebalancing side panels.

Hiding a panel body is not the same as releasing its column. This module owns
the width arithmetic that turns a collapse into reclaimed workspace and an
expand back into the width the operator last chose, and keeps it out of the
shell so it can be reasoned about — and tested — on its own.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from peaklive.ui.widgets import RAIL_WIDTH

if TYPE_CHECKING:
    from peaklive.ui.widgets import CollapsiblePanel

#: A side panel narrower than this cannot show a signal name or a field label,
#: so it is the floor an expanded panel is restored to.
MIN_SIDE_WIDTH = 200

#: Below this the graph area stops being a measurement workspace; side panels
#: give way first.
MIN_CENTER_WIDTH = 360

#: Used only when nothing was ever remembered for a panel.
DEFAULT_SIDE_WIDTH = 300

#: The graph area keeps three stacked plots visible before the operator has to
#: scroll; the trace keeps enough rows to read a burst. The report opens closed.
GRAPH_MINIMUM_HEIGHT = 240
SECTION_MINIMUM_HEIGHT = 120
DEFAULT_DIVIDER_SIZES = [560, 240, 0]


def reflow_widths(
    collapsed: list[bool],
    remembered: list[int],
    total: int,
    *,
    center: int = 1,
) -> list[int]:
    """Split `total` across three panels, giving collapsed ones only a rail.

    `remembered` carries each panel's preferred expanded width; the centre
    panel absorbs whatever the side panels do not need, and gives width back
    only down to `MIN_CENTER_WIDTH`.
    """
    if total <= 0 or len(collapsed) != len(remembered):
        return []
    rails = sum(1 for flag in collapsed if flag)
    available = total - rails * RAIL_WIDTH
    open_indexes = [index for index, flag in enumerate(collapsed) if not flag]
    if not open_indexes or available <= 0:
        return [RAIL_WIDTH if flag else max(available, 0) for flag in collapsed]

    widths = [RAIL_WIDTH if flag else 0 for flag in collapsed]
    sides = [index for index in open_indexes if index != center]

    if center not in open_indexes:
        share = available // len(sides)
        for index in sides:
            widths[index] = share
        widths[sides[-1]] += available - share * len(sides)
        return widths

    for index in sides:
        widths[index] = max(MIN_SIDE_WIDTH, remembered[index] or DEFAULT_SIDE_WIDTH)
    requested = sum(widths[index] for index in sides)
    if available - requested < MIN_CENTER_WIDTH and sides:
        room = max(available - MIN_CENTER_WIDTH, 0)
        for index in sides:
            widths[index] = widths[index] * room // requested
    widths[center] = available - sum(widths[index] for index in sides)
    return widths


class WorkspaceReflow:
    """Collapse handling for the shell: reclaim, restore, and remember."""

    def _remember_panel_widths(self, *, only: CollapsiblePanel | None = None) -> None:
        """Record the widths the splitter currently shows as the operator's preference.

        Call this only where the current sizes reflect an explicit operator
        choice: right before a collapse/expand reflow runs (the collapse
        signal arrives before the splitter has reflowed, so the panel being
        collapsed is still at its full width here — exactly the width the
        operator expects back on expand) or after a real splitter drag. Never
        call it after `_reflow_workspace` has run, or the automatic
        redistribution it computed would be captured as if the operator had
        chosen it. A rail-sized column is never worth remembering.

        `only`, when given, limits the capture to that one panel. A sibling
        panel's *current* width can itself be leftover automatic allocation
        from an earlier reflow (for example the one panel left open when its
        neighbours were collapsed, which absorbed all of their released
        space) — recording it here would launder that allocation into a
        preference the operator never chose. A real drag legitimately moves
        every column at once, so `_splitter_dragged` passes no `only`.
        """
        panels = (only,) if only is not None else self._layout_panels
        sizes = self.workspace.sizes()
        for panel in panels:
            index = self._layout_panels.index(panel)
            size = sizes[index]
            if size > RAIL_WIDTH:
                self._expanded_widths[panel.key] = int(size)

    def _splitter_dragged(self) -> None:
        """Handle an explicit operator drag of a splitter handle.

        Unlike collapse/expand, a drag does not go through `_reflow_workspace`,
        so the sizes it just produced are exactly the operator's new
        preference and are safe to remember before persisting.
        """
        if self._restoring:
            return
        self._remember_panel_widths()
        self._persist_layout()

    def _reflow_workspace(self) -> None:
        """Apply the collapsed/expanded width split to the workspace splitter."""
        panels = self._layout_panels
        sizes = self.workspace.sizes()
        total = sum(sizes) or self.workspace.width()
        widths = reflow_widths(
            [panel.is_collapsed for panel in panels],
            [self._expanded_widths.get(panel.key, 0) for panel in panels],
            total,
            center=1,
        )
        if widths:
            self.workspace.setSizes(widths)

    def _panel_collapse_changed(self) -> None:
        # Restoring a saved profile emits the same signal as an operator
        # collapsing a panel.  Its splitter has not reached the saved geometry
        # yet, so remembering at that point would replace the saved width with
        # Qt's temporary minimum.  `_show_profile` performs one reflow after
        # all restored state is installed.
        if self._restoring:
            return
        # Only the panel whose own collapse state just changed had a width
        # the operator was actually looking at; a sibling's current width can
        # be leftover automatic allocation from an earlier reflow.
        self._remember_panel_widths(only=self.sender())
        self._reflow_workspace()
        self._persist_layout()
