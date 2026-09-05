import pytest

from peaklive.analysis import IdentifierDiagnostics, SessionFacts
from peaklive.domain import CanFrame


def frame(timestamp: float, identifier: int = 0x120) -> CanFrame:
    return CanFrame(timestamp, identifier, b"\x01\x02")


def test_identifier_rows_update_in_constant_time_with_period_and_status():
    diagnostics = IdentifierDiagnostics(bitrate=500_000)
    first = diagnostics.update(frame(1.0), decoded=True)
    second = diagnostics.update(frame(1.2), decoded=True)

    assert first is second
    assert second.count == 2
    assert second.mean_period == pytest.approx(0.2)
    assert second.delta_t == pytest.approx(0.2)
    assert second.decode_status == "decoded"
    assert second.load_contribution is not None


def test_session_facts_exposes_identifier_rows_without_changing_report_contract():
    facts = SessionFacts()
    facts.reset("fixture")
    facts.record_frame(frame(0.0), decoded=False)
    facts.record_frame(frame(0.5), decoded=True)

    report = facts.report()
    row = report.identifier_aggregates[0]
    assert row.arbitration_id == 0x120
    assert row.count == 2
    assert row.mean_period == 0.5
    assert row.decode_status == "partial"
