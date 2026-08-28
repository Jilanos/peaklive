"""On-demand signal decoding after a trace is loaded (req_009, item_037).

Every test opens a synthetic capture once and then behaves like an analyst who
changes their mind about which signal matters. Nothing here may reopen the
file: that is the whole point of the slice.
"""

from __future__ import annotations

from pathlib import Path

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis.benchmark import CaptureProfile, synthetic_dbc, write_synthetic_capture
from peaklive.domain import CanFrame
from peaklive.services.profiles import ProfileStore
from peaklive.services.signal_decode_worker import SignalDecodeWorker, decode_series
from peaklive.ui import MainWindow

CAPTURE = CaptureProfile("lazy", 2_000, message_count=2)

FIRST = "Synth0.Counter0"
SECOND = "Synth1.Level1"


def _workspace(qtbot, tmp_path) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    dbc = tmp_path / "synthetic.dbc"
    dbc.write_text(synthetic_dbc(CAPTURE.message_count), encoding="utf-8")
    window._load_dbc_path(dbc)
    return window


def _capture(tmp_path) -> Path:
    return write_synthetic_capture(tmp_path / "lazy.asc", CAPTURE)


def _load(window: MainWindow, capture: Path, qtbot, *, selected: set[str]) -> None:
    window._selected_signal_names = set(selected)
    window._sync_graphs()
    window._open_trace(capture)
    qtbot.waitUntil(lambda: window._replay_worker is None, timeout=120_000)


def _await_backfill(window: MainWindow, qtbot) -> None:
    qtbot.waitUntil(lambda: window._signal_decode_worker is None, timeout=120_000)


def _samples(window: MainWindow, name: str) -> int:
    series = window._series.series(name)
    return 0 if series is None else len(series)


# --------------------------------------------------------------------------
# AC3 - a signal selected after the load appears without reopening the trace
# --------------------------------------------------------------------------


def test_a_signal_selected_after_the_load_is_derived_from_the_loaded_session(
    qtbot, tmp_path
):
    window = _workspace(qtbot, tmp_path)
    capture = _capture(tmp_path)
    _load(window, capture, qtbot, selected={FIRST})
    assert _samples(window, SECOND) == 0
    opened = window._replay_generation

    window._signal_shown_changed(SECOND, True)
    _await_backfill(window, qtbot)

    assert _samples(window, SECOND) == CAPTURE.frames // CAPTURE.message_count
    # The trace was never reopened: no new replay generation was started.
    assert window._replay_generation == opened
    assert SECOND in window.graph_panel.signal_names


def test_repeated_selection_rebuilds_rather_than_duplicates_the_samples(qtbot, tmp_path):
    window = _workspace(qtbot, tmp_path)
    _load(window, _capture(tmp_path), qtbot, selected={FIRST})

    window._signal_shown_changed(SECOND, True)
    _await_backfill(window, qtbot)
    first_pass = _samples(window, SECOND)
    for _ in range(3):
        window._signal_shown_changed(SECOND, False)
        window._signal_shown_changed(SECOND, True)
        _await_backfill(window, qtbot)

    assert _samples(window, SECOND) == first_pass


def test_deselecting_a_signal_drops_it_without_disturbing_the_session(qtbot, tmp_path):
    window = _workspace(qtbot, tmp_path)
    _load(window, _capture(tmp_path), qtbot, selected={FIRST})
    report_before = window.report_panel.text
    rows_before = window.trace_table.rowCount()

    window._signal_shown_changed(SECOND, True)
    _await_backfill(window, qtbot)
    window._signal_shown_changed(SECOND, False)

    assert _samples(window, SECOND) == 0
    assert _samples(window, FIRST) > 0
    assert window.report_panel.text == report_before
    assert window.trace_table.rowCount() == rows_before


def test_a_signal_already_ingested_live_is_not_decoded_again(qtbot, tmp_path):
    window = _workspace(qtbot, tmp_path)
    _load(window, _capture(tmp_path), qtbot, selected={FIRST})
    before = _samples(window, FIRST)

    window._request_signal_backfill(FIRST)

    assert window._signal_decode_worker is None
    assert _samples(window, FIRST) == before


# --------------------------------------------------------------------------
# AC4 - bounded, deterministic, cancellable, and explicit when unavailable
# --------------------------------------------------------------------------


def test_selecting_a_signal_with_no_retained_session_says_so_plainly(qtbot, tmp_path):
    window = _workspace(qtbot, tmp_path)

    window._signal_shown_changed(SECOND, True)

    assert window._signal_decode_worker is None
    assert SECOND in window.session_note.text()


def test_a_backfill_is_bounded_by_the_retained_frames(qtbot, tmp_path):
    window = _workspace(qtbot, tmp_path)
    window._frames = type(window._frames)(capacity=500)
    _load(window, _capture(tmp_path), qtbot, selected={FIRST})

    window._signal_shown_changed(SECOND, True)
    _await_backfill(window, qtbot)

    assert len(window._frames) == 500
    assert _samples(window, SECOND) <= 500
    # The operator is told the session no longer holds the whole capture.
    assert "no longer held" in window.session_note.text()


def test_a_cancelled_backfill_installs_nothing(qtbot, tmp_path):
    window = _workspace(qtbot, tmp_path)
    _load(window, _capture(tmp_path), qtbot, selected={FIRST})

    window._signal_shown_changed(SECOND, True)
    window._signal_shown_changed(SECOND, False)
    _await_backfill(window, qtbot)

    assert _samples(window, SECOND) == 0
    assert SECOND not in window._selected_signal_names


def test_a_superseded_backfill_result_is_dropped_on_arrival(qtbot, tmp_path):
    window = _workspace(qtbot, tmp_path)
    _load(window, _capture(tmp_path), qtbot, selected={FIRST})
    stale = window._signal_decode_generation

    window._signal_shown_changed(SECOND, True)
    _await_backfill(window, qtbot)
    installed = _samples(window, SECOND)
    # A result from a retired generation must not overwrite the current series.
    window._signal_backfill_completed(stale, _decoded(window, SECOND, ()))

    assert _samples(window, SECOND) == installed


def _decoded(window: MainWindow, name: str, samples):
    from peaklive.services.signal_decode_worker import DecodedSeries

    return DecodedSeries(name, tuple(samples), None, window._frames.ingested, False)


def test_the_worker_decodes_the_same_samples_as_the_live_ingest_path(qtbot, tmp_path):
    window = _workspace(qtbot, tmp_path)
    frames = [
        CanFrame(index * 0.01, 0x301, (index % 256).to_bytes(2, "little") + b"\x00" * 6)
        for index in range(64)
    ]
    worker = SignalDecodeWorker(window._catalog, tuple(frames), SECOND, len(frames))

    with qtbot.waitSignal(worker.completed, timeout=30_000) as blocker:
        worker.start()

    assert blocker.args[0].samples == decode_series(window._catalog, tuple(frames), SECOND)
    assert len(blocker.args[0].samples) == len(frames)
