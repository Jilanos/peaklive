"""Local-only diagnostics for failures that would otherwise vanish in Qt."""

from __future__ import annotations

import logging
import logging.handlers
import os
import sys
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

from platformdirs import user_data_path

from peaklive.version import build_info

LOG_NAME = "peaklive"
LOG_FILENAME = "peaklive.log"
_notifier: Callable[[str], None] | None = None


def log_path() -> Path:
    """Return the local diagnostic path, honouring the testable data override."""
    configured = os.environ.get("PEAKLIVE_DATA_DIR")
    directory = Path(configured) if configured else user_data_path("PeakLive")
    return directory / LOG_FILENAME


def install_exception_hooks(notify: Callable[[str], None] | None = None) -> logging.Logger:
    """Install process and worker hooks before a window can be shown."""
    global _notifier
    _notifier = notify
    result = logging.getLogger(LOG_NAME)
    if not result.handlers:
        path = log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.handlers.RotatingFileHandler(
            path, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(threadName)s %(message)s"
        )
        handler.setFormatter(formatter)
        result.addHandler(handler)
        result.setLevel(logging.INFO)
        result.propagate = False
        result.info("session started build=%s", build_info().identifier)

    def report(kind: str, exc_type: type[BaseException], value: BaseException, trace: Any) -> None:
        result.error("unhandled %s exception", kind, exc_info=(exc_type, value, trace))
        if _notifier is not None:
            _notifier("An unexpected error was recorded in the local diagnostic log.")

    sys.excepthook = lambda exc_type, value, trace: report("process", exc_type, value, trace)
    threading.excepthook = lambda args: report(
        "thread", args.exc_type, args.exc_value, args.exc_traceback
    )
    return result


def set_operator_notifier(notify: Callable[[str], None] | None) -> None:
    global _notifier
    _notifier = notify


def logger() -> logging.Logger:
    return logging.getLogger(LOG_NAME)
