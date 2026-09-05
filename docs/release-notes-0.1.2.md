# PeakLive 0.1.2

This release consolidates the September 2026 remediation wave.

- bounded, recoverable acquisition and replay workflows;
- durable profile storage with schema migration dispatch;
- aggregate identifier diagnostics and live report synthesis;
- explicit Fusion dark palette and interactive control states;
- trace context commands, copy support, and deterministic graph teardown;
- local operational failure logging and injectable recorder workers.

Validation: `QT_QPA_PLATFORM=offscreen uv run python -m pytest` (520 passed)
and `uv run ruff check .`.
