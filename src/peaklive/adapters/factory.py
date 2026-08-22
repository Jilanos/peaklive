"""Select the live adapter without leaking vendor concerns into the UI."""

from __future__ import annotations

import os
import platform

from peaklive.adapters.base import CanAdapter
from peaklive.adapters.fake import FakeCanAdapter
from peaklive.adapters.pcan import PcanAdapter


def default_adapter() -> CanAdapter:
    """Use PCAN on Windows; retain an explicit simulation escape hatch."""
    if os.environ.get("PEAKLIVE_ADAPTER", "").lower() == "fake":
        return FakeCanAdapter()
    if platform.system() == "Windows":
        return PcanAdapter()
    return FakeCanAdapter()
