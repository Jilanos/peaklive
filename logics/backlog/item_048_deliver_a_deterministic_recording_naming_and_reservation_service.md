## item_048_deliver_a_deterministic_recording_naming_and_reservation_service - Deliver a deterministic recording naming and reservation service
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: High
> Theme: Recording naming integrity
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-03 10:57:27

# AI Context
- Summary: Separates naming, occupancy search, and exclusive target reservation from Qt and the ASC/TRC writer.
- Keywords: deliver, deterministic, recording, naming, reservation, service
- Use when: Implementing or testing template resolution and acquisition-start target ownership.
- Skip when: Building the recording settings surface or changing the contents of capture formats.

# Problem
- Template expansion and collision fallback live inside AscRecorder. They cannot provide a single testable naming contract, preview result, visible first-free iteration, or durable reservation before session start.
- A simple iteration increment is unsafe when recordings were moved, a prior process crashed, or two acquisition starts contend for the same target.

# Scope
- In:
  - Create a Qt-independent RecordingNaming service/value types that validate and expand the bounded placeholder grammar, sanitize profile text consistently, and keep resolved paths within the configured directory.
  - Implement non-mutating preview and a first-free resolver beginning from the persisted iteration, including final, partial, and reservation artifacts in occupancy checks.
  - Implement exclusive, durable reservation before writer open; define ownership, release/finalization, crash recovery, and failed-start behaviour so no artifact can look like a clean completed capture.
  - Integrate the service between session start and the ASC/TRC recorder, preserving current raw-frame-before-presentation ordering, rotation, capture format suffixes, failure notes, and completed/incomplete evidence rules.
  - Advance and persist the next iteration only after reservation succeeds, with a deterministic reset-to-one search policy.
  - Add deterministic tests including competing resolver instances, existing final/partial/reserved targets, malformed placeholders, clock injection, and recorder/acquisition regression fixtures.
- Out:
  - A UI settings dialog or menu action.
  - Changing ASC/TRC syntax, adding formats, changing segment rotation policy, or deleting old captures automatically.
  - Cross-machine locks for shared network filesystems beyond the platform's atomic local create guarantees.

# Acceptance criteria
- AC1: A pure service resolves valid templates deterministically and rejects unsafe templates with actionable errors.
- AC2: First-free selection and atomic reservation make overwrite impossible for pre-existing and concurrently chosen local targets.
- AC3: The selected capture path, completed/incomplete state, rotation behaviour, and raw frame writer contract remain correct through session lifecycle tests.
- AC4: The profile's next iteration is persisted after reservation and reset searches safely from one.
- AC5: Deterministic service, concurrency, and lifecycle fixtures prove failure recovery and preserve the current writer contract.

# AC Traceability
- request-AC3 -> This backlog slice. Proof: AC1: A pure service resolves valid templates deterministically and rejects unsafe templates with actionable errors.
- request-AC5 -> This backlog slice. Proof: AC2: First-free selection and atomic reservation make overwrite impossible for pre-existing and concurrently chosen local targets.
- request-AC6 -> This backlog slice. Proof: AC3: The selected capture path, completed/incomplete state, rotation behaviour, and raw frame writer contract remain correct through session lifecycle tests.
- request-AC7 -> This backlog slice. Proof: AC4: The profile's next iteration is persisted after reservation and reset searches safely from one.
- request-AC8 -> This backlog slice. Proof: AC5: Deterministic service, concurrency, and lifecycle fixtures prove failure recovery and preserve the current writer contract.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_013_peaklive_configurable_and_collision_safe_acquisition_recording`
- Architecture decision(s): (none yet)
- Request: `req_013_add_canalyzer_style_recording_configuration_and_collision_safe_acquisition_naming_to_peaklive`
- Primary task(s): `task_014_implement_configurable_collision_safe_peaklive_recording_names`

# Priority
- Priority: High - a recording target selected only by an unchecked increment can overwrite irreplaceable acquisition evidence.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_014_implement_configurable_collision_safe_peaklive_recording_names`

# Notes
- Task `task_014_implement_configurable_collision_safe_peaklive_recording_names` was finished via `logics-manager flow finish task` on 2026-09-03.
