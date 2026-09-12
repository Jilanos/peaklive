# Dense historical curves disappearing during zoom-out

## Evidence boundary

Source inspected: `7cc00d63890818055b9840b5cda8828b88004773`, Python 3.13.15,
pyqtgraph 0.14.0 and PySide6 6.11.2. The corresponding CI run
`https://github.com/Jilanos/peaklive/actions/runs/34635167259` succeeded on both
platforms. Passing CI does not establish visual correctness on this capture.

The operator reports three curves from two message groups, roughly 10 ms sample
periods, fluid navigation below about 500 s, and all three curves disappearing
after one horizontal zoom-out step beyond approximately 650 s. One zoom-in step
restores them. The three signals were selected BEFORE loading the capture, so
late-selection backfill is not the reported reproduction path. The operator
typed the build as `v0.1.2 + b20269111856`; keep that verbatim as unverified input,
not a normalized identifier or a proven source mapping. They also requested a
selectable/copyable build identifier to prevent future transcription errors.
Message names, private source paths and payloads are deliberately not recorded
here. The copied build identifier, exact three signal keys, DBC revision and
lane pixel width still need local recording for executable reproduction.

This investigation changes no application code. Reproduce with:

```text
uv run python logics/analysis/dense_overview_probe.py
uv run python logics/analysis/dense_overview_probe.py --capture PRIVATE_ASC
```

The script streams the private source, substitutes synthetic values, and uses
real timestamps from its most frequent frame identity. It exercises the actual
history selector and offscreen PlotDataItem display arrays. It neither decodes
the operator's DBC signals nor reproduces their exact ingest-batch composition.
Qt emitted a missing-font-directory warning; no claim about rendered screenshot
quality or packaged interaction latency is derived from these offscreen probes.

## Reproduced findings

The source contains 1,755,746 CAN frames, 40 channel/identifier/format identities,
and 195,753,923 bytes. The selected diagnostic identity has 94,493 samples over
944.781020 s. It is a density/timestamp surrogate, not a decoded physical signal.

| Probe | Actual result | Meaning |
| --- | --- | --- |
| One bulk append, full real-timestamp range | 3,881 returned/display points; complete endpoints; 226.65 ms isolated query | The existing fallback can downsample this volume; no universal 650 s limit was reproduced. |
| Same data, one final row in a separate append | 7 summary rows; broad query returns only the final sample | A partial summary is accepted as complete history. A one-point line without a marker is visually empty. |
| Same data, final 16 rows in a separate append | Broad query returns 4 points covering only the final 0.149984 s | The result depends on ingestion batch partition, despite identical raw samples. |
| Three points at 944.97/944.98/944.99 s, 0..945 s view, 963 px view width | Automatic peak factor 19; zero display points | The second reducer can erase a nonempty input entirely. |
| Identical three-point input with automatic reduction disabled | Three display points | Disabling the second reducer avoids this erasure, but cannot recover missing summary coverage. |
| Clear a populated, cached store | Exact returns empty; overview still returns previous values | Reset deletes raw rows but leaves summary and overview cache tables. |

Synthetic 100 Hz data reproduces the same batch-dependent coverage defect.
At a 650 s end-aligned viewport, the real-timestamp bulk-only case returns 3,882
points in 167.50 ms; adding a one-row final append instead returns one point in
5.53 ms. The faster result is incorrect. These are single local observations,
not performance budgets or multi-lane latency measurements.

## Mechanism and scope of certainty

1. `HistoricalSignalStore.append_many` updates summaries only when the entire
   decoded batch has at most 32 rows. Larger batches still insert all raw rows
   but skip the summary hierarchy. No coverage/revision marker declares these
   summaries incomplete. The comment promising lazy summary construction is not
   backed by a hierarchy-building path in `overview`.
2. `overview` trusts any nonempty summary query and bypasses the raw fallback.
   A final small batch, or intermittent small batches, can therefore replace
   the whole interval with a few local points. The application batches selected
   decoded signal values together: adding a third lane can cross the 32-row
   threshold even with unchanged underlying CAN traffic.
