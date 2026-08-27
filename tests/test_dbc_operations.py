"""item_031 - catalog mutations are prepared without touching live state."""

from pathlib import Path
from threading import Event

from peaklive.analysis import DbcCatalog
from peaklive.services.dbc_worker import (
    CatalogOperation,
    CatalogOperationKind,
    apply_catalog_operation,
)

VEHICLE_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 291 VehicleStatus: 8 ECU
 SG_ Speed : 0|16@1+ (0.1,0) [0|250] "km/h" ECU
'''

BODY_DBC = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 292 BodyStatus: 8 ECU
 SG_ DoorOpen : 0|1@1+ (1,0) [0|1] "" ECU
'''


def _write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _loaded(tmp_path: Path) -> tuple[DbcCatalog, Path]:
    catalog = DbcCatalog()
    path = _write(tmp_path, "vehicle.dbc", VEHICLE_DBC)
    catalog.load(path)
    return catalog, path


def test_copy_is_independent_of_the_catalog_it_came_from(tmp_path):
    catalog, _ = _loaded(tmp_path)
    duplicate = catalog.copy()

    duplicate.remove(catalog.definitions[0].content_hash)

    assert len(catalog.definitions) == 1
    assert not duplicate.definitions


def test_a_prepared_load_never_mutates_the_live_catalog(tmp_path):
    catalog = DbcCatalog()
    operation = CatalogOperation(
        kind=CatalogOperationKind.LOAD,
        paths=(_write(tmp_path, "vehicle.dbc", VEHICLE_DBC),),
    )

    outcome = apply_catalog_operation(catalog, operation)

    assert not catalog.definitions
    assert len(outcome.view.definitions) == 1
    assert outcome.view.signal_names == ("VehicleStatus.Speed",)


def test_a_prepared_remove_never_mutates_the_live_catalog(tmp_path):
    catalog, _ = _loaded(tmp_path)
    content_hash = catalog.definitions[0].content_hash

    outcome = apply_catalog_operation(
        catalog, CatalogOperation(kind=CatalogOperationKind.REMOVE, content_hash=content_hash)
    )

    assert len(catalog.definitions) == 1
    assert not outcome.view.definitions
    assert outcome.removed_path is not None


def test_a_malformed_file_does_not_abandon_the_rest_of_the_selection(tmp_path):
    broken = _write(tmp_path, "broken.dbc", "this is not a DBC file")
    good = _write(tmp_path, "body.dbc", BODY_DBC)

    outcome = apply_catalog_operation(
        DbcCatalog(), CatalogOperation(kind=CatalogOperationKind.LOAD, paths=(broken, good))
    )

    assert outcome.added_paths == (good,)
    assert len(outcome.errors) == 1
    failed_path, message = outcome.errors[0]
    assert failed_path == broken
    assert "DBC" in message
    assert outcome.view.signal_names == ("BodyStatus.DoorOpen",)


def test_cancelling_before_commit_yields_nothing(tmp_path):
    cancelled = Event()
    cancelled.set()

    outcome = apply_catalog_operation(
        DbcCatalog(),
        CatalogOperation(
            kind=CatalogOperationKind.LOAD,
            paths=(_write(tmp_path, "vehicle.dbc", VEHICLE_DBC),),
        ),
        cancelled=cancelled.is_set,
    )

    assert outcome is None


def test_the_view_carries_the_derived_data_the_panels_need(tmp_path):
    catalog = DbcCatalog()
    outcome = apply_catalog_operation(
        catalog,
        CatalogOperation(
            kind=CatalogOperationKind.LOAD,
            paths=(
                _write(tmp_path, "vehicle.dbc", VEHICLE_DBC),
                _write(tmp_path, "body.dbc", BODY_DBC),
            ),
        ),
    )
    view = outcome.view

    assert len(view.definitions) == 2
    assert len(view.references) == 2
    assert view.conflicts == ()
    assert view.unresolved_conflicts == ()
    assert all(view.is_enabled(definition.content_hash) for definition in view.definitions)
    assert sum(view.signal_counts.values()) == 2


def test_disabling_is_prepared_without_dropping_the_definition(tmp_path):
    catalog, _ = _loaded(tmp_path)
    content_hash = catalog.definitions[0].content_hash

    outcome = apply_catalog_operation(
        catalog,
        CatalogOperation(
            kind=CatalogOperationKind.ENABLE, content_hash=content_hash, enabled=False
        ),
    )

    assert len(outcome.view.definitions) == 1
    assert not outcome.view.is_enabled(content_hash)
    assert outcome.view.signal_names == ()
    # The live catalog still decodes against the enabled database.
    assert catalog.is_enabled(content_hash)


def test_progress_reports_each_file_then_completion(tmp_path):
    seen: list[tuple[int, int, str]] = []

    apply_catalog_operation(
        DbcCatalog(),
        CatalogOperation(
            kind=CatalogOperationKind.LOAD,
            paths=(
                _write(tmp_path, "vehicle.dbc", VEHICLE_DBC),
                _write(tmp_path, "body.dbc", BODY_DBC),
            ),
        ),
        progress=lambda done, total, name: seen.append((done, total, name)),
    )

    assert seen == [(0, 2, "vehicle.dbc"), (1, 2, "body.dbc"), (2, 2, "")]
