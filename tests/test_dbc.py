import pytest

from peaklive.analysis import AmbiguousMessageError, DbcCatalog
from peaklive.analysis.dbc import _UNRESOLVED
from peaklive.domain import CanFrame

DBC = """VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 291 VehicleStatus: 8 ECU
 SG_ Speed : 0|16@1+ (0.1,0) [0|250] "km/h" ECU
"""

CONFLICTING_DBC = """VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 291 OtherStatus: 8 ECU
 SG_ Temperature : 0|8@1+ (1,0) [0|255] "degC" ECU
"""


def test_catalog_decodes_dbc_signals(tmp_path):
    path = tmp_path / "vehicle.dbc"
    path.write_text(DBC, encoding="utf-8")
    catalog = DbcCatalog()
    catalog.load(path)

    decoded = catalog.decode(CanFrame(1.0, 291, b"\xd2\x04" + b"\x00" * 6))

    assert [(sample.signal_name, sample.value, sample.unit) for sample in decoded] == [
        ("Speed", 123.4, "km/h")
    ]


def test_catalog_loads_cp1252_dbc_text(tmp_path):
    path = tmp_path / "vehicle_cp1252.dbc"
    path.write_bytes(DBC.replace("km/h", "°C").encode("cp1252"))
    catalog = DbcCatalog()

    catalog.load(path)
    decoded = catalog.decode(CanFrame(1.0, 291, b"\xd2\x04" + b"\x00" * 6))

    assert decoded[0].unit == "°C"


def test_catalog_requires_explicit_resolution_for_non_equivalent_messages(tmp_path):
    first = tmp_path / "first.dbc"
    second = tmp_path / "second.dbc"
    first.write_text(DBC, encoding="utf-8")
    second.write_text(CONFLICTING_DBC, encoding="utf-8")
    catalog = DbcCatalog()
    first_definition = catalog.load(first)
    catalog.load(second)
    frame = CanFrame(1.0, 291, b"\x00" * 8)

    with pytest.raises(AmbiguousMessageError):
        catalog.decode(frame)

    catalog.resolve(291, first_definition.content_hash)
    assert catalog.decode(frame)[0].message_name == "VehicleStatus"


def test_repeated_decode_of_a_known_id_reuses_the_cached_lookup(tmp_path, monkeypatch):
    path = tmp_path / "vehicle.dbc"
    path.write_text(DBC, encoding="utf-8")
    catalog = DbcCatalog()
    catalog.load(path)
    frame = CanFrame(1.0, 291, b"\xd2\x04" + b"\x00" * 6)
    resolves: list = []
    original = catalog._resolve_candidate
    monkeypatch.setattr(
        catalog, "_resolve_candidate", lambda arb_id: (resolves.append(True), original(arb_id))[1]
    )

    for _ in range(5):
        catalog.decode(frame)

    assert len(resolves) == 1
    assert catalog._decode_cache[291][0] is catalog.definitions[0]


def test_repeated_decode_of_an_unknown_id_avoids_rebuilding_candidates(tmp_path, monkeypatch):
    path = tmp_path / "vehicle.dbc"
    path.write_text(DBC, encoding="utf-8")
    catalog = DbcCatalog()
    catalog.load(path)
    frame = CanFrame(1.0, 0x7FF, b"\x00" * 8)
    has_message_calls: list = []
    original = DbcCatalog._has_message
    monkeypatch.setattr(
        DbcCatalog,
        "_has_message",
        staticmethod(
            lambda database, arb_id: (has_message_calls.append(True), original(database, arb_id))[1]
        ),
    )

    for _ in range(10):
        assert catalog.decode(frame) == []

    # One membership check per loaded definition on the first call, none after.
    assert len(has_message_calls) == 1
    assert catalog._decode_cache[0x7FF] is _UNRESOLVED


def test_a_sustained_conflict_still_raises_every_call_but_is_cached_between_them(
    tmp_path, monkeypatch
):
    first = tmp_path / "first.dbc"
    second = tmp_path / "second.dbc"
    first.write_text(DBC, encoding="utf-8")
    second.write_text(CONFLICTING_DBC, encoding="utf-8")
    catalog = DbcCatalog()
    catalog.load(first)
    catalog.load(second)
    frame = CanFrame(1.0, 291, b"\x00" * 8)
    resolves: list = []
    original = catalog._resolve_candidate
    monkeypatch.setattr(
        catalog, "_resolve_candidate", lambda arb_id: (resolves.append(True), original(arb_id))[1]
    )

    for _ in range(5):
        with pytest.raises(AmbiguousMessageError):
            catalog.decode(frame)

    # The expensive candidate/fingerprint rebuild happened once; every call
    # still raised, satisfying callers that must see the conflict each time.
    assert len(resolves) == 1
    assert isinstance(catalog._decode_cache[291], AmbiguousMessageError)


def test_loading_a_new_dbc_invalidates_a_cached_unknown_id(tmp_path):
    path = tmp_path / "vehicle.dbc"
    path.write_text(DBC, encoding="utf-8")
    catalog = DbcCatalog()
    catalog.load(path)
    other = tmp_path / "unrelated.dbc"
    other.write_text(CONFLICTING_DBC.replace("291", "292"), encoding="utf-8")

    # Cached as unresolved before anything defines arbitration ID 292 ...
    assert catalog.decode(CanFrame(1.0, 292, b"\x00" * 8)) == []

    catalog.load(other)

    # ... and must not stay stuck unresolved once a DBC covering it loads.
    assert catalog.decode(CanFrame(1.0, 292, b"\x00" * 8))[0].signal_name == "Temperature"


def test_removing_a_dbc_invalidates_the_decode_cache(tmp_path):
    path = tmp_path / "vehicle.dbc"
    path.write_text(DBC, encoding="utf-8")
    catalog = DbcCatalog()
    definition = catalog.load(path)
    frame = CanFrame(1.0, 291, b"\xd2\x04" + b"\x00" * 6)
    assert catalog.decode(frame)

    catalog.remove(definition.content_hash)

    assert catalog.decode(frame) == []


def test_catalog_lists_signals_by_dbc_and_ignores_disabled_conflicts(tmp_path):
    first = tmp_path / "first.dbc"
    second = tmp_path / "second.dbc"
    first.write_text(DBC, encoding="utf-8")
    second.write_text(CONFLICTING_DBC, encoding="utf-8")
    catalog = DbcCatalog()
    first_definition = catalog.load(first)
    second_definition = catalog.load(second)

    assert [conflict.arbitration_id for conflict in catalog.conflicts()] == [291]
    assert [reference.display_name for reference in catalog.signal_references()] == [
        "VehicleStatus.Speed",
        "OtherStatus.Temperature",
    ]

    catalog.set_enabled(second_definition.content_hash, False)

    assert catalog.conflicts() == ()
    assert catalog.is_enabled(first_definition.content_hash)
    assert not catalog.is_enabled(second_definition.content_hash)
    assert catalog.decode(CanFrame(1.0, 291, b"\xd2\x04" + b"\x00" * 6))[0].value == 123.4