3. `GraphStackPanel` enables pyqtgraph automatic peak downsampling on every
   curve, including source-reduced historical results. The installed renderer
   estimates average X spacing, computes a reduction factor from viewport span
   and pixel width, then forms `len(x) // factor` peak groups. A factor larger
   than the surviving input produces zero groups and an empty display array.
   Single samples, clipped sparse coverage and already-reduced extrema need an
   explicit display contract; a count assertion on input alone cannot detect
   this failure.
4. The selected summary level, exact/overview mode, surviving timestamp span,
   pixel width and wheel-step size affect the transition. There is no 650 s
   constant in the inspected graph path. The two defects are proven and form a
   plausible explanation for reversible zoom-out disappearance. Their exact
   contribution to the operator's three curves at 650 s remains an executable
   reproduction requirement, not an established numerical threshold.

The current exact selector uses an 8% duration fraction and a 20,000-sample cap.
It falls back to overview on overflow. At 100 Hz, 650 s is about 65,000 samples,
but this does not prove a 65,536-point renderer limit: historical display is
already capped near 4,000 points, and no such renderer cap was found in the app.

## Comparison with the reference application

Local reference checkout: `CanTraceDiag`, inspected read-only. Relevant files
within that checkout are `src/cantracediag/store.py` (`signal_series`, `_decimate`),
`src/cantracediag/web/js/signals.js` and `src/cantracediag/web/js/plot.js`.

Its series request counts raw samples in the selected window, sets a point
budget from plot width (approximately two points per pixel, bounded 500..20,000),
and reduces by time buckets in DuckDB. Bucket extrema retain source timestamps;
the returned values are sorted chronologically. The response carries both
`raw_count` and `downsampled`. The canvas draws that prepared result as a
sample-and-hold line and labels the reduction state. It does not apply
pyqtgraph's second automatic reducer.

Reuse these contracts, not its browser/server architecture. PeakLive already
has Python, Qt, pyqtgraph and SQLite; neither DuckDB migration nor canvas/WebView
is required. The reference's GROUP BY query still scans its window; copying it
would not prove bounded indexed work. Min/max alone does not guarantee original
first/last coverage or preservation of every digital transition. Its async
functions mutate shared series before checking the final token, so do not copy
that race into PeakLive. No license file was identified at the inspected root;
do not copy source verbatim without confirming reuse rights.

## Proposed development design

### Correctness patch first

- Track a per-signal/data-revision summary completeness watermark, or invalidate
  every affected level whenever maintenance is skipped. Never choose a partial
  level merely because it contains rows. Until rebuilding completes, use a
  cancellable worker fallback over authoritative raw data and show its state.
- Make summary results independent of append batching (1/16/32/33/256/4096 and
  mixed final batches), including multi-signal batches. Preserve first/last and
  per-bucket extrema; refine partial boundary buckets against source data.
- Make reset atomic across samples, summaries, cached bounds, overview cache
  and revision identity. Prevent stale in-memory results crossing reset/reload.
- Historical envelopes arrive pre-reduced: disable secondary automatic
  downsampling explicitly, restoring the live policy when changing modes.
  Handle one-point data, gaps and zero-width ranges deliberately; do not invent
  samples to make a line visible. Test display arrays and actual visual output.

### Operator-confirmed fidelity priority

The operator explicitly prioritizes peaks and rare changes, including an error
asserted for only two 10 ms samples, to find precise timecodes for investigation.
Uniform stride sampling and averaging are unacceptable. Preserving extrema is
necessary but not sufficient: a short event that is not a bucket minimum or
maximum can still disappear in a plain envelope.

For discrete/error-code signals, preserve transition/event anchors independently
of the analog envelope and retain original timecodes for zoom/detail retrieval.
When several anchors collide in one pixel or exceed the display budget, use an
explicit clustered activity marker with count/range and drill-down; never silently
discard their existence or claim every event is individually distinguishable.
For analog signals, retain first/min/max/last source samples and local-change
activity. The operator clarified two mandatory examples: a binary signal staying
at zero for 50,000 frames then asserting for four frames, and an allowed-current
signal falling from 250 A to 180 A for 100 ms before returning. At 100 Hz these
are respectively four samples over 40 ms and ten samples over 100 ms. Keep the
earlier one/two-sample cases as additional adversarial tests.

