"""item_059 coverage: acquisition ingestion must not drop frames under load.

A saturated bus can queue many worker batches before the 16ms presentation
timer drains them. Facts, the frame cache, the series store, and deferred
decode must still see every one of those frames, whether or not the retained
trace window is large enough to display all of them.
"""

from __future__ import annotations

from peaklive.adapters import FakeCanAdapter
from peaklive.analysis import TraceBuffer
from peaklive.domain import CanFrame
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow


def _window(qtbot, tmp_path) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    return window


def _synthetic_frames(count: int, *, start: int = 0) -> list[CanFrame]:
    return [
        CanFrame((start + index) * 0.001, 0x300, index.to_bytes(2, "little") + b"\x00" * 6)
        for index in range(count)
    ]


def test_a_saturated_acquisition_stream_ingests_every_queued_frame(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._begin_presentation_generation(1)
    batch_count = 20
    for index in range(batch_count):
        window._queue_acquisition_frames(1, _synthetic_frames(64, start=index * 64))
    total_frames = batch_count * 64

    window._drain_presentation_frames()

    assert window._facts.report().frame_count == total_frames
    assert window._frames.ingested == total_frames
    assert len(window._trace) == total_frames


def test_facts_and_cache_see_every_frame_even_when_the_trace_window_is_smaller(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._trace = TraceBuffer(capacity=3)
    window.trace_panel.set_buffer(window._trace)
    window._begin_presentation_generation(1)
    batch_count = 20
    for index in range(batch_count):
        window._queue_acquisition_frames(1, _synthetic_frames(64, start=index * 64))
    total_frames = batch_count * 64

    window._drain_presentation_frames()

    # The retained window is bounded, but every frame still reached facts,
    # the frame cache, and the series projection that feeds deferred decode.
    assert window._facts.report().frame_count == total_frames
    assert window._frames.ingested == total_frames
    assert len(window._trace) == 3


def test_a_generation_change_stops_accepting_the_old_generations_batches(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._begin_presentation_generation(1)
    window._queue_acquisition_frames(1, _synthetic_frames(64))
    window._invalidate_presentation_generation(1)

    window._queue_acquisition_frames(1, _synthetic_frames(64))
    window._drain_presentation_frames()

    assert window._facts.report().frame_count == 0
