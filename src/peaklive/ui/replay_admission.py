"""Ordered, nonblocking admission of replay batches into the session.

A replay worker parses far faster than historical persistence can commit, so
something has to absorb the difference. It used to be `HistoryWriter.submit`,
which blocks its caller while the bounded write queue is full - and the caller
is the GUI thread, inside the same slot that drains a batch. A slow but
perfectly healthy disk therefore stalled the event loop for as long as the
queue took to drain (item_143).

Admission is checked here instead, before each submission rather than once per
batch: a mixed frame/event batch submits once per frame group, so one check up
front cannot keep the later groups off the blocking path. When there is no
room the batch goes back at the head of the queue with the exact record index
to resume from, and its worker permit stays held - so nothing is acknowledged
early, nothing is projected twice, and source order is preserved across the
deferral.
"""

from __future__ import annotations

from itertools import groupby
from time import monotonic

from peaklive.domain import BusEvent
from peaklive.i18n import translate
from peaklive.services.history_writer import QUEUE_STALL_TIMEOUT_S
from peaklive.services.replay_worker import ReplayWorker

#: Turnaround between replay drain turns: long enough to yield to the event
#: loop, short enough that presentation keeps up with the worker's permits.
REPLAY_PRESENTATION_POLL_MS = 1

#: Turnaround when a batch was deferred because historical persistence had no
#: queue room. One display frame, so a full queue is re-asked at a bounded
#: cadence instead of in a busy retry loop.
REPLAY_BACKPRESSURE_POLL_MS = 16


class WorkspaceReplayAdmission:
    """Feeds parsed replay batches to ingestion at the rate persistence allows."""

    def _replay_records_for_generation(
        self, generation: int, worker: ReplayWorker, records: list[object]
    ) -> None:
        if generation != getattr(self, "_replay_generation", 0):
            return
        self._pending_replay_batches.append((generation, worker, records, 0))
        if not self._replay_presentation_timer.isActive():
            self._schedule_replay_drain()

    def _drain_replay_batch(self) -> None:
        """Ingest one worker batch, then yield before accepting the next one.

        A historical-persistence failure discovered while ingesting (either
        synchronously, or asynchronously once the background writer reports
        it) is handled entirely inside `_fail_history`: it stops and abandons
        the worker and routes through `_replay_failed_for_generation` itself,
        which also empties `_pending_replay_batches`. So by the time this
        resumes below, a fresh failure already looks like an ordinary empty,
        not-yet-succeeded queue - `_replay_ready_to_complete` correctly
        declines to complete it.
        """
        if not self._pending_replay_batches:
            return
        generation, worker, records, cursor = self._pending_replay_batches.pop(0)
        if generation == getattr(self, "_replay_generation", 0):
            resumed = self._ingest_replay_records(records, cursor)
            if self._history_failed:
                return
            if resumed < len(records):
                self._pending_replay_batches.insert(0, (generation, worker, records, resumed))
                if self._note_replay_backpressure():
                    return
                self._schedule_replay_drain(REPLAY_BACKPRESSURE_POLL_MS)
                return
        self._note_replay_progress()
        worker.batch_rendered()
        if self._pending_replay_batches:
            self._schedule_replay_drain()
        elif self._replay_ready_to_complete(generation, worker):
            self._complete_replay(generation)

    def _schedule_replay_drain(self, delay_ms: int = REPLAY_PRESENTATION_POLL_MS) -> None:
        """Arm the next drain turn, yielding to the event loop in between.

        A deferred batch waits a display frame rather than the immediate
        turnaround: re-asking a full writer queue every millisecond would spin
        the GUI thread for no admission it could not have had one frame later.
        """
        self._replay_presentation_timer.start(delay_ms)

    def _note_replay_progress(self) -> None:
        self._history_backpressure_since = None

    def _note_replay_backpressure(self) -> bool:
        """Bound a non-draining writer without ever waiting on the GUI thread.

        The budget measures absence of durable progress, not elapsed load
        time: a slow but progressing writer resets it every time a batch
        settles, so a legitimately long load stays valid. Returns whether the
        writer was failed, in which case `_fail_history` has already emptied
        the queue and there is nothing left to reschedule.
        """
        settled = self._history_batches_settled
        now = monotonic()
        if self._history_backpressure_since is None or settled != self._replay_backpressure_mark:
            self._replay_backpressure_mark = settled
            self._history_backpressure_since = now
            return False
        if now - self._history_backpressure_since < QUEUE_STALL_TIMEOUT_S:
            return False
        self._history_backpressure_since = None
        self._fail_history(
            translate("trace.history_queue_stalled").format(seconds=int(QUEUE_STALL_TIMEOUT_S))
        )
        return True

    def _ingest_replay_records(self, records: list[object], start: int = 0) -> int:
        """Ingest one ordered replay batch from `start`, in source frame/event order.

        Returns the index of the first record this call did not consume:
        `len(records)` when the whole batch was ingested, and a smaller index
        when historical persistence has no queue room for the next frame
        group. A mixed batch submits once per frame group, so checking
        capacity once for the whole batch would not keep the later groups off
        the blocking path; deferring at an exact record index instead lets the
        caller resume without re-projecting anything already applied.
        """
        ingested_frames = False
        cursor = start
        for is_event, group in groupby(
            records[start:], key=lambda record: isinstance(record, BusEvent)
        ):
            chunk = list(group)
            if is_event:
                for event in chunk:
                    self._render_replay_event(event)
            else:
                if not self._history_ready_for_batch():
                    break
                self._ingest_frames(chunk, coalesce=True)
                ingested_frames = True
                if self._history_failed:
                    cursor += len(chunk)
                    break
            cursor += len(chunk)
        if ingested_frames:
            self._mark_graphs_dirty()
        return cursor

    def _history_ready_for_batch(self) -> bool:
        """Whether one more historical submission can avoid waiting on this thread.

        The GUI thread is the only producer, so room observed here is still
        there for the submission that follows. A failed or absent writer also
        reports ready: `_ingest_frames` skips or refuses such a write outright,
        and that refusal is the caller's terminal signal rather than a stall.
        """
        writer = self._history_writer
        return writer is None or self._history_failed or writer.has_room()

    def _clear_pending_replay_batches(self) -> None:
        timer = getattr(self, "_replay_presentation_timer", None)
        if timer is not None:
            timer.stop()
        self._pending_replay_batches = []
