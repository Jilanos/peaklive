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

from peaklive.i18n import translate

#: A completed capture is a fixed thing to read: its extent is exactly the span
#: of the samples it retained.
AXIS_CAPTURE = "capture"

#: A live session is an open-ended thing to watch: its extent begins at the
#: moment the session started, not at its first sample, and only ever grows.
#: Anchoring the left edge at zero is what keeps the operator's mental picture
#: of elapsed time stable while the right edge advances.
AXIS_LIVE = "live"

ZOOM_STEP = 1.6


class GraphNavigation:
    """Extent, zoom, fit, and follow-tail over the shared X axis."""

    # ---- extent --------------------------------------------------------

    def begin_session(self, *, live: bool) -> None:
        """Adopt the axis semantics of the session that is about to start."""
        self._axis_mode = AXIS_LIVE if live else AXIS_CAPTURE
        self._live_extent_end = 0.0
        self._window_chosen = False

    def global_extent(self) -> tuple[float, float] | None:
        """The whole time span the operator should be able to navigate.

        For a capture that is the samples' own span. For a live session it is
        zero to the newest sample, and it never contracts: a bounded series
        drops its oldest samples as it fills, and letting the axis follow that
        would silently rewrite how much history the operator appears to have.
        """
        store = self._store
        bounds = None if store is None else store.bounds()
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
        """Keep the extent in view, or the tail if the operator zoomed into it.

        Following the tail means something only once the operator has chosen a
        window narrower than the extent. Inferring that from the current span
        alone was the old defect: a plot that has never been ranged reports the
        library's own default, so a fresh session showed a one-second tail of a
        capture it should have been showing whole.
        """
        anchor = getattr(self, "anchor_plot", None)
        if anchor is None:
            return
        view = anchor.getViewBox()
        current = view.viewRange()[0]
        span = current[1] - current[0]
        full = extent[1] - extent[0]
        if not self._window_chosen or span <= 0 or span >= full:
            view.setXRange(extent[0], extent[1], padding=0.02)
            return
        view.setXRange(extent[1] - span, extent[1], padding=0)

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
        """Show the whole extent of the session, capture or live."""
        anchor = getattr(self, "anchor_plot", None)
        extent = self.global_extent()
        if anchor is None or extent is None:
            return
        self._window_chosen = False
        anchor.getViewBox().setXRange(extent[0], extent[1], padding=0.02)
        self._refresh_window_label()

    def set_follow_live(self, enabled: bool) -> None:
        if self.follow_live == enabled:
            return
        self.follow_live = enabled
        self.follow_checkbox.blockSignals(True)
        self.follow_checkbox.setChecked(enabled)
        self.follow_checkbox.blockSignals(False)

    def _follow_toggled(self, enabled: bool) -> None:
        self.follow_live = enabled
        if enabled:
            self.refresh_data()

    def visible_window(self) -> tuple[float, float] | None:
        anchor = getattr(self, "anchor_plot", None)
        if anchor is None:
            return None
        low, high = anchor.getViewBox().viewRange()[0]
        return float(low), float(high)

    def _x_range_changed(self) -> None:
        self._refresh_window_label()
        self.view_changed.emit()

    def _refresh_window_label(self) -> None:
        window = self.visible_window()
        extent = self.global_extent()
        if window is None or extent is None:
            self.window_label.setText(translate("graph.window_empty"))
            return
        low, high = window
        full_low, full_high = extent
        full_span = full_high - full_low
        span = high - low
        zoom = full_span / span if span > 0 and full_span > 0 else 1.0
        self.window_label.setText(
            translate("graph.window").format(
                start=f"{low:.3f}s", end=f"{high:.3f}s", zoom=f"{zoom:.1f}"
            )
        )

