from peaklive.services.lifecycle import AcquisitionLifecycle, AcquisitionPhase


def _running() -> AcquisitionLifecycle:
    lifecycle = AcquisitionLifecycle()
    generation = lifecycle.begin()
    lifecycle.advance(generation, AcquisitionPhase.RUNNING)
    return lifecycle


def test_a_fresh_lifecycle_is_idle_and_startable():
    lifecycle = AcquisitionLifecycle()

    assert lifecycle.phase is AcquisitionPhase.IDLE
    assert lifecycle.can_start
    assert not lifecycle.can_stop
    assert lifecycle.settled


def test_each_start_opens_a_new_generation():
    lifecycle = AcquisitionLifecycle()

    first = lifecycle.begin()
    lifecycle.advance(first, AcquisitionPhase.STOPPED)
    second = lifecycle.begin()

    assert second == first + 1
    assert lifecycle.phase is AcquisitionPhase.STARTING


def test_a_generation_settles_exactly_once():
    lifecycle = _running()
    generation = lifecycle.generation

    assert lifecycle.advance(generation, AcquisitionPhase.STOPPED)
    # A duplicate finish, or a late failure, must not reopen a settled result.
    assert not lifecycle.advance(generation, AcquisitionPhase.STOPPED)
    assert not lifecycle.advance(generation, AcquisitionPhase.FAILED)
    assert lifecycle.phase is AcquisitionPhase.STOPPED


def test_a_stale_generation_cannot_change_the_phase():
    lifecycle = _running()

    assert not lifecycle.advance(lifecycle.generation - 1, AcquisitionPhase.STOPPED)
    assert lifecycle.phase is AcquisitionPhase.RUNNING


def test_phases_never_step_backwards():
    lifecycle = _running()
    generation = lifecycle.generation
    lifecycle.advance(generation, AcquisitionPhase.STOPPING)

    assert not lifecycle.advance(generation, AcquisitionPhase.RUNNING)
    assert not lifecycle.advance(generation, AcquisitionPhase.STARTING)
    assert lifecycle.phase is AcquisitionPhase.STOPPING


def test_a_timed_out_shutdown_is_degraded_but_not_settled():
    lifecycle = _running()
    generation = lifecycle.generation
    lifecycle.advance(generation, AcquisitionPhase.STOPPING)

    assert lifecycle.advance(generation, AcquisitionPhase.TIMED_OUT)
    assert not lifecycle.settled
    # Reopening the channel is unsafe while the previous worker may hold it.
    assert not lifecycle.can_start
    assert not lifecycle.can_stop

    # A worker that lands late still settles its own generation.
    assert lifecycle.advance(generation, AcquisitionPhase.STOPPED)
    assert lifecycle.settled
    assert lifecycle.can_start


def test_starting_from_a_live_generation_is_refused():
    lifecycle = _running()

    assert not lifecycle.can_start
    try:
        lifecycle.begin()
    except RuntimeError:
        pass
    else:  # pragma: no cover - the guard is the point of the test
        raise AssertionError("begin() must refuse a second live generation")


def test_a_failed_generation_is_startable_again():
    lifecycle = AcquisitionLifecycle()
    generation = lifecycle.begin()

    lifecycle.advance(generation, AcquisitionPhase.FAILED)

    assert lifecycle.settled
    assert lifecycle.can_start


def test_reset_abandons_the_generation_without_a_terminal_result():
    lifecycle = _running()
    abandoned = lifecycle.generation

    lifecycle.reset()

    assert lifecycle.phase is AcquisitionPhase.IDLE
    assert not lifecycle.accepts(abandoned)
    assert not lifecycle.advance(abandoned, AcquisitionPhase.STOPPED)
