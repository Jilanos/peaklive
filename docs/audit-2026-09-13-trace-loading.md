# Incremental audit: trace loading and historical storage

## Scope and baseline

Reviewed application revision `cc75668`, following the last independent review
`a4a4bbf` (2026-09-07, captured in the second-pass review request): 93 intervening
commits and 191 changed files. The original September audit and subsequent
historical zoom/dense-overview diagnoses were checked as an exclusion list.
This is an incremental review, with instrumented trace-loading investigation;
it is not a line-by-line recertification of every unchanged module.

The second-pass delivery already introduced bounded live ingestion, transactional
exports, collision protection, complete CAN identity and qualified signal keys.
Those fixes are not reported again as new defects. Recent changes concentrate
on SQLite history, asynchronous reconstruction/navigation, workspace geometry,
and Windows qualification. Current history and replay behavior warrants further
correction even though focused and general regression tests exist.

Only audit evidence and Logics planning documents are changed. Pre-existing
deleted files under `logics/external` are unrelated operator changes and are
excluded from commits. No private capture or DBC contents were used. No Windows
or PCAN execution was performed; repository records of earlier Windows runs
are historical evidence, not a qualification of this revision.

## Measurement method

Reproduce from the repository root:

```sh
QT_QPA_PLATFORM=offscreen uv run --python 3.13 python logics/analysis/trace_load_followup_probe.py --frames 20000 --signals 0 1 8 16
QT_QPA_PLATFORM=offscreen uv run --python 3.13 python logics/analysis/trace_load_followup_probe.py --frames 200000 --signals 0 1 8 16
QT_QPA_PLATFORM=offscreen uv run --python 3.13 python logics/analysis/trace_load_followup_probe.py --faults
```

The probe creates temporary synthetic ASC and DBC files, runs the actual window
replay path, times `HistoricalSignalStore.append_many` separately, inspects
SQLite row/file counts, and removes its own temporary evidence. Eight CAN
messages each contain two signals; sixteen selected signals therefore produce
two historical samples per source frame. Selection is deterministic. Zero
selected signals still exercises DBC decoding and the raw preview.

Initial measurements below used Linux, Python 3.13, offscreen Qt, an unshown
window, and the enabled profiler. The full test suite was also running, so
these are diagnostic observations, not an isolated reference-machine benchmark.
Wall time ends after replay finalization, not after every asynchronous viewport
worker has painted. Maximum `processEvents` duration is a responsiveness proxy,
not a native Windows input-latency measurement. Stage durations can overlap
across threads; do not subtract their sum from elapsed time or infer CPU shares.
Environment: Linux x86_64, Python 3.13.15, PySide6 6.11.2, pyqtgraph 0.14.0,
cantools 43.0.0.

| Frames | Selected signals | Load seconds | History seconds | Slowest event pass ms | SQLite bytes |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20,000 | 0 | 0.7970 | 0.0001 | 153.811 | 57,344 |
| 20,000 | 1 | 0.9051 | 0.0991 | 147.664 | 2,351,104 |
| 20,000 | 8 | 1.5454 | 0.6033 | 216.887 | 18,513,920 |
| 20,000 | 16 | 2.7116 | 1.2289 | 318.993 | 36,851,712 |
| 200,000 | 0 | 6.0476 | 0.0009 | 133.709 | 57,344 |
| 200,000 | 1 | 7.3978 | 1.0041 | 133.343 | 22,777,856 |
| 200,000 | 8 | 13.8231 | 6.2783 | 346.366 | 186,400,768 |
| 200,000 | 16 | 21.9811 | 12.5650 | 487.384 | 370,114,560 |

All eight loads succeeded, dispatched the expected frame count, and ended with
zero pending frame batches. The 200k ASC file is 9,490,094 bytes. With sixteen
signals its history contains 400,000 samples, 355,584 summary rows and 400,000
event anchors: about 39 times the source bytes, excluding transient journals.
This ratio depends on signal density and content; it is not a universal forecast.

Ten warm repetitions of `bounds()` plus `data_revision()` average 2.692, 25.705
and 52.146 ms for the 200k one/eight/sixteen-signal histories respectively.
These calls still precede the background viewport request. This is additional
evidence for already-open historical scheduling work, not a new backlog slice.

