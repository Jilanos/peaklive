# ADR 0003: Isolate hardware behind a capability-driven adapter boundary

- Status: Accepted
- Date: 2026-08-22

## Context

The MVP targets the currently connected Classic USB CAN adapter, but later
versions may support other models, CAN FD, and multiple channels. Driver APIs
vary in channel discovery, timestamp precision, listen-only behaviour, error
reporting, and reconnect semantics.

## Decision

Define a `CanAdapter` port in the domain layer. Each implementation reports
capabilities, enumerates channels, validates configuration, owns its native
driver handle, and emits normalized frames and bus events. No UI or recorder
module may call a vendor API directly.

The MVP adapter uses the installed Windows vendor API through python-can and
supports one Classic CAN channel. A deterministic fake adapter and a timed
replay adapter are required before hardware-dependent UI work.

Controller configuration distinguishes normal receive, passive listen-only,
and future transmit-enabled modes. Unsupported settings are rejected rather
than silently approximated.

## Consequences

- Additional hardware can be added without forking the UI or capture format.
- Capability differences stay visible to users and tests.
- Some low-level features may require a thin vendor-specific extension beyond
  python-can; it remains contained inside the adapter implementation.
- Bitrate scan results are advisory and must include confidence and failure
  reasons, especially for quiet or acknowledgement-dependent buses.

