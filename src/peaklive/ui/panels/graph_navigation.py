"""Time-axis navigation for the stacked plots.

Three things an operator can mean by "where am I looking" are kept apart here,
because conflating them is what made the old viewport surprising. The *global
extent* is everything there is to navigate — a capture's own span, or zero to
now for a live session. *Fit* shows that extent. *Follow-tail* is the choice to
keep a narrower window pinned to the newest data instead. A completed capture
therefore opens showing all of itself, a live session grows from zero, and an
operator who zooms keeps the window they chose.
"""

from __future__ import annotations

#: A completed capture is a fixed thing to read: its extent is exactly the span
#: of the samples it retained.
AXIS_CAPTURE = "capture"

#: A live session is an open-ended thing to watch: its extent begins at the
#: moment the session started, not at its first sample, and only ever grows.
#: Anchoring the left edge at zero is what keeps the operator's mental picture
#: of elapsed time stable while the right edge advances.
AXIS_LIVE = "live"

ZOOM_STEP = 1.6

#: Follow-live modes (item_137 AC3): the default is the whole live/capture
#: extent; "trailing" keeps the pre-existing pinned-narrower-window behavior.
FOLLOW_MODE_FULL = "full"
FOLLOW_MODE_TRAILING = "trailing"

#: How far a manual pan or zoom may travel past either data edge, as a
#: fraction of the acquired/live span (item_137 AC1) - enough room to read the
#: last sample without it sitting flush against the plot border.
X_RANGE_PADDING_FRACTION = 0.05

#: A floor on that padding in seconds, so an empty, one-sample, or
#: sub-millisecond extent still clamps to a usable, non-degenerate window
#: instead of one a fraction of a millisecond wide (item_137 AC2).
X_RANGE_MIN_PADDING_SECONDS = 0.5

#: How far ahead of the newest sample Follow live reserves blank canvas
#: (item_144). The axis then stays still until data reaches that edge instead
#: of moving on every refresh, which is what made following cost a range
#: change - and its whole notification fan-out - per incoming slice.
FOLLOW_LOOK_AHEAD_SECONDS = 30.0

#: In trailing mode the reserved space is taken out of the operator's own
#: window, so it is capped at a quarter of it: the selected span is preserved
#: and at least three quarters of it still shows recent history.
FOLLOW_LOOK_AHEAD_SPAN_FRACTION = 0.25


def _clamp_x_range(
    low: float, high: float, extent: tuple[float, float]
) -> tuple[float, float]:
    """Bound `[low, high]` to `extent` plus a small, finite edge margin.

    A window that lands entirely outside the padded extent (e.g. after a
    fast pan) snaps back to the full padded extent rather than staying
    stranded over blank canvas.
    """
    extent_low, extent_high = extent
    span = extent_high - extent_low
    padding = max(span * X_RANGE_PADDING_FRACTION, X_RANGE_MIN_PADDING_SECONDS)
    lower_bound = extent_low - padding
    upper_bound = extent_high + padding
    clamped_low = max(low, lower_bound)
    clamped_high = min(high, upper_bound)
    if clamped_high <= clamped_low:
        return lower_bound, upper_bound
    return clamped_low, clamped_high


