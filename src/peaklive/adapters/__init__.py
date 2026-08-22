"""CAN adapter ports and deterministic test adapters."""

from .base import CanAdapter
from .fake import FakeCanAdapter

__all__ = ["CanAdapter", "FakeCanAdapter"]
