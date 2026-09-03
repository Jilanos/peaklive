"""item_052 coverage: the owned PeakLive icon, from source asset to package."""

from __future__ import annotations

import struct
from pathlib import Path

from PySide6.QtGui import QIcon

from peaklive.adapters import FakeCanAdapter
from peaklive.app import apply_application_identity
from peaklive.resources import APPLICATION_ICON, application_icon_path, resource_path
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow

REPOSITORY = Path(__file__).resolve().parents[1]
EXPECTED_SIZES = {16, 24, 32, 48, 64, 128, 256}


def test_the_owned_icon_asset_ships_in_the_source_tree():
    icon = application_icon_path()
    source = resource_path("peaklive.svg")

    assert icon.name == APPLICATION_ICON
    assert icon.is_file() and icon.stat().st_size > 0
    assert source.is_file()
    assert "<svg" in source.read_text(encoding="utf-8")
    # Ownership and regeneration are documented next to the asset itself.
    assert "generate_icon.py" in resource_path("README.md").read_text(encoding="utf-8")


def test_the_icon_carries_every_size_windows_chrome_asks_for():
    raw = application_icon_path().read_bytes()
    reserved, kind, count = struct.unpack_from("<HHH", raw, 0)

    assert (reserved, kind) == (0, 1)
    sizes = set()
    for index in range(count):
        width, height = struct.unpack_from("<BB", raw, 6 + 16 * index)
        sizes.add(256 if width == 0 else width)
        assert (width == 0) == (height == 0)
    assert sizes == EXPECTED_SIZES


def test_a_frozen_build_resolves_the_asset_under_the_extraction_root(monkeypatch, tmp_path):
    monkeypatch.setattr("peaklive.resources._PACKAGE_DIRECTORY", tmp_path / "absent")
    monkeypatch.setattr("sys._MEIPASS", str(tmp_path), raising=False)

    resolved = resource_path(APPLICATION_ICON)

    assert resolved == tmp_path / "peaklive" / "resources" / APPLICATION_ICON


def test_the_application_is_badged_before_any_window_is_built(qapp, qtbot, tmp_path):
    icon = apply_application_identity(qapp)

    assert isinstance(icon, QIcon)
    assert not icon.isNull()
    assert not qapp.windowIcon().isNull()
    assert qapp.applicationName() == "PeakLive"
    assert {size.width() for size in qapp.windowIcon().availableSizes()} == EXPECTED_SIZES

    window = MainWindow(ProfileStore(tmp_path), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)

    # A window with no icon of its own shows the application's.
    assert not window.windowIcon().isNull()
    assert not window.windowIcon().pixmap(32, 32).isNull()


def test_the_windows_package_embeds_the_same_icon_and_ships_the_resources():
    spec = (REPOSITORY / "peaklive.spec").read_text(encoding="utf-8")

    assert "resources/*" in spec
    assert 'peaklive.ico' in spec
    assert "icon=ICON" in spec
