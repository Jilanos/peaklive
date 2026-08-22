# PeakLive MVP Product Scope

## Purpose

PeakLive is the primary installed workstation for live CAN acquisition and
high-performance trace analysis on Windows. A companion browser-only tool
remains useful for opening shared captures on computers where PeakLive is not
installed.

The initial audience is a team of three engineers. The product must favour
predictable acquisition, transparent state, and recoverable recordings over
decorative dashboard features.

## Primary workflows

### Live acquisition

1. Start PeakLive and inspect detected CAN interfaces.
2. Select or edit a named measurement profile containing the channel,
   controller mode, bitrate, DBCs, favorites, plots, filters, and recording
   policy.
3. Select **Start Acquisition** and see an explicit connection, recording, and
   bus-health state.
4. Observe chronological raw frames and decoded messages.
5. Filter what is displayed without changing what is recorded.
6. Select decoded signals and plot them in real time.
7. Finalize the configured recording with **Stop Acquisition**.
8. Recover cleanly from a dongle disconnect, bus error, or application restart.

### Offline analysis

1. Open an ASC or supported text TRC capture.
2. Load one or more DBC files and resolve conflicting message definitions.
3. Filter and inspect frames, decoded signals, and acquisition errors/events.
4. Plot signals with zoom, pan, and measurement cursors.
5. Export selected decoded data to CSV or Parquet.

## MVP boundaries

Included:

- Windows 10/11 x64 desktop installation for three internal users, with an
  English-only MVP interface;
- one active Classic CAN channel;
- application-level receive-only operation;
- normal receive and passive listen-only controller modes when supported;
- manual 125/250/500/1000 kbit/s selection and an assisted, non-guaranteed
  bitrate scan over the same initial set;
- complete ASC recording with preserved error and connection events;
- ASC and supported text TRC replay;
- multi-DBC decoding, live trace, live plots, and decoded export;
- local settings, recent sessions, and layout persistence;
- named measurement profiles and restoration of the last selected profile;
- a visual language aligned with the companion trace-analysis product.

Excluded from the MVP:

- user-authored frame transmission or cyclic transmission;
- dashboards, gauges, alarms, scripting, and diagnostic protocols;
- cloud storage, telemetry, accounts, and remote collaboration;
- multi-channel synchronized capture;
- CAN FD, LIN, and protocol-specific tooling;
- automatic updates and code-signing infrastructure.
- detachable/multi-monitor panels, while keeping UI ownership boundaries able
  to support them later.

## Measurement profiles and acquisition controls

A named measurement profile stores the selected adapter/channel, bitrate,
controller mode, ordered DBC set and conflict choices, favorites, displayed
signals, graph layout, trace filters, capture directory, recording enablement,
and filename template. The last selected profile is restored and displayed at
startup, but the bus stays disconnected until the user acts.

The MVP uses the unambiguous English labels **Start Acquisition** and **Stop
Acquisition**. Starting acquisition applies the visible profile and, when that
profile enables recording, opens the ASC session as part of the same operation.
Stopping acquisition finalizes it. A monitor-only profile may disable recording.

Recording templates support at least `{date}`, `{time}`, `{profile}`, and a
zero-padded configurable `{iteration}` token. The iteration value is visible
before starting and advances without overwriting an existing capture. The
default template is `{date}_{time}_{profile}_{iteration:03d}.asc`.

## Controller-mode language

The UI must not collapse several safety-relevant concepts into a single
"read-only" label:

- **Receive only (normal controller):** PeakLive exposes no transmit action,
  but the CAN controller may acknowledge valid traffic and participates in bus
  error handling.
- **Passive listen-only:** the controller neither transmits frames nor sends
  acknowledgements; availability depends on adapter capability.
- **Transmit enabled:** reserved for V2 and requires an explicit capability and
  UI safety gate.

The assisted bitrate scan uses passive mode whenever the adapter supports it.
It may fail on a quiet bus or a topology that needs this adapter to provide the
only acknowledgement, so manual selection remains the authoritative path.

## Capture policy

Recording is independent from rendering. Every received data frame, remote
frame, error frame exposed by the driver, and connection/bus-state transition
is queued to a dedicated writer before display filtering. A bounded in-memory
buffer serves the table and plots; it is never the source of truth for a saved
capture.

The primary artifact is an interoperable `.asc` file. Events that cannot be
represented portably in ASC are written both as readable ASC comments and to a
same-basename `.peaklive-events.jsonl` sidecar. Recordings are first created
with a `.partial` marker and finalized atomically so an interrupted session can
be detected and recovered.

## Initial quality targets

- sustain the practical maximum load of one Classic CAN 1 Mbit/s channel for a
  60-minute acceptance run without recorder queue overflow;
- keep the UI responsive while recording and plotting eight selected signals;
- report any driver-side overrun, recorder overflow, malformed record, or
  unsupported event visibly and in the saved session;
- show live data with a typical presentation latency below 250 ms while using
  batched UI updates rather than one UI operation per frame;
- reconnect after a physical adapter disconnect without restarting the app,
  while recording a visible discontinuity event;
- recover a recording interrupted by process termination without silently
  presenting it as a cleanly closed capture.

These are product acceptance targets. Available real ASC files seed realistic
replay tests; deterministic fake-adapter generators provide saturated traffic,
driver overruns, bus-state transitions, disconnects, malformed input, and other
edge cases that are difficult to collect safely on the available bus.
