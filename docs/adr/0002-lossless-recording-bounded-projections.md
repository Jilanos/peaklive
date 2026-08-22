# ADR 0002: Separate lossless recording from bounded live projections

- Status: Accepted
- Date: 2026-08-22

## Context

Display filtering and real-time plotting can fall behind a saturated bus or a
slow workstation. An engineering capture must not silently lose frames because
the user hid an identifier, paused a table, or requested an expensive plot.
Keeping every frame indefinitely in memory is also unsafe.

## Decision

Branch normalized acquisition events to a dedicated recorder before all UI
filters. The recorder writes every available frame and error/state event to an
ASC artifact plus a JSONL event sidecar. The live table and plots consume
bounded, batched projections and may discard old presentation data.

Use partial-session markers and atomic finalization. Any driver overrun or
recorder overflow marks the capture incomplete and remains visible in both the
UI and saved metadata.

## Consequences

- Display filters never affect capture contents.
- Long sessions have bounded application memory.
- The recorder must be benchmarked independently from the UI.
- A capture consists of an ASC file and, when needed, a same-basename metadata
  sidecar; tools that only understand ASC can still read the raw frames.
- "Lossless" is a verified session property, not an unconditional marketing
  claim: upstream driver loss and local overflow are explicitly recorded.

