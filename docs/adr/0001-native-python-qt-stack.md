# ADR 0001: Use a native Python and Qt desktop stack

- Status: Accepted
- Date: 2026-08-22

## Context

The product must access a Windows CAN driver reliably, render high-rate live
data, analyze large offline traces, reuse proven Python DBC/data tooling, and
ship as an installable application. The companion browser tool demonstrates the
desired workflows and visual identity but reaches practical compute and memory
limits on large traces.

## Decision

Build PeakLive as a native Python 3.13 application with PySide6. Use pyqtgraph
for live plots, python-can behind an internal port for CAN adapters, cantools
for DBC semantics, and DuckDB/Arrow for large-file analysis and exports. Package
the application and Python runtime as a self-contained Windows distribution.

Do not embed the existing PWA or run a localhost web service. Reuse its product
concepts, interaction patterns, fixtures, and compatible parsing behaviour,
while implementing desktop-native presentation models.

## Consequences

- The team can reuse Python domain knowledge and established trace/DBC tests.
- Native widgets and batched models avoid browser memory and DOM bottlenecks.
- Acquisition and rendering still require strict worker boundaries; using Qt
  does not by itself make per-frame UI updates safe.
- The installer is larger because it bundles Python and Qt.
- Native dependencies, LGPL obligations, and third-party notices must be
  handled explicitly in packaging.
- If future measured workloads exceed this architecture, hot paths can move
  behind the same ports into a native extension without redesigning the UI.

