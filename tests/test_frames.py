"""Regression coverage for the bounded raw-frame cache."""

from peaklive.analysis.frames import FrameCache
from peaklive.domain import CanFrame


def test_frame_cache_discards_the_oldest_frames_after_its_capacity():
    cache = FrameCache(capacity=3)
    cache.extend(CanFrame(index, 0x100, b"") for index in range(5))

    assert [frame.timestamp for frame in cache] == [2.0, 3.0, 4.0]
    assert cache.ingested == 5
    assert cache.dropped == 2
    assert cache.truncated
