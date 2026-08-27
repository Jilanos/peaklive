"""The operator-facing build identity, resolved from one authoritative source.

An operator testing a copied executable needs to answer one question without a
network, a console, or a file manager: *which build am I running?* That answer
is `build_identifier()`, and it is derived here so the package metadata, the
window chrome, the About dialog, and the packaged executable cannot drift apart.

The identifier is `<version>` for a plain build and `<version>+<tag>` for a
rebuild produced for operator testing. The tag is *baked in* at package time —
written to `peaklive/_build.py` by the build script — rather than read from the
environment at run time, because an environment variable on the test machine
says nothing about which executable was actually built.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from peaklive._version import __version__

#: The convention for a test rebuild tag: `b` followed by a UTC timestamp, as
#: produced by the Windows build script. Documented in docs/build-identity.md.
BUILD_TAG_PREFIX = "b"


def base_version() -> str:
    """The declared package version, without any build tag."""
    return __version__


def build_tag() -> str:
    """The baked-in build tag, or an empty string for an untagged build."""
    try:
        from peaklive._build import BUILD_TAG  # type: ignore[attr-defined]
    except ImportError:
        return ""
    return str(BUILD_TAG).strip()


def build_identifier() -> str:
    """The full identifier shown to the operator, e.g. `0.1.0+b202608271530`."""
    tag = build_tag()
    return f"{base_version()}+{tag}" if tag else base_version()


def is_frozen() -> bool:
    """Whether this is running from a packaged executable rather than source."""
    return bool(getattr(sys, "frozen", False))


@dataclass(frozen=True, slots=True)
class BuildInfo:
    """Everything the About dialog states about the running build."""

    identifier: str
    base_version: str
    build_tag: str
    packaged: bool

    @property
    def is_test_rebuild(self) -> bool:
        """Whether this build carries a tag distinguishing it from a prior one."""
        return bool(self.build_tag)


def build_info() -> BuildInfo:
    return BuildInfo(
        identifier=build_identifier(),
        base_version=base_version(),
        build_tag=build_tag(),
        packaged=is_frozen(),
    )


if __name__ == "__main__":  # pragma: no cover - the packaged smoke check
    print(build_identifier())
