"""Qt-independent, collision-safe recording filename resolution and reservation.

The naming policy is deliberately kept out of Qt and out of the ASC/TRC
writer: a pure service can be tested with plain filesystem fixtures and a
clock injected instead of touching wall time, and it stays the single place
that knows the placeholder grammar, the sanitisation rule, and the atomic
reservation contract that ``AcquisitionSession`` relies on to make an
overwrite impossible.
"""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from peaklive.domain import RecordingSettings

#: The only placeholders a template may reference, with the numeric ones
#: additionally accepting a Python-compatible zero-padded width, e.g.
#: ``{iteration:03d}`` or ``{iteration:03}``.
_TOKEN_PATTERN = re.compile(r"\{([A-Za-z_]+)(?::([^{}]*))?\}")
_NUMERIC_FIELDS = frozenset({"iteration", "segment"})
_TEXT_FIELDS = frozenset({"date", "time", "profile", "text"})
_KNOWN_FIELDS = _NUMERIC_FIELDS | _TEXT_FIELDS
_NUMERIC_SPEC = re.compile(r"^0\d{1,6}d?$")

DEFAULT_CAPTURE_DIRECTORY = Path.home() / "Documents" / "PeakLive" / "Captures"

#: What ``{text}`` expands to when the operator left the label empty, or typed
#: only characters a filename cannot carry. A fixed word rather than an empty
#: string keeps the separators in the template meaningful and keeps the
#: resulting basename stable, which the reservation search relies on.
EMPTY_TEXT_COMPONENT = "unnamed"


#: Upper bound on candidates a single reservation search will try before
#: giving up. Without a bound, a filename template that never varies between
#: attempts (no ``{iteration}``/``{text}``/``{time}``) combined with a
#: permanently blocked candidate spins the search forever.
_MAX_RESERVATION_ATTEMPTS = 10000


class InvalidTemplateError(ValueError):
    """A filename template is malformed, unsupported, empty, or path-escaping."""


class ReservationExhaustedError(RuntimeError):
    """No free candidate was found within :data:`_MAX_RESERVATION_ATTEMPTS`."""


class ReservationCancelledError(RuntimeError):
    """A caller-supplied ``stop_requested`` check cancelled the search."""


@dataclass(frozen=True, slots=True)
class Reservation:
    """One exclusively-owned, not-yet-written capture target."""

    final_path: Path
    partial_path: Path
    event_final_path: Path
    event_partial_path: Path
    marker_path: Path
    iteration: int
    next_iteration: int

    def release(self) -> None:
        """Give up an unused reservation. Safe to call more than once."""
        self.marker_path.unlink(missing_ok=True)


