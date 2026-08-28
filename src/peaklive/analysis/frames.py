"""The bounded raw-frame retention that makes later signal selection possible.

A session decodes only the signals that were selected while it ingested, so a
signal chosen afterwards has no history to show. Keeping the raw frames — the
cheapest complete representation of what the session actually read — lets that
signal be derived from the loaded session instead of from a second pass over
the file. The retention is bounded and says so: a capture larger than the cache
reports exactly how much of its head is no longer available.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable, Iterator

from peaklive.domain import CanFrame

#: Raw frames retained for on-demand decoding.
#:
#: One `CanFrame` is small, and this bound is deliberately larger than the
#: trace buffer's: the trace is a display projection, whereas this is the
#: material a newly selected signal is rebuilt from.
DEFAULT_FRAME_CACHE_CAPACITY = 50_000


class FrameCache:
    """A bounded chronological window over the frames a session ingested."""

    __slots__ = ("_capacity", "_first_index", "_frames", "_ingested")

    def __init__(self, capacity: int = DEFAULT_FRAME_CACHE_CAPACITY) -> None:
        if capacity < 1:
            raise ValueError("A frame cache needs room for at least one frame")
        self._capacity = capacity
        self._frames: deque[CanFrame] = deque(maxlen=capacity)
        self._ingested = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def ingested(self) -> int:
        """Every frame the session ever added, retained or not."""
        return self._ingested

    @property
    def dropped(self) -> int:
        """Frames the bound has already discarded from the head."""
        return self._ingested - len(self._frames)

    @property
    def truncated(self) -> bool:
        """Whether a derived signal would be missing the start of the session."""
        return self.dropped > 0

    def __len__(self) -> int:
        return len(self._frames)

    def __iter__(self) -> Iterator[CanFrame]:
        return iter(self._frames)

    def extend(self, frames: Iterable[CanFrame]) -> None:
        for frame in frames:
            self._frames.append(frame)
            self._ingested += 1

    def clear(self) -> None:
        self._frames.clear()
        self._ingested = 0

    def snapshot(self) -> tuple[CanFrame, ...]:
        """A stable copy safe to hand to a worker thread."""
        return tuple(self._frames)

    def frames_after(self, ingested: int) -> tuple[CanFrame, ...]:
        """Return the frames added after the cache had ingested `ingested`.

        A backfill decodes a snapshot off the UI thread while ingestion may
        still be running. This is how the commit closes that gap exactly: the
        delta is decoded in the foreground, so the rebuilt series is neither
        short of the newest samples nor holding any of them twice.
        """
        pending = self._ingested - max(ingested, self.dropped)
        if pending <= 0:
            return ()
        retained = len(self._frames)
        return tuple(self._frames)[retained - min(pending, retained) :]
