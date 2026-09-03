# PeakLive application assets

- `peaklive.svg` — the original PeakLive icon, drawn for this project: a dark
  rounded instrument face carrying a green CAN waveform with a marked peak. It
  contains no third-party logo, trademark, or icon-pack artwork, and it is
  covered by the repository's Apache-2.0 licence like the rest of the source.
- `peaklive.ico` — generated from the SVG by `scripts/generate_icon.py` at 16,
  24, 32, 48, 64, 128, and 256 pixels. Qt loads it for the application and
  window icon, and PyInstaller embeds it in `PeakLive.exe`.

Edit the SVG, then regenerate the ICO; never hand-edit the ICO:

```
uv run python scripts/generate_icon.py
```
