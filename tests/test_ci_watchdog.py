"""A stalled test must fail before the outer GitHub job timeout."""

import os
import subprocess
import sys


def test_native_pytest_watchdog_exits_and_reports_a_stalled_test(tmp_path):
    stalled = tmp_path / "test_stalled.py"
    stalled.write_text(
        "from threading import Event\n"
        "def test_stalled():\n"
        "    Event().wait()\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest", str(stalled), "-vv",
            "-o", "faulthandler_timeout=0.5",
            "-o", "faulthandler_exit_on_timeout=true",
        ],
        cwd=tmp_path,
        env={**os.environ, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
        capture_output=True,
        text=True,
        timeout=15,
    )

    assert result.returncode == 1
    assert "test_stalled.py::test_stalled" in result.stdout
    assert "Timeout" in result.stderr
    assert "test_stalled.py" in result.stderr
