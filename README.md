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

## License

PeakLive is licensed under the [Apache License 2.0](LICENSE).