After the full test suite completed, the probe was repeated with an offscreen
window shown at 1280x720 (`--frames 200000 --signals 8 16 --shown`). Eight signals
took 14.4754 seconds, including 6.2489 seconds in history, with a 286.410 ms
maximum event pass. Sixteen took 23.4771 seconds, including 12.3577 seconds in
history, with a 670.130 ms maximum event pass. Both succeeded with exact frame
counts and zero pending batches. SQLite counts/sizes matched the table. A
separate source census overlapped the beginning of the eight-signal run; the
sixteen-signal run had no concurrent test suite or census. These repeats confirm
the bottleneck under realized offscreen widgets, but are still not native
Windows latency measurements or statistically sampled performance percentiles.

### Operator workload clarification

The operator supplied a local reference capture and explicitly accepts longer
loading for equally dense captures up to fifty minutes. A read-only streaming
census using the production `iter_trace` parser measured:

- 195,753,923 source bytes and 1,755,746 CAN frames.
- 944.788905 seconds (about 15 minutes 45 seconds), averaging 1,858.347 frames/s.
- 40 distinct frame identities; identifier values and payloads are not recorded.
- 991 bus-status events, 23 error-frame events and one parser anomaly.
- 10.105 seconds for the census, including aggregate calculations; this is not
  an application load time or an isolated parser microbenchmark.

At comparable mean density and line size, fifty minutes corresponds to about
5,575,042 frames and 621,579,875 source bytes. These are workload estimates,
not measurements of an existing fifty-minute file. Synthetic qualification must
cover that scale and density in addition to the smaller diagnostic fixtures.
Do not extrapolate the synthetic sixteen-signal disk multiplier directly onto
the private capture: its signal rates/DBC mix were not provided or decoded.
The private source path, name, payloads and DBC identities are excluded from
versioned documents. The census establishes that valid events are present in
the operator's actual workload, not only adversarial synthetic inputs.

## Findings requiring new corrective scope

### F1 — High: synchronous history construction dominates selected-signal loading

Evidence: `src/peaklive/ui/ingest_controller.py:280-323`,
`src/peaklive/analysis/history.py:114-279`, and the measurement table.
Every GUI ingestion batch appends raw samples, maintains seven summary levels,
updates run anchors and commits SQLite. The replay batch size is 256; 200k
frames trigger 782 append calls. Each selected sample traverses all seven
levels, repeatedly decodes JSON extrema and incurs per-bucket SELECT/update
operations. Moving parsing into a worker did not move this work off Qt.

At sixteen signals, the measured history append time alone is 12.565 seconds
out of 21.981 seconds of loading. Slow event passes exceed the existing 250 ms
product budget. This is a demonstrated scaling bottleneck, not proof that every
individual 256-frame transaction exceeds that budget. Disk contention can also
block synchronous SQLite calls; the measured runs used ordinary local storage.

Corrective direction: one explicit bounded background writer/ingestion owner,
batched transactions chosen through measurement, and lossless raw/summary/event
coverage. Preserve source order, selected-signal identity, live recording and
frame acknowledgements. Measure before choosing schema or journal changes;
disabling durability or dropping rare-event anchors is not an acceptable gain.

### F2 — High: replay events bypass backpressure and source order

Evidence: `src/peaklive/services/replay_worker.py:127-159` and
`src/peaklive/ui/ingest_controller.py:358-367`.
Valid bus events use a separate immediate `event_received` signal. They neither
flush the current frame batch nor acquire a pending-batch permit. The GUI
renders each event synchronously. Bounded anomaly aggregation does not cover
valid `ErrorFrame`, bus-status or TRC events.

Reproduction with source frame at 0.000, event at 0.001, frame at 0.002 delivers
`event(0.001), frame(0.000), frame(0.002)`. An event-only capture emits 10,000
events and succeeds without any acknowledgement, with `pending_batch_count=0`.
The direct signal sink proves producer behavior; an actual queued GUI sink can
accumulate these events. The probe does not claim to measure its peak queue RAM.

