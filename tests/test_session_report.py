from peaklive.analysis.session import DbcSummary, ReportRenderer, SessionFacts
from peaklive.domain import BusEvent, CanFrame


def test_facts_summarize_volumes_coverage_and_anomalies():
    facts = SessionFacts()
    facts.reset("vehicle.asc")
    facts.record_frame(CanFrame(1.0, 0x123, b"\x01"), decoded=True)
    facts.record_frame(CanFrame(2.0, 0x123, b"\x02"), decoded=True)
    facts.record_frame(CanFrame(3.0, 0x456, b"\x03"), decoded=False)
    facts.record_event(BusEvent(3.5, "replay_anomaly", "Line 9: unsupported record"))
    facts.record_anomaly("dbc_conflict")

    report = facts.report(
        (DbcSummary("vehicle.dbc", "abcd1234", True, 12, (0x123,)),)
    )

    assert report.source == "vehicle.asc"
    assert report.frame_count == 3
    assert report.event_count == 1
    assert report.duration == 2.5
    assert report.frames_per_second == 1.2
    assert report.decode_coverage == 2 / 3
    assert report.top_arbitration_ids == ((0x123, 2), (0x456, 1))
    assert dict(report.anomalies) == {
        "dbc_conflict": 1,
        "replay_anomaly": 1,
        "unknown_id": 1,
    }
    assert not report.is_empty


def test_per_id_tracking_stays_bounded_and_says_so():
    facts = SessionFacts(max_tracked_ids=2)
    for arbitration_id in (0x100, 0x101, 0x102, 0x103):
        facts.record_frame(CanFrame(0.0, arbitration_id, b""), decoded=True)

    report = facts.report()

    assert report.tracked_id_count == 2
    assert report.truncated_ids


def test_empty_session_reports_an_explicit_empty_state():
    report = SessionFacts().report()

    assert report.is_empty
    assert report.duration == 0.0
    assert report.frames_per_second == 0.0
    assert report.decode_coverage == 0.0
    assert "no sample captured" in ReportRenderer(report).render()


def test_rendered_report_matches_the_collected_facts():
    facts = SessionFacts()
    facts.reset("live")
    facts.record_frame(CanFrame(0.0, 0x200, b"\x01"), decoded=True)
    facts.record_event(BusEvent(1.0, "error_frame", "ErrorFrame"))

    text = ReportRenderer(
        facts.report((DbcSummary("body.dbc", "beef0001", False, 4),))
    ).render()

    assert "PeakLive session report" in text
    assert "Source: live" in text
    assert "Frames: 1" in text
    assert "Decode coverage: 100.0%" in text
    assert "body.dbc [beef0001] disabled, 4 signals" in text
    assert "0x200  1" in text
    assert "Bus error frames: 1" in text
