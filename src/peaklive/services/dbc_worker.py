"""DBC catalog mutations prepared off the UI thread and committed atomically.

Every add, remove, enable, disable, and conflict resolution is expressed as a
`CatalogOperation` and applied to a *copy* of the live catalog. Parsing and the
expensive derived projections (signal references, conflicts, per-DBC counts)
happen on the copy; the workspace keeps decoding against the old catalog until
the finished `CatalogView` is handed over in one step.

That shape is what makes the two guarantees possible at once: the event loop is
never held while cantools parses a large file, and a cancelled or failed
operation cannot leave the catalog, the profile, or the panels half-updated,
because nothing was ever mutated in place.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from threading import Event

from PySide6.QtCore import QThread, Signal

from peaklive.analysis import CatalogView, DbcCatalog, DbcDefinition


class CatalogOperationKind(StrEnum):
    LOAD = "load"
    REMOVE = "remove"
    ENABLE = "enable"
    RESOLVE = "resolve"


@dataclass(frozen=True, slots=True)
class CatalogOperation:
    """One requested catalog mutation, in a form that can cross a thread."""

    kind: CatalogOperationKind
    paths: tuple[Path, ...] = ()
    content_hash: str = ""
    enabled: bool = True
    arbitration_id: int = 0

    @property
    def cancellable(self) -> bool:
        """Whether interrupting this operation before commit is worth offering.

        Only loading does enough work to be worth cancelling; the rest are a
        catalog copy and a projection.
        """
        return self.kind is CatalogOperationKind.LOAD


@dataclass(frozen=True, slots=True)
class CatalogOutcome:
    """A prepared catalog state plus what the commit has to reconcile with it."""

    operation: CatalogOperation
    view: CatalogView
    added_paths: tuple[Path, ...] = ()
    removed_path: Path | None = None
    errors: tuple[tuple[Path, str], ...] = field(default=())


ProgressCallback = Callable[[int, int, str], None]


def apply_catalog_operation(
    catalog: DbcCatalog,
    operation: CatalogOperation,
    progress: ProgressCallback | None = None,
    cancelled: Callable[[], bool] | None = None,
) -> CatalogOutcome | None:
    """Prepare `operation` against a copy of `catalog`.

    Returns the prepared outcome, or None if cancellation was requested before
    the result was ready. Nothing here touches `catalog` itself, so a None
    return means the caller's state is untouched by construction.
    """
    prepared = catalog.copy()
    if operation.kind is CatalogOperationKind.LOAD:
        return _apply_load(prepared, operation, progress, cancelled)
    if operation.kind is CatalogOperationKind.REMOVE:
        return _apply_remove(prepared, operation)
    if operation.kind is CatalogOperationKind.ENABLE:
        prepared.set_enabled(operation.content_hash, operation.enabled)
        return CatalogOutcome(operation, prepared.view())
    if operation.kind is CatalogOperationKind.RESOLVE:
        prepared.resolve(operation.arbitration_id, operation.content_hash)
        return CatalogOutcome(operation, prepared.view())
    raise ValueError(f"Unknown catalog operation: {operation.kind}")


def _apply_load(
    prepared: DbcCatalog,
    operation: CatalogOperation,
    progress: ProgressCallback | None,
    cancelled: Callable[[], bool] | None,
) -> CatalogOutcome | None:
    added: list[Path] = []
    errors: list[tuple[Path, str]] = []
    total = len(operation.paths)
    for index, path in enumerate(operation.paths):
        if cancelled is not None and cancelled():
            return None
        if progress is not None:
            progress(index, total, path.name)
        try:
            definition: DbcDefinition = prepared.load(path)
        except (OSError, ValueError) as error:
            # One unreadable file must not abandon the rest of the selection.
            errors.append((path, str(error)))
            continue
        prepared.set_enabled(definition.content_hash, True)
        added.append(path)
    if cancelled is not None and cancelled():
        return None
    if progress is not None:
        progress(total, total, "")
    return CatalogOutcome(operation, prepared.view(), tuple(added), None, tuple(errors))


def _apply_remove(prepared: DbcCatalog, operation: CatalogOperation) -> CatalogOutcome:
    removed = next(
        (
            definition
            for definition in prepared.definitions
            if definition.content_hash == operation.content_hash
        ),
        None,
    )
    prepared.remove(operation.content_hash)
    return CatalogOutcome(
        operation,
        prepared.view(),
        removed_path=None if removed is None else removed.path,
    )


class DbcCatalogWorker(QThread):
    """Run one `CatalogOperation` off the UI thread.

    The worker carries a `generation` for the same reason the acquisition worker
    does: the shell must be able to recognise a result it no longer wants — a
    superseded operation, or a profile that has since changed — and drop it
    instead of committing it over newer state.
    """

    progressed = Signal(int, int, str)
    completed = Signal(object)
    cancelled = Signal()

    def __init__(
        self,
        catalog: DbcCatalog,
        operation: CatalogOperation,
        generation: int = 0,
    ) -> None:
        super().__init__()
        # The catalog is copied here, on the calling thread, so the worker never
        # reads a structure the UI thread might mutate underneath it.
        self._catalog = catalog.copy()
        self._operation = operation
        self._generation = generation
        self._cancel_requested = Event()

    @property
    def generation(self) -> int:
        return self._generation

    @property
    def operation(self) -> CatalogOperation:
        return self._operation

    def request_cancel(self) -> None:
        """Ask the worker to stop before it commits anything. Always safe."""
        self._cancel_requested.set()

    def run(self) -> None:
        outcome = apply_catalog_operation(
            self._catalog,
            self._operation,
            progress=self._emit_progress,
            cancelled=self._cancel_requested.is_set,
        )
        if outcome is None:
            self.cancelled.emit()
            return
        self.completed.emit(outcome)

    def _emit_progress(self, done: int, total: int, name: str) -> None:
        self.progressed.emit(done, total, name)
