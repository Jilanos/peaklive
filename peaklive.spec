# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller definition for the Windows x64 PeakLive distribution."""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("peaklive", includes=["i18n/*.json"])

a = Analysis(
    ["src/peaklive/__main__.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=["can.interfaces.pcan"],
    hookspath=[],
    excludes=[],
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
)