Corrective direction: an ordered bounded stream of frame/event records with
one ownership and acknowledgement contract; coalesce presentation only. Keep
authoritative event counts and ordering exact, including event-only files,
frame/event boundaries, cancellation, replacement and EOF finalization.

### F3 — High: history write failure escapes the GUI drain after partial ingestion

Evidence: `src/peaklive/ui/session_controller.py:201-212` and
`src/peaklive/ui/ingest_controller.py:295-323`.
The drain pops its batch, mutates trace/facts/series/frame cache, then writes
history, then acknowledges. No GUI-slot error boundary encloses that sequence.

A real SQLite failure induced on the session connection with
`PRAGMA query_only=ON` produces `attempt to write a readonly database` with
one trace row, one cached frame, zero acknowledgements, an empty pending queue
and no active drain timer. This deterministic reproduction exercises a database
exception, not actual disk exhaustion. Locked/full/unwritable storage can take
the same unchecked exception route, but their exact timing was not reproduced.

The UI can be partially updated while the producer waits or eventually reports
a generic backpressure failure. For a short source that already reached EOF,
completion also needs explicit auditing: current source success is set before
GUI acknowledgement. Do not treat that scenario as reproduced false success.

Corrective direction: explicit failed/partial session state and per-batch commit
semantics; release/retire owned permits exactly once on every terminal path,
cancel the producer, and retain an actionable storage error. Never retry already
counted frames blindly or acknowledge persistence success when it failed.

### F4 — Medium: the published performance gate misses the new dominant work

Evidence: `src/peaklive/analysis/profiling.py:23-65`,
`scripts/audit_trace_performance.py:43-74,104-117`, and
`tests/test_trace_performance.py:82-125,203-233`.
The stage list still contains only parse/dispatch/decode/trace/series/graph/report.
History writes sit outside every stage. The default fixture selects one signal;
the event-loop test loads no DBC. The script does not require successful replay
or the expected frame count after its deadline and always returns zero even when
printing budget overruns. It also ends before asynchronous historical plotting
is guaranteed ready. The old 4.1-second result in `docs/trace-performance-audit.md`
belongs to an older pipeline and cannot certify this version.

Windows-specific tolerances allow a 1.25-second event pass in the responsiveness
test, a 350 ms/1k trace stage instead of 150, and a 30-second retention-test stall
instead of the production two seconds. These are explicit harness choices, not
proof of a production improvement. Preserve the distinction in reported verdicts.

Corrective direction: measure parse, decode, history append/summary/commit,
queue wait, GUI projection, first useful display and final ready state separately.
Add ASC/TRC, event-heavy, one/eight/sixteen-signal and late-selection scenarios;
fail the benchmark when timed out, truncated, unsuccessful or over the chosen
gate. Keep machine-dependent timing evidence distinct from deterministic bounds.

## Existing debt and blockers: coordinate, do not duplicate

| Existing owner | Evidence and remaining obligation | Impact on this corpus |
| --- | --- | --- |
| Historical scheduler/reconstruction backlog item 123, active task 026 | `graph_stack.py:198-223` still does synchronous bounds/revision SQL and starts replacement workers without waiting for the old query to finish; `history_worker.py:28-42` checks cancellation between signals, not within SQL. | Share writer/revision/cancellation contracts with the new ingestion pipeline; retain the existing owner for navigation corrections. |
| Same owner, reconstruction lifecycle | `signal_decode_worker.py:180-253` commits partial rows into the shared history, checks source size/mtime only against worker-start identity, and drops by signal on cancellation; session reset clears and reuses the same store (`session_controller.py:288-295`). Generation guards protect callbacks but not all database writes. | Existing atomic coverage/session/source/DBC isolation criteria remain prerequisites. These are static gaps; concurrent stale deletion was not reproduced here. |
| Historical rare-event item 122, active task 026 | `history.py:300-320` returns no anchors when the reserved count overflows. The task explicitly records the missing clustered-activity marker. | Preserve its raw fidelity/coverage contract while optimizing summary construction. |
| Existing historical retention contract, requests 023/025 | Disk bounds were requested; current SQLite appends have no explicit quota/free-space policy. Measured history amplification is substantial. | Implement resource admission and disk-failure handling in the ingestion slice; final default capacity needs workload input. Disk growth is expected for lossless history, not a RAM leak. |
| Workspace task 027 | `tests/conftest.py:8-40` quarantines seven Windows offscreen test functions (eleven historically failing cases); Windows visual/DPI qualification remains open in the task. | Reuse that task for layout corrections. A green quarantined CI run does not settle native UI acceptance. |
| Workflow closeout evidence | Task 025 is Done with repeated multi-commit proof text although parts of its promised scheduler/memory/platform behavior are still owned by task 026. | Keep open follow-up obligations visible; do not automatically close or rewrite older tasks in this audit. |

