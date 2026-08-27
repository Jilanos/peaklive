"""The acquisition lifecycle contract shared by the worker and the shell.

The rules that keep a slow or blocking driver from corrupting the UI state live
here, in plain Python, so they can be tested without a Qt event loop:

- every Start opens a new *generation*, and a signal that names an older
  generation is ignored rather than allowed to re-enable controls;
- a generation settles exactly once, so a duplicate finish, a late failure, or
  a close-window race cannot produce two terminal results;
- a shutdown that overruns its bounded interval becomes an observable
  ``timed_out`` phase, which is degraded but *not* settled: the worker may still
  land later and settle the generation properly.
"""

from __future__ import annotations

from enum import StrEnum


class AcquisitionPhase(StrEnum):
    """Every observable state of one acquisition generation."""

    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FINALIZING = "finalizing"
    STOPPED = "stopped"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


#: Phases from which a new acquisition may be opened. ``TIMED_OUT`` is absent on
#: purpose: a worker that never returned may still hold the driver, so the safe
#: operator action is to close the application, not to reopen the channel.
STARTABLE_PHASES = frozenset(
    {AcquisitionPhase.IDLE, AcquisitionPhase.STOPPED, AcquisitionPhase.FAILED}
)

#: Phases during which Stop is meaningful.
STOPPABLE_PHASES = frozenset({AcquisitionPhase.STARTING, AcquisitionPhase.RUNNING})

#: Phases that end a generation for good.
SETTLED_PHASES = frozenset({AcquisitionPhase.STOPPED, AcquisitionPhase.FAILED})

#: Phases in which the worker is still doing shutdown work.
SHUTDOWN_PHASES = frozenset({AcquisitionPhase.STOPPING, AcquisitionPhase.FINALIZING})

_ORDER: dict[AcquisitionPhase, int] = {
    AcquisitionPhase.IDLE: 0,
    AcquisitionPhase.STARTING: 1,
    AcquisitionPhase.RUNNING: 2,
    AcquisitionPhase.STOPPING: 3,
    AcquisitionPhase.FINALIZING: 4,
    AcquisitionPhase.TIMED_OUT: 5,
    AcquisitionPhase.STOPPED: 6,
    AcquisitionPhase.FAILED: 6,
}


class AcquisitionLifecycle:
    """Track the phase of the current acquisition generation."""

    def __init__(self) -> None:
        self._generation = 0
        self._phase = AcquisitionPhase.IDLE
        self._settled = True

    @property
    def generation(self) -> int:
        return self._generation

    @property
    def phase(self) -> AcquisitionPhase:
        return self._phase

    @property
    def can_start(self) -> bool:
        return self._phase in STARTABLE_PHASES

    @property
    def can_stop(self) -> bool:
        return self._phase in STOPPABLE_PHASES

    @property
    def is_shutting_down(self) -> bool:
        return self._phase in SHUTDOWN_PHASES

    @property
    def settled(self) -> bool:
        """True once the current generation has reached a terminal result."""
        return self._settled

    def accepts(self, generation: int) -> bool:
        """Whether a signal naming `generation` still describes the live work."""
        return generation == self._generation and not self._settled

    def begin(self) -> int:
        """Open the next generation, or raise if one is still in flight."""
        if not self.can_start:
            raise RuntimeError(f"Cannot start acquisition from phase {self._phase}")
        self._generation += 1
        self._phase = AcquisitionPhase.STARTING
        self._settled = False
        return self._generation

    def advance(self, generation: int, phase: AcquisitionPhase) -> bool:
        """Apply a phase change, reporting whether it was accepted.

        A stale generation, a settled generation, or a backwards step is
        rejected. Backwards steps are not an error: Qt delivers queued signals
        from a thread that has already been abandoned.
        """
        if not self.accepts(generation):
            return False
        if _ORDER[phase] <= _ORDER[self._phase] and phase is not self._phase:
            return False
        if phase is self._phase:
            return False
        self._phase = phase
        if phase in SETTLED_PHASES:
            self._settled = True
        return True

    def reset(self) -> None:
        """Abandon the current generation without settling it as a real result.

        Used when the window is closing: the shell stops caring about the
        worker, and any signal it still emits names a generation nobody accepts.
        """
        self._generation += 1
        self._phase = AcquisitionPhase.IDLE
        self._settled = True