class GraphNavigation:
    """Extent, zoom, fit, and follow-tail over the shared X axis."""

    # ---- extent --------------------------------------------------------

    def begin_session(self, *, live: bool) -> None:
        """Adopt the axis semantics of the session that is about to start."""
        self._axis_mode = AXIS_LIVE if live else AXIS_CAPTURE
        self._live_extent_end = 0.0
        self._window_chosen = False
        self._release_reserved_axis()

    def global_extent(self) -> tuple[float, float] | None:
        """The whole time span the operator should be able to navigate.

        For a capture that is the samples' own span. For a live session it is
        zero to the newest sample, and it never contracts: a bounded series
        drops its oldest samples as it fills, and letting the axis follow that
        would silently rewrite how much history the operator appears to have.
        """
        history = getattr(self, "_history", None)
        store = self._store
        bounds = (
            history.bounds()
            if history is not None
            else (None if store is None else store.bounds())
        )
        if self._axis_mode is not AXIS_LIVE:
            return bounds
        if bounds is None:
            return None
        end = max(self._live_extent_end, bounds[1])
        self._live_extent_end = end
        return (0.0, end)

    def show_full_extent(self) -> None:
        """Show the whole extent, unless the operator has navigated away.

        A completed replay lands here, which is why a finished capture opens
        showing all of itself rather than its last few seconds. Zooming clears
        follow-live, and that choice outranks this.
        """
        if not self.follow_live:
            return
        self.fit()

    def _apply_follow(self, extent: tuple[float, float]) -> None:
        """Keep the newest data in view, moving the axis only at a reserved edge.

        `FOLLOW_MODE_FULL` (the default) always shows the whole extent, so
        re-enabling follow-live after a manual zoom jumps back to the whole
        span rather than resuming wherever the operator last narrowed it.
        `FOLLOW_MODE_TRAILING` keeps the pre-existing behavior: once the
        operator has chosen a window narrower than the extent, that width
        stays pinned to the newest data instead. Inferring "chosen" from the
        current span alone was the old defect: a plot that has never been
        ranged reports the library's own default, so a fresh session showed a
        one-second tail of a capture it should have been showing whole.

        On a live session both modes reserve blank canvas ahead of the newest
        sample rather than tracking it continuously. Between boundaries the
        target range is the one already displayed and nothing is set at all,
        so incoming points keep being drawn into space the axis has already
        made for them. The reserved edge is display only: it is computed from
        session data time, it never reaches `global_extent`, and it therefore
        cannot widen the sample or history bounds A/B and Fit are read from.
        """
        anchor = getattr(self, "anchor_plot", None)
        if anchor is None:
            return
        view = anchor.getViewBox()
        current = view.viewRange()[0]
        span = current[1] - current[0]
        full = extent[1] - extent[0]
        mode = getattr(self, "follow_live_mode", FOLLOW_MODE_FULL)
        newest = extent[1]
        # Only a live session has a future to reserve. A capture's extent is a
        # fixed thing to read, so reserving ahead of it would squeeze the whole
        # recording into part of the width for no responsiveness gained.
        reserve = self._axis_mode is AXIS_LIVE
        padding = 0.0
        if mode != FOLLOW_MODE_TRAILING or not self._window_chosen or span <= 0 or span >= full:
            low = extent[0]
            high = self._reserved_edge(newest, FOLLOW_LOOK_AHEAD_SECONDS) if reserve else newest
            if high <= newest:
                # Nothing reserved ahead - a capture, or a live session Fit has
                # just settled on its real extent. Leave a window that already
                # shows all of it alone, so Fit's own edge margin survives the
                # next refresh instead of being trimmed flush to the last
                # sample; otherwise adopt that same margin.
                if current[0] <= extent[0] and current[1] >= newest:
                    return
                padding = 0.02
        else:
            look_ahead = min(FOLLOW_LOOK_AHEAD_SECONDS, span * FOLLOW_LOOK_AHEAD_SPAN_FRACTION)
            high = self._reserved_edge(newest, look_ahead) if reserve else newest
            low = high - span
        if not padding and (low, high) == (current[0], current[1]):
            return
        self._applying_range = True
        try:
            view.setXRange(low, high, padding=padding)
        finally:
            self._applying_range = False

    def _reserved_edge(self, newest: float, look_ahead: float) -> float:
        """The right edge to display, advanced only once data reaches it.

        A large timestamp jump is absorbed by this one computation rather than
        one catch-up step per missed interval, because the new edge is derived
        from the newest sample itself and not from the previous edge.
        """
        reserved = getattr(self, "_reserved_axis_end", None)
        if reserved is None or newest > reserved or newest + look_ahead < reserved:
            reserved = newest + look_ahead
            self._reserved_axis_end = reserved
        return reserved

    def _release_reserved_axis(self) -> None:
        """Drop the reserved edge so the next follow update recomputes it.

        Called wherever the axis stops meaning what it meant: a new session, a
        mode change, and re-enabling Follow after manual navigation - which is
        what makes re-enabling catch up at once instead of waiting out an edge
        reserved for an earlier window.
        """
        self._reserved_axis_end = None

    def set_follow_live_mode(self, mode: str) -> None:
        """Adopt a Follow-live mode and, if following now, reapply it at once."""
        self.follow_live_mode = mode
        self._release_reserved_axis()
        extent = self.global_extent()
        if extent is not None and self.follow_live:
            self._apply_follow(extent)

    def zoom(self, factor: float) -> None:
        anchor = getattr(self, "anchor_plot", None)
        if anchor is None:
            return
        self.set_follow_live(False)
        self._window_chosen = True
        view = anchor.getViewBox()
        low, high = view.viewRange()[0]
        center = (low + high) / 2
        span = max((high - low) * factor, 1e-6)
        view.setXRange(center - span / 2, center + span / 2, padding=0)

    def fit(self) -> None:
        """Show the whole extent of every shown lane, on both axes.

        X is set explicitly from the session's extent, and Y is an explicit
        autorange per lane rather than pyqtgraph's own implicit default, so
        the action is a deliberate "fit everything" rather than an X-only
        reset that happens to leave Y wherever the library last left it.
        """
        anchor = getattr(self, "anchor_plot", None)
        extent = self.global_extent()
        if anchor is None or extent is None:
            return
        self._window_chosen = False
        # Fit is a deliberate "show exactly what there is", so it reserves no
        # future: the axis holds the real extent until data actually passes it,
        # at which point following resumes with a fresh look-ahead. Releasing
        # the edge instead would let the next refresh immediately re-expand the
        # window the operator just asked to see, including after a Stop.
        self._reserved_axis_end = extent[1]
        self._applying_range = True
        try:
            anchor.getViewBox().setXRange(extent[0], extent[1], padding=0.02)
        finally:
            self._applying_range = False
        for plot in self._plots.values():
            plot.getViewBox().enableAutoRange(y=True)

    def fit_y(self) -> None:
        """Recompute every shown lane's Y range within the current X window.

        The visible time window is left exactly where the operator set it -
        only the amplitude axis is rescaled, which is what an operator needs
        after zooming into a time window and losing a signal off the top or
        bottom of its lane.
        """
        if not self._plots:
            return
        for plot in self._plots.values():
            plot.getViewBox().enableAutoRange(y=True)

    def set_follow_live(self, enabled: bool) -> None:
        if self.follow_live == enabled:
            return
        self.follow_live = enabled
        if enabled:
            self._release_reserved_axis()
        self.follow_checkbox.blockSignals(True)
        self.follow_checkbox.setChecked(enabled)
        self.follow_checkbox.blockSignals(False)

    def _follow_toggled(self, enabled: bool) -> None:
        self.follow_live = enabled
        if enabled:
            self._release_reserved_axis()
            self.refresh_data()

    def visible_window(self) -> tuple[float, float] | None:
        anchor = getattr(self, "anchor_plot", None)
        if anchor is None:
            return None
        low, high = anchor.getViewBox().viewRange()[0]
        return float(low), float(high)

    def _x_range_changed(self) -> None:
        """React to any X-range change, telling a manual one from our own.

        pyqtgraph fires the same signal whether the operator just wheel-zoomed
        or panned the plot directly, or a follow-live/fit update just moved
        it programmatically. Only the former is a manual navigation choice
        that must disable follow-live; the latter would otherwise be
        immediately undone by the very update that caused it.

        Only the anchor lane is connected to this (see `GraphStackPanel.sync`).
        A linked lane also emits when it is merely mirroring the anchor -
        including from its own resizeEvent, which pyqtgraph routes through
        linkedViewChanged outside the `_applying_range` guard - and that read
        as a manual navigation, silently clearing Follow live on any relayout
        of a multi-lane stack. A real gesture on a linked lane still
        propagates to the anchor, so nothing the operator does is lost.
        """
        if not self._applying_range:
            self.set_follow_live(False)
            self._window_chosen = True
            self._clamp_manual_range()
        self.view_changed.emit()

    def _clamp_manual_range(self) -> None:
        """Snap a just-completed manual pan/zoom back inside the data extent.

        Only reached for a manual change (see `_x_range_changed`); a follow-live
        or fit update already computes its range from the extent itself and
        sets `_applying_range` around its own `setXRange`, so it never re-enters
        here.
        """
        anchor = getattr(self, "anchor_plot", None)
        extent = self.global_extent()
        if anchor is None or extent is None:
            return
        view = anchor.getViewBox()
        low, high = view.viewRange()[0]
        clamped_low, clamped_high = _clamp_x_range(low, high, extent)
        if (clamped_low, clamped_high) == (low, high):
            return
        self._applying_range = True
        try:
            view.setXRange(clamped_low, clamped_high, padding=0)
        finally:
            self._applying_range = False