Known general architecture debt (UI mixins, table item allocation and package
weight) is not promoted merely because it is visible. New evidence supports
the history/event/error-boundary priorities above. This audit performs no
dependency vulnerability lookup and makes no vulnerability-free claim.

## Development assumptions and open questions

The new corrective slices can start with synthetic fixtures. Missing private
files or a Windows machine do not block code preparation, but block claims of
target-machine loading performance and full packaged acceptance.

1. Typical size/density and maximum duration are now answered by the census and
   operator instruction: approximately 1.756M frames normally and 5.575M at fifty
   minutes. Selected-signal count remains open; default to 1/8/16 plus an
   unselected baseline. Keep 20k/200k routine fixtures and add resource-budgeted
   1.756M/5.575M qualification cases. The large synthetic cases were not run here.
2. What Windows reference hardware/storage and acceptable open-to-first-data and
   open-to-ready times should be reported? Retain 250 ms responsiveness as the
   existing target. The operator accepts longer total loading for longer traces;
   do not impose a fixed completion deadline as a product requirement. Benchmark
   watchdogs remain explicit harness safeguards, distinct from that requirement.
3. How much temporary disk may a session use? Propose a configurable cap and
   reserved free-space margin. Do not invent a fixed universal quota from the
   synthetic expansion factor.
4. On indexing failure, should an explicitly partial raw trace remain usable?
   Working contract: stop historical preparation, retain source files and clearly
   mark incomplete analysis; never label it complete. Product refinement may
   choose more recovery options without weakening truthfulness.
5. Should selecting several signals after loading share one source pass?
   Start with correct serialized jobs and revision-matched reuse as already
   scoped; measure redundant reads before committing to a broader decode cache.

Delivery order: establish complete measurements; secure ordered event delivery
and explicit failure handling; move/batch historical ingestion with bounded
ownership; integrate existing task 026 contracts; qualify representative Windows
workloads and report the remaining layout/rare-event obligations separately.

## Validation record

- Baseline Ruff: `uv run --python 3.13 ruff check .` passed.
- Baseline Logics lint passed; health reported zero issues and 21 open workflow
  docs. Baseline audit reported zero blockers, 27 warnings including 24 deferred
  closeout findings; visible warnings concern duplicate proof, a missing product
  diagram and prose-only lineage references.
- Full Linux/offscreen baseline: `QT_QPA_PLATFORM=offscreen uv run --python 3.13
  python -m pytest -ra` -> **626 passed in 197.18 seconds**. No runtime changes
  were made after this test run; documentation and the standalone audit probe
  are validated separately.
- Initial `rtk proxy` invocations rejected `--python`; raw `uv run --python 3.13`
  was used thereafter for exact command semantics. This was a wrapper invocation
  failure, not a test or application failure.
- Final corpus: both review and corrective requests pass `flow validate` with
  zero findings. Logics lint and Ruff pass. Global audit has zero blockers,
  three pre-existing visible warnings and 31 deferred closeout findings (seven
  newly expected for the unimplemented corrective request). No new visible
  audit warning remains. `git diff --check` passes.

## Development handoff

The review is captured in request 028. Corrective request 029 and product 027
feed backlog items 130 through 134 and orchestration task 028, all corrective
workflow work marked Ready with zero implementation progress. The context pack
is `logics/context-packs/peaklive_trace_loading_followup.json`; source scaffold
input is `logics/scaffold/peaklive_trace_loading_followup.json`.
Task 028's completion requires runtime proof, long-workload qualification and
resolution of its shared historical ownership prerequisites, not merely this
successful documentation validation.
