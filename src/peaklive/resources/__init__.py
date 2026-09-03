"""Packaged, project-owned application assets and how to find them.

Assets are addressed through this module rather than through ``__file__``
arithmetic spread over the codebase, because a frozen PyInstaller build lays
the package data out under its own extraction root. Resolution therefore looks
next to this module first — the source tree and a normal installation — and
falls back to the frozen root, which is where ``peaklive.spec`` places the same
files.
"""

from __future__ import annotations

import sys
from pathlib import Path

__all__ = ["APPLICATION_ICON", "application_icon_path", "resource_path"]

#: The file name of the multi-size Windows icon generated from
#: ``peaklive.svg`` by ``scripts/generate_icon.py``.
APPLICATION_ICON = "peaklive.ico"

_PACKAGE_DIRECTORY = Path(__file__).resolve().parent


def resource_path(name: str) -> Path:
    """Return the packaged asset `name`, from source or from a frozen build."""
    candidate = _PACKAGE_DIRECTORY / name
    if candidate.exists():
        return candidate
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root is not None:
        return Path(frozen_root) / "peaklive" / "resources" / name
    return candidate


def application_icon_path() -> Path:
    """Return the PeakLive application icon used by Qt and by the installer."""
    return resource_path(APPLICATION_ICON)
