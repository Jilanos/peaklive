"""A retired test window must not become the next test's collection workload."""

import os
import subprocess
import sys
from pathlib import Path


def test_previous_window_and_its_session_are_released_before_the_next_test(tmp_path):
    # Exercise real pytest fixture/Qt teardown ordering in a fresh process.
    # Keeping only weak references ensures this probe does not retain its own
    # garbage; the window cycle and diagnostic callback come from production.
    conftest = Path(__file__).with_name("conftest.py")
    (tmp_path / "conftest.py").write_text(conftest.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "test_windows.py").write_text(
        """
import weakref

from peaklive.adapters import FakeCanAdapter
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow

retired = []


def test_create_window(qtbot, tmp_path):
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    retired.extend((weakref.ref(window), weakref.ref(window._series)))


def test_next_case_starts_without_the_retired_session():
    assert len(retired) == 2
    assert all(reference() is None for reference in retired)
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(tmp_path)],
        cwd=tmp_path,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
