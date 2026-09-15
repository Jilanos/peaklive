"""Run pytest with an external deadline, including native/interpreter teardown."""

import subprocess
import sys


def run(args: list[str], timeout: float = 300) -> int:
    process = subprocess.Popen([sys.executable, "-m", "pytest", *args])
    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"pytest exceeded {timeout}s: {args}", file=sys.stderr, flush=True)
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                check=False, timeout=15,
            )
        process.kill()
        process.wait(timeout=15)
        return 124


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
