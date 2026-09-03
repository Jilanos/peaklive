"""Render the owned PeakLive icon source into the packaged Windows .ico.

The SVG next to the generated file is the drawing of record; this script is
the only supported way to regenerate ``peaklive.ico`` from it, so the runtime
icon, the taskbar icon, and the icon embedded in the executable can never
drift apart. Run it after editing the SVG:

    uv run python scripts/generate_icon.py
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QIODevice, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

#: Windows picks the closest entry it needs from these; 16 to 256 covers the
#: taskbar, the window chrome, Explorer, and the large-icon views.
SIZES = (16, 24, 32, 48, 64, 128, 256)

RESOURCES = Path(__file__).resolve().parents[1] / "src" / "peaklive" / "resources"
SOURCE = RESOURCES / "peaklive.svg"
TARGET = RESOURCES / "peaklive.ico"


def render(renderer: QSvgRenderer, size: int) -> bytes:
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter)
    painter.end()
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    buffer.close()
    return bytes(buffer.data())


def pack(images: list[tuple[int, bytes]]) -> bytes:
    """Assemble PNG-compressed entries into one ICO container."""
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = len(header) + 16 * len(images)
    directory = b""
    payload = b""
    for size, png in images:
        directory += struct.pack(
            "<BBBBHHII",
            0 if size >= 256 else size,
            0 if size >= 256 else size,
            0,
            0,
            1,
            32,
            len(png),
            offset,
        )
        payload += png
        offset += len(png)
    return header + directory + payload


def main() -> int:
    # The instance must stay referenced for the lifetime of the rendering:
    # Qt tears the platform integration down with it.
    app = QGuiApplication.instance() or QGuiApplication(["generate-icon"])
    assert app is not None
    renderer = QSvgRenderer(str(SOURCE))
    if not renderer.isValid():
        raise SystemExit(f"Unreadable icon source: {SOURCE}")
    images = [(size, render(renderer, size)) for size in SIZES]
    TARGET.write_bytes(pack(images))
    print(f"Wrote {TARGET} ({TARGET.stat().st_size} bytes, sizes {', '.join(map(str, SIZES))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
