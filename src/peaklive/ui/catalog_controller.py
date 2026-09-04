"""DBC catalog and signal-selection coordination for the workspace shell.

Operator-driven mutations — add, remove, enable, disable, resolve — are prepared
on a worker thread and committed here in one step. The commit is the only place
the live catalog is replaced, and it updates the catalog, the profile, the
library panel, the signal explorer, the selection, and the graphs together, so
no panel can be left describing a catalog that no longer exists.
"""

from __future__ import annotations

from functools import partial
from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from peaklive.analysis import CatalogView
from peaklive.i18n import translate
from peaklive.services.dbc_worker import (
    CatalogOperation,
    CatalogOperationKind,
    CatalogOutcome,
    DbcCatalogWorker,
    apply_catalog_operation,
)
from peaklive.ui.debounce import INTERACTIVE_DEBOUNCE_MS, Debouncer


class WorkspaceCatalog:
    """Owns the DBC lifecycle and the shown/favorite signal selection.

    Enable, disable, and remove all funnel through here so the profile, the
    catalog, the explorer, and the graph stack can never disagree about which
    databases are active.
    """

    # ---- operation queue ------------------------------------------------

    def _queue_catalog_operation(self, operation: CatalogOperation) -> None:
        """Run `operation` in the background, after any operation already queued.

        Serializing is what keeps rapid consecutive actions deterministic: two
        mutations prepared concurrently would each start from the pre-mutation
        catalog, and whichever committed last would silently drop the other.
        """
        self._catalog_queue.append(operation)
        self._pump_catalog_queue()

    def _pump_catalog_queue(self) -> None:
        if self._catalog_worker is not None or not self._catalog_queue:
            return
        operation = self._catalog_queue.pop(0)
        self._catalog_generation += 1
        generation = self._catalog_generation
        worker = DbcCatalogWorker(self._catalog, operation, generation)
        worker.progressed.connect(partial(self._catalog_progressed, generation))
        worker.completed.connect(partial(self._catalog_completed, generation))
        worker.cancelled.connect(partial(self._catalog_cancelled, generation))
        worker.finished.connect(partial(self._catalog_worker_finished, generation))
        self._catalog_worker = worker
        self._begin_work(_operation_message(operation))
        worker.start()

    def _cancel_catalog_operation(self) -> None:
        """Drop queued work and ask the running operation to stop before commit.

        The generation is bumped as well, so a worker that races past its own
        cancel check and completes anyway is recognised as stale on arrival.
        """
        self._catalog_queue.clear()
        if self._catalog_worker is not None:
            self._catalog_worker.request_cancel()
            self._catalog_generation += 1

    def _catalog_progressed(self, generation: int, done: int, total: int, name: str) -> None:
        if generation != self._catalog_generation:
            return
        if not name:
            return
        self.status.showMessage(
            translate("dbc.load_progress").format(done=done + 1, total=total, name=name)
        )

    def _catalog_completed(self, generation: int, outcome: CatalogOutcome) -> None:
        if generation != self._catalog_generation:
            return
        self._commit_catalog_outcome(outcome)

    def _catalog_cancelled(self, generation: int) -> None:
        if generation != self._catalog_generation:
            return
        # Nothing was committed, so the catalog and the profile are unchanged.
        self.status.showMessage(translate("dbc.cancelled"))

    def _catalog_worker_finished(self, generation: int) -> None:
        worker = self._catalog_worker
        if worker is None or worker.generation != generation:
            return
        self._catalog_worker = None
        self._end_work()
        self._pump_catalog_queue()

    # ---- commit ---------------------------------------------------------

    def _commit_catalog_outcome(self, outcome: CatalogOutcome) -> None:
        """Adopt a prepared catalog state everywhere, in one pass."""
        self._catalog = outcome.view.catalog
        self._reconcile_profile_paths(outcome)
        self._reconcile_selection(outcome)
        self._adopt_catalog_view(outcome.view)
        self._announce_outcome(outcome)
        # Per-file diagnostics come last: refreshing the library rewrites the
        # panel note, and the operator must be left looking at the failure.
        for path, message in outcome.errors:
            self._report_dbc_error(path, message)

    def _reconcile_selection(self, outcome: CatalogOutcome) -> None:
        """Keep the shown-signal selection consistent with the new catalog.

        Removing a DBC drops its signals for good. Disabling one deliberately
        does not: re-enabling it has to bring the operator's plots back, so a
        disabled database's selected signals are kept as they were.
        """
        kind = outcome.operation.kind
        if kind is CatalogOperationKind.REMOVE:
            available = set(outcome.view.signal_names)
            self._selected_signal_names = {
                name for name in self._selected_signal_names if name in available
            }
        elif kind is CatalogOperationKind.LOAD and not self._selected_signal_names:
            first_signal = next(iter(outcome.view.signal_names), None)
            if first_signal is not None:
                self._selected_signal_names.add(first_signal)

    def _adopt_catalog_view(self, view: CatalogView) -> None:
        """Point every dependent panel and projection at one catalog view."""
        self._persist_signal_state(view.signal_names)
        self._persist_dbc_state()
        self.dbc_panel.refresh(view)
        self.explorer_panel.refresh(
            view.references, self._selected_signal_names, self._favorite_signal_names
        )
        self._sync_graphs()

    def _reconcile_profile_paths(self, outcome: CatalogOutcome) -> None:
        profile = self.selected_profile
        changed = False
        for path in outcome.added_paths:
            if str(path) not in profile.dbc_paths:
                profile.dbc_paths.append(str(path))
                changed = True
        if outcome.removed_path is not None:
            remaining = [
                configured
                for configured in profile.dbc_paths
                if configured != str(outcome.removed_path)
            ]
            changed = changed or remaining != profile.dbc_paths
            profile.dbc_paths = remaining
        if changed:
            self._save()

    def _announce_outcome(self, outcome: CatalogOutcome) -> None:
        operation = outcome.operation
        if operation.kind is CatalogOperationKind.LOAD and outcome.added_paths:
            self.status.showMessage(
                translate("dbc.loaded").format(name=outcome.added_paths[-1].name)
            )
        elif operation.kind is CatalogOperationKind.RESOLVE:
            name = next(
                (
                    definition.path.name
                    for definition in outcome.view.definitions
                    if definition.content_hash == operation.content_hash
                ),
                operation.content_hash[:8],
            )
            self.status.showMessage(
                translate("dbc.conflict_resolved").format(
                    arbitration_id=operation.arbitration_id, name=name
                )
            )

    # ---- DBC ------------------------------------------------------------

    def _load_profile_dbcs(self) -> None:
        """Restore a profile catalog through the serial background queue."""
        self._cancel_catalog_operation()
        filters = self.selected_profile.trace_filters
        paths = tuple(Path(path) for path in self.selected_profile.dbc_paths)
        if not paths:
            # Nothing can parse here; clearing an empty profile is immediate
            # and avoids creating a pointless short-lived worker at startup.
            self._catalog.clear()
            self._adopt_catalog_view(self._catalog.view())
            return
        self._queue_catalog_operation(
            CatalogOperation(
                kind=CatalogOperationKind.RESTORE,
                paths=paths,
                disabled_hashes=tuple(
                    str(value) for value in filters.get("disabled_dbc_hashes", [])
                ),
                resolutions=tuple(
                    (int(raw_id), str(content_hash))
                    for raw_id, content_hash in dict(
                        filters.get("dbc_conflict_resolutions", {})
                    ).items()
                ),
            )
        )

    def _choose_dbc(self) -> None:
        selected, _ = QFileDialog.getOpenFileNames(
            self, translate("dbc.load_dialog"), "", translate("dbc.load_filter")
        )
        if not selected:
            return
        self._queue_catalog_operation(
            CatalogOperation(
                kind=CatalogOperationKind.LOAD,
                paths=tuple(Path(item) for item in selected),
            )
        )

    def _load_dbc_path(self, path: Path) -> None:
        """Load a programmatic fixture without ever waiting for a worker.

        The interactive path always queues work.  This small synchronous
        helper remains for deterministic test/setup callers only when no
        operation is in flight; if there is one, it joins the queue instead of
        blocking the UI thread.
        """
        operation = CatalogOperation(kind=CatalogOperationKind.LOAD, paths=(path,))
        if self._catalog_worker is not None:
            self._queue_catalog_operation(operation)
            return
        outcome = apply_catalog_operation(self._catalog, operation)
        if outcome is not None:
            self._commit_catalog_outcome(outcome)

    def _report_dbc_error(self, path: Path, message: str) -> None:
        self._facts.record_anomaly("dbc_error")
        self.dbc_panel.show_error(
            translate("dbc.load_failed").format(name=path.name, message=message)
        )

    def _dbc_enabled_changed(self, content_hash: str, enabled: bool) -> None:
        # The row already shows the new state; the catalog catches up behind it.
        self.dbc_panel.set_row_state(content_hash, enabled)
        self._queue_catalog_operation(
            CatalogOperation(
                kind=CatalogOperationKind.ENABLE,
                content_hash=content_hash,
                enabled=enabled,
            )
        )

    def _remove_dbc(self, content_hash: str) -> None:
        self._queue_catalog_operation(
            CatalogOperation(kind=CatalogOperationKind.REMOVE, content_hash=content_hash)
        )

    def _remove_selected_dbc(self) -> None:
        self.dbc_panel._remove_current()

    def _resolve_conflict(self, arbitration_id: int, content_hash: str) -> None:
        self._queue_catalog_operation(
            CatalogOperation(
                kind=CatalogOperationKind.RESOLVE,
                arbitration_id=arbitration_id,
                content_hash=content_hash,
            )
        )

    # ---- signals -------------------------------------------------------

    @property
    def _signal_explorer_debouncer(self) -> Debouncer:
        """Coalesce a burst of search keystrokes into one tree rebuild."""
        debouncer = getattr(self, "_signal_explorer_debouncer_instance", None)
        if debouncer is None:
            debouncer = Debouncer(
                INTERACTIVE_DEBOUNCE_MS, lambda: self._refresh_signal_explorer(), self
            )
            self._signal_explorer_debouncer_instance = debouncer
        return debouncer

    def _schedule_signal_explorer_refresh(self) -> None:
        self._signal_explorer_debouncer.trigger()

    def _refresh_signal_explorer(self) -> None:
        self.explorer_panel.refresh(
            self._catalog.signal_references(),
            self._selected_signal_names,
            self._favorite_signal_names,
        )

    def _signal_shown_changed(self, signal_name: str, shown: bool) -> None:
        """Show or hide one signal, deriving its history when it has none.

        Selecting a signal the session never decoded used to leave an empty
        plot until the trace was opened again. The retained frames are enough
        to derive it, so selection asks for that instead.
        """
        if shown:
            self._selected_signal_names.add(signal_name)
        else:
            self._selected_signal_names.discard(signal_name)
            self._cancel_signal_backfill(signal_name)
            self._series.drop(signal_name)
        self._persist_signal_state()
        self._sync_graphs()
        if shown:
            self._request_signal_backfill(signal_name)

    def _signal_favorite_changed(self, signal_name: str, favorite: bool) -> None:
        if favorite:
            self._favorite_signal_names.add(signal_name)
        else:
            self._favorite_signal_names.discard(signal_name)
        self._persist_signal_state()

    def _sync_graphs(self) -> None:
        self.graph_panel.sync(self._series, self._selected_signal_names)


def _operation_message(operation: CatalogOperation) -> str:
    if operation.kind in {CatalogOperationKind.LOAD, CatalogOperationKind.RESTORE}:
        return translate("dbc.loading").format(count=len(operation.paths))
    return translate(f"dbc.working_{operation.kind.value}")