The `nonextreme_short_dip` probe confirms this limitation: 1,000 synthetic
100 Hz samples contain a 250 A baseline, a 100 A dip and a separate 180 A dip,
each lasting 100 ms. With a four-point overview budget, the current store
returns only `(0, 250)`, `(1, 100)` and `(9.99, 250)`; the 180 A event vanishes.
This is a deliberately small-budget counterexample, not a measurement of the
operator's real decoded current signal.

Preserve the entry, local extremum and recovery timecodes of short plateau
excursions via run-boundary/local-extremum anchors, even when another event in
the same large bucket has a larger amplitude. No configured amplitude threshold
is required for these explicitly accepted cases. Generic noisy analog signals
can generate many changes: group their presentation with truthful activity
metadata rather than claiming a universal semantic anomaly detector. Domain-
specific threshold classification is future scope and must be explicit.
An event marker represents activity, not an invented physical sample.

### Sustainable indexed path

- Build/maintain a complete disk-backed first/min/max/last hierarchy in bounded
  batches. Reader connections remain read-only. Publish a level only for a
  committed source/data revision. Specify progress, cancellation and disk-full
  behavior; do not make 7 per-sample SQL loops the ingestion hot path.
- Choose exact/envelope using density, coverage and available pixels, with
  hysteresis. Proposed historical budget: `min(4000, max(256, 4 * width_px))`;
  source exact cap stays 20,000. Reserve slots before reduction, never truncate
  late buckets. No averaging of sharp diagnostic peaks.
- Return immutable request metadata: session/data/DBC identity, signal keys,
  requested range, width, budget, detail mode, coverage, counts and status.
  Statuses distinguish exact, overview, empty, incomplete, cancelled and error.
- Enforce one active and one replaceable pending viewport request. Cancel within
  long SQL/reduction work, retain the last valid curve while pending, and publish
  only the latest matching request. A cache hit must also obsolete an in-flight
  incompatible request. Cache keys must be the request keys, not reconstructed
  from whatever viewport exists at callback time.
- Cache extents and enforce a byte budget (proposed 64 MiB total). Correct cache
  replacement accounting; current hits increment the point counter again.
  Wire worker errors into a nonmodal, accessible state through existing i18n.

### Analytical and UX guardrails

Downsampling is display-only. Exact analytical values and exports must never
use an envelope as if it were original evidence. Current historical A/B code
can exceed its cap, omit a lane or fall back to the retained tail; report this
as incomplete/unavailable until a correct source-backed calculation exists.
Do not broaden export coverage claims beyond the product's existing contract.
Viewport-only changes must not trigger unchanged/hidden A/B SQL on the GUI thread.

The operator's busy cursor is an observation, not an attributed cause. No
explicit busy/wait cursor setter was found in the inspected application path.
Global bounds still run SQL synchronously, and every completed viewport dirties
measurements. Instrument request counts, GUI heartbeat and pending operation
ownership before deciding whether the pointer reflects OS scheduling, redundant
queries, or another action. A modal/global busy state is inappropriate for a
background viewport request that keeps the UI usable.

## Questions, defaults and technical debt

### Additional operator reproduction: selection after loading

The operator subsequently supplied a screenshot showing a blank newly selected
signal and a retained-frame warning reporting 1,705,746 discarded earlier
frames. The private signal identifier and screenshot are not committed.
The capture census (1,755,746 frames) minus that count is exactly 50,000,
matching `DEFAULT_FRAME_CACHE_CAPACITY` in `analysis/frames.py`. This is the
shared CAN-frame cache limit, not 50,000 samples of the selected signal, and
does not imply deletion from the source ASC file.

`WorkspaceIngest._pump_signal_backfill` passes only `_frames.snapshot()` to
`SignalDecodeWorker`. Its completion installs samples in `_series` but never
in `_history`. The truncation warning is emitted after the nonempty sample
check: this application path can therefore warn even though decoding succeeded.
Historical rendering queries `_history`; `curve_points` falls back to `_series`
only for unavailable history (`None`), not an empty historical query. The
asynchronous historical viewport path similarly reads only the history store.
These source-level facts explain how successfully decoded tail samples can
still yield a blank historical lane. This is separate from the original
before-load selection / zoom-out failure; the screenshot does not establish
that the two have the same cause.