class RecordingNaming:
    """Resolves, previews, and atomically reserves recording filenames."""

    def __init__(self, clock: Callable[[], datetime] | None = None) -> None:
        self._clock = clock or (lambda: datetime.now().astimezone())

    def validate_template(self, template: str) -> None:
        """Raise :class:`InvalidTemplateError` for anything unsafe or unsupported."""
        if not template or not template.strip():
            raise InvalidTemplateError("Filename template cannot be empty.")
        if "\x00" in template:
            raise InvalidTemplateError("Filename template contains a null character.")
        if "/" in template or "\\" in template:
            raise InvalidTemplateError("Filename template cannot contain path separators.")
        if ".." in template:
            raise InvalidTemplateError("Filename template cannot contain '..'.")

        literal = _TOKEN_PATTERN.sub("", template)
        if literal != re.sub(r"[{}]", "", literal):
            raise InvalidTemplateError("Filename template has an unmatched '{' or '}'.")

        for name, spec in _TOKEN_PATTERN.findall(template):
            if name not in _KNOWN_FIELDS:
                raise InvalidTemplateError(f"Unsupported placeholder: {{{name}}}.")
            if spec and name not in _NUMERIC_FIELDS:
                raise InvalidTemplateError(f"Placeholder {{{name}}} does not accept a format spec.")
            if spec and not _NUMERIC_SPEC.match(spec):
                raise InvalidTemplateError(
                    f"Unsupported format spec for {{{name}:{spec}}}; "
                    "use a zero-padded numeric width such as {iteration:03d}."
                )

    def expand(
        self,
        template: str,
        *,
        profile_name: str,
        now: datetime,
        iteration: int,
        segment: int,
        capture_format: str,
        text: str = "",
    ) -> str:
        """Expand a validated template into a bare filename below any directory."""
        self.validate_template(template)
        values = {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H-%M-%S"),
            "profile": _sanitize_component(profile_name, "measurement"),
            "text": _sanitize_component(text, EMPTY_TEXT_COMPONENT),
            "iteration": max(1, iteration),
            "segment": max(1, segment),
        }
        filename = template.format(**values)
        return str(Path(filename).with_suffix(f".{capture_format}"))

    def preview(
        self,
        settings: RecordingSettings,
        profile_name: str,
        *,
        now: datetime | None = None,
        iteration: int | None = None,
        segment: int = 1,
    ) -> str:
        """Return the filename acquisition would use now, without touching disk."""
        moment = now or self._clock()
        return self.expand(
            settings.filename_template,
            profile_name=profile_name,
            now=moment,
            iteration=settings.iteration if iteration is None else iteration,
            segment=segment,
            capture_format=settings.capture_format,
            text=settings.text,
        )

    def resolve_directory(self, settings: RecordingSettings) -> Path:
        return Path(settings.directory) if settings.directory else DEFAULT_CAPTURE_DIRECTORY

    def reserve(
        self,
        settings: RecordingSettings,
        profile_name: str,
        *,
        now: datetime | None = None,
        stop_requested: Callable[[], bool] | None = None,
    ) -> Reservation:
        """Search from the persisted iteration and atomically own the first free one.

        A candidate is free only when no final, partial, or reservation
        artifact already claims it. Ownership is taken with an exclusive
        ``O_CREAT | O_EXCL`` marker create, which is atomic even against a
        second process or a second instance of this service racing the same
        directory.

        The search is bounded to :data:`_MAX_RESERVATION_ATTEMPTS` candidates
        and raises :class:`ReservationExhaustedError` rather than spinning
        forever. When the template doesn't discriminate between attempts
        (e.g. it has no ``{iteration}``/``{text}``/``{time}`` placeholder),
        a numeric suffix is appended so each attempt still tries a distinct
        candidate. If ``stop_requested`` is given and returns ``True``, the
        search stops early with :class:`ReservationCancelledError`.
        """
        directory = self.resolve_directory(settings)
        directory.mkdir(parents=True, exist_ok=True)
        moment = now or self._clock()
        iteration = max(1, settings.iteration)
        previous_base: str | None = None
        for attempt in range(1, _MAX_RESERVATION_ATTEMPTS + 1):
            if stop_requested is not None and stop_requested():
                raise ReservationCancelledError(
                    "Recording-name reservation was cancelled before a candidate was claimed."
                )
            base = self.expand(
                settings.filename_template,
                profile_name=profile_name,
                now=moment,
                iteration=iteration,
                segment=1,
                capture_format=settings.capture_format,
                text=settings.text,
            )
            filename = base if base != previous_base else _suffixed(base, attempt)
            previous_base = base
            final_path = directory / filename
            partial_path = final_path.with_suffix(final_path.suffix + ".partial")
            marker_path = final_path.with_suffix(final_path.suffix + ".reserved")
            if final_path.exists() or partial_path.exists() or marker_path.exists():
                iteration += 1
                continue
            try:
                fd = os.open(marker_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                iteration += 1
                continue
            os.close(fd)
            event_final = final_path.with_suffix(".peaklive-events.jsonl")
            return Reservation(
                final_path=final_path,
                partial_path=partial_path,
                event_final_path=event_final,
                event_partial_path=event_final.with_suffix(event_final.suffix + ".partial"),
                marker_path=marker_path,
                iteration=iteration,
                next_iteration=iteration + 1,
            )
        raise ReservationExhaustedError(
            f"Could not reserve a free recording name in {directory} after "
            f"{_MAX_RESERVATION_ATTEMPTS} attempts."
        )


def _suffixed(filename: str, attempt: int) -> str:
    """Disambiguate a filename that repeated between two search attempts."""
    path = Path(filename)
    return str(path.with_name(f"{path.stem}-{attempt}{path.suffix}"))


def _sanitize_component(value: str, fallback: str) -> str:
    """Reduce free operator text to one safe, deterministic filename component.

    Anything outside the conservative set becomes an underscore, so a path
    separator, a traversal, or a shell character cannot survive into a
    filename; an empty result falls back rather than collapsing separators
    the template author placed deliberately.
    """
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._") or fallback
