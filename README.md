# PeakLive

PeakLive is a Windows desktop CAN workstation for a small engineering team. It
captures a Classic CAN bus through a USB adapter, decodes DBC signals, renders
live traces and plots, records lossless ASC sessions, and replays ASC/TRC files.

The MVP is deliberately receive-only at the application level. Transmission is
reserved for a later version, while the design already distinguishes normal
receive mode (the controller may acknowledge valid frames) from true passive
listen-only mode.

## MVP capabilities

- installable, self-contained Windows 10/11 x64 application with an English UI;
- one Classic USB CAN channel, with a vendor-neutral adapter boundary;
- manual 125/250/500/1000 kbit/s selection and an optional assisted bitrate scan;
- named measurement profiles containing bus, DBC, favorites, plots, filters,
  and recording settings, with the last profile selected at startup;
- explicit **Start Acquisition** and **Stop Acquisition** controls;
- robust connect, disconnect, error-state, and reconnect handling;
- chronological live trace with display-only filtering;
- complete recording of frames and acquisition events to ASC plus metadata;
- one or more DBC files, deterministic conflict handling, and live decoding;
- selectable real-time signal plots with bounded memory;
- ASC and supported text TRC replay;
- CSV/Parquet export of selected decoded signals;
- local-only data and settings, with no cloud dependency.

## Analyst workspace

- a frame inspector driven by the trace row you select: identity, raw payload,
  resolved message, decode status, and every decoded physical signal;
- stacked plots on a shared time axis with zoom, pan, fit, grid, follow-live,
  and A/B cursors that stay where you put them during a live acquisition;
- a measurement table combining the value at each cursor with the A-B range
  statistics (count, min, max, mean, standard deviation, RMS), and a value
  distribution for enumerated signals;
- display-only trace filtering by ID, message, signal, direction, event kind,
  decode status, and time range, with removable active-filter chips;
- configurable trace columns - visibility, order, width, and value format
  (seconds, hexadecimal, decimal, binary, status) - persisted per profile;
- CSV and Parquet export over the A-B range, the visible window, or the full
  retained buffer, streamed and cancellable;
- a session diagnostic report: volumes, frames per second, decode coverage,
  loaded DBCs, top arbitration IDs, and anomalies by type;
- a bus-state indicator and explicit empty, error, and loading states in every
  panel, including recording disk warnings.

### Keyboard

| Shortcut | Action |
| --- | --- |
| `F5` / `F6` | Start / stop acquisition |
| `Ctrl+D` | Load DBC files |
| `Ctrl+O` | Open an ASC or TRC trace |
| `Ctrl+E` | Export selected signals |
| `Ctrl+1` / `Ctrl+2` | Place cursor A / cursor B |
| `Ctrl+0` | Fit the graphs to the full extent |
| `Ctrl+F` | Focus the trace filter |
| `Ctrl+B` | Collapse or expand the signals panel |
| `F11` | Fullscreen |
| `Ctrl+Q` | Quit |

Every actionable control carries a tooltip and an accessible name, and the
layout is verified at 1024x768, 1280x720, and 1600x900.

## Documentation

- [Product scope](docs/product-scope.md)
- [Architecture](docs/architecture.md)
- [ADR 0001: Native Python and Qt stack](docs/adr/0001-native-python-qt-stack.md)
- [ADR 0002: Lossless recording and bounded projections](docs/adr/0002-lossless-recording-bounded-projections.md)
- [ADR 0003: Hardware adapter boundary](docs/adr/0003-hardware-adapter-boundary.md)

The ready-to-develop workflow is tracked under `logics/`.

## Development

Prerequisites: Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --all-extras
uv run peaklive
uv run ruff check .
uv run pytest
uv build
```

For a headless Qt test session on Linux or CI:

```bash
QT_QPA_PLATFORM=offscreen uv run pytest
```

PeakLive persists profiles below the platform user-data directory. Set
`PEAKLIVE_DATA_DIR` to an explicit local directory for development or tests.
The application restores the last selected profile but never connects to a bus
until **Start Acquisition** is selected.

## Windows build and hardware acceptance

On Windows, run `scripts/build-windows.ps1` from PowerShell. It creates a
self-contained `dist/PeakLive.exe`; the adapter driver itself remains a machine
prerequisite. Follow [Windows hardware acceptance](docs/windows-hardware-acceptance.md)
before declaring a release ready.

## License

PeakLive is licensed under the [Apache License 2.0](LICENSE).