Recommended follow-up: for file replay, derive a newly selected signal from
the complete source in a bounded, cancellable background pass, publish its
historical samples and summaries with explicit coverage, invalidate stale
empty results, and preserve viewport/other lanes. Missing or changed source,
DBC changes, deselection, reset and shutdown need explicit handling. Do not
solve this by retaining unlimited frames in RAM or reloading the whole UI.
Until that preparation is available, a retained-tail preview must be labelled
partial and must not masquerade as a full-history result. Live acquisition
without a persisted source cannot promise reconstruction of discarded frames.
The operator has been asked whether to accept full-file preparation latency;
this scope choice is pending, not silently added to the implementation contract.

| Decision or missing fact | Proposed handling | Blocking scope |
| --- | --- | --- |
| Exact build, three signal identities, DBC revision and viewport width | Before-load selection confirmed; build string supplied but transcription uncertain. Record locally and redact private identities. | Required for operator-specific executable qualification, not for reproduced unit-level fixes. |
| Preserve extrema/transitions versus add oscillation-density rendering | Confirmed binary four-frame pulses after 50,000 quiet frames and 250 A to 180 A dips lasting 100 ms, plus earlier two-frame errors. Preserve run-boundary/extremum anchors; uniform stride is excluded. | No unresolved semantic choice for these cases; general threshold anomaly classification is out of scope. |
| Signals selected after the file loads | Now a second confirmed operator scenario; screenshot count matches the 50,000-frame cache and source inspection finds no history publication. See the diagnosis above. | Full-file reconstruction versus explicitly partial preview is awaiting the operator's choice. |
| Digital/enum signals and gaps | Preserve true transitions and gaps within the budget; mark approximation when transitions exceed it. Never coerce enum evidence to fabricated numeric zero. | Confirm representative signal types before visual qualification. |
| Index preparation and temporary disk allowance | Permit visible cancellable preparation; measure cost and footprint before fixing a production quota. Preserve last valid display and source on failure. | Needed for shipping resource guarantees, not the first coverage patch. |
| Existing task 025 marked Done while its stronger guarantees are not implemented | Record corrective follow-up and new behavioral evidence. Do not rewrite old proof or consider a green CI equivalent to operator acceptance. | New task cannot close before packaged qualification. |

Small authorized UX companion: make the existing build label selectable with
mouse and keyboard and copyable as exact text, read-only, using the canonical
`build_info().identifier`. Preserve layout and accessibility; no versioning
scheme change. Relevant code: `src/peaklive/ui/main_window.py` and
`tests/test_ui_build_identity.py`.

Technical debt to address in this chain: incomplete summary publication; stale
reset caches; double reduction; callback/cache generation races; weak query
cancellation; GUI-bound bounds/measurement reads; no worker-failure presentation;
and coverage-blind tests. Track full-file late-selection decoding separately
unless the operator opts it into this correction.

## Qualification and completion gates

Deterministic tests must combine three lanes, 1/10/100 ms and irregular timing,
constant/digital/analog signals, the two operator-confirmed pulse/dip cases,
late spikes, gaps, duplicates, empty intervals,
mixed append batches and reset/reload with reused signal names. Sweep 500, 640,
650, 660, 800 s and full capture; also test synthetic threshold cases at multiple
pixel widths. Assert raw coverage, envelope coverage, finite chronological
timestamps, peak preservation and nonempty rendered paths whenever data should
be visible. Test out-of-order completions and cache-hit A/B/A navigation.

For indexed history, prove query work scales with pixel budget rather than raw
sample count (10x duration comparison). Proposed reference-machine gates reuse
the existing product targets: warm settled viewport <=250 ms, cold indexed
query <=1 s, 20 ms heartbeat p95 lateness <=50 ms and maximum <=150 ms. Report
indexing separately. Tests must not loosen budgets silently or imply a single
local timing is a guarantee on every runner.

Final qualification requires Linux/Windows CI including Windows packaging, and
an identified Windows executable on the operator's private trace with the three
original signals and reversible wheel steps around the reported boundary.
An unavailable build/DBC/private reproduction stays explicitly outstanding;
do not mark the task complete using option flags, source-only tests or a queued
CI run as substitutes.
