# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller definition for the Windows x64 PeakLive distribution.

The build identity comes from the same authoritative source the running
application reads, so a packaged executable can never claim a version the
package metadata disagrees with. `peaklive/_build.py` is written by
`scripts/build-windows.ps1` just before this runs; it is imported lazily at run
time, so it has to be named as a hidden import when it exists.
"""

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

sys.path.insert(0, str(Path.cwd() / "src"))
from peaklive.version import build_identifier  # noqa: E402

IDENTIFIER = build_identifier()
print(f"PeakLive build identity: {IDENTIFIER}")

datas = collect_data_files("peaklive", includes=["i18n/*.json", "resources/*"])

# The same generated icon the running application loads, so the executable in
# Explorer and the window it opens cannot show two different marks.
ICON = str(Path.cwd() / "src" / "peaklive" / "resources" / "peaklive.ico")

hiddenimports = ["can.interfaces.pcan"]
if (Path.cwd() / "src" / "peaklive" / "_build.py").exists():
    hiddenimports.append("peaklive._build")

a = Analysis(
    ["src/peaklive/__main__.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    excludes=[
        "_pytest",
        "pytest",
        "pytestqt",
        "setuptools",
        "unittest",
    ],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PeakLive",
    console=False,
    icon=ICON,
)
