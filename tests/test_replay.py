from peaklive.analysis import iter_trace
from peaklive.domain import BusEvent, CanFrame


def test_streams_asc_and_preserves_error_and_malformed_records(tmp_path):
    trace = tmp_path / "trace.asc"
    trace.write_text(
        "date Tue Jul 15 10:00:00 2026\n"
        "   0.000000 1  123             Rx   d 2 01 02\n"
        "   0.010000 1  ErrorFrame\n"
        "   0.020000 1  123             Rx   d 2 01\n",
        encoding="utf-8",
    )

    records = list(iter_trace(trace))

    assert isinstance(records[0], CanFrame)
    assert records[0].data == b"\x01\x02"
    assert isinstance(records[1], BusEvent) and records[1].kind == "error_frame"
    assert isinstance(records[2], BusEvent) and records[2].kind == "replay_anomaly"


def test_streams_supported_text_trc(tmp_path):
    trace = tmp_path / "trace.trc"
    trace.write_text("; PCAN-View\n1) 15.0 Rx 18FEF100x 2 AA 55\n", encoding="utf-8")

    records = list(iter_trace(trace))

    assert len(records) == 1
    assert isinstance(records[0], CanFrame)
    assert records[0].timestamp == 0.015
    assert records[0].is_extended_id is True


def test_honours_declared_decimal_asc_base(tmp_path):
    trace = tmp_path / "decimal.asc"
    trace.write_text(
        "date Tue Jul 15 10:00:00 2026\n"
        "base dec  timestamps absolute\n"
        "   0.000000 1  291             Rx   d 2 10 255\n",
        encoding="utf-8",
    )

    records = list(iter_trace(trace))

    assert len(records) == 1
    assert isinstance(records[0], CanFrame)
    assert records[0].arbitration_id == 291
    assert records[0].data == b"\x0a\xff"
