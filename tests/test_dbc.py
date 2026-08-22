import pytest

from peaklive.analysis import AmbiguousMessageError, DbcCatalog
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
