## item_101_preserve_complete_can_frame_identity_and_make_decoding_total - Preserve complete CAN frame identity and make decoding total
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: High
> Theme: Canonical CAN record semantics and safe decoding
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.

# AI Context
- Summary: Carry CAN direction, declared DLC, remote/data kind, and standard/extended identifier identity through every layer while retaining undecodable raw frames safely.
- Keywords: can-frame, direction, declared-dlc, remote-frame, standard-id, extended-id, total-decode
- Use when: Changing normalized frames, adapters, replay parsing, DBC lookup, session aggregation, trace, filters, reports, exports, or capture round trips.
- Skip when: Adding CAN FD, transmission controls, transport protocols, or signal-name provenance without changing canonical frame identity.

# Problem
- The frame model derives DLC from payload and carries no direction, making a non-zero remote DLC and replayed Tx record impossible to preserve.
- Remote frames enter ordinary DBC payload decoding and can raise before facts or raw identity are retained.
- DBC caches, conflict resolution, filters, and identifier reports use only the numeric identifier and merge standard and extended spaces.

# Scope
- In:
  - Extend normalized frame identity with explicit direction and declared DLC while keeping backward-compatible construction defaults where safe.
  - Carry those fields through hardware normalization, text replay, trace, inspector, filters, reporting, capture writing, and relevant export surfaces.
  - Skip physical-signal decoding for remote frames and classify malformed or short data-frame decode failures explicitly without dropping the raw frame.
  - Use a standard-or-extended identifier key consistently in DBC lookup/cache/conflicts/resolutions and session identifier aggregation.
  - Prepare full frame-kind and equal-numeric-ID regression fixtures, deferring their execution until final verification.
- Out:
  - Adding flexible-data-rate support, transmission controls, transport protocols, or new physical-value mathematics.
  - Changing the meaning of valid existing classic data-frame decoding.
  - Running model, parser, adapter, DBC, or UI tests during this slice.

# Acceptance criteria
- AC1: Rx and Tx data and remote records round-trip direction, declared DLC, identifier format, channel, timestamp, and payload wherever applicable.
- AC2: A remote frame with a matching DBC definition remains visible and counted without entering payload decode or raising from the ingestion slot.
- AC3: A short or invalid payload receives an explicit decode status while its raw frame still reaches authoritative session state.
- AC4: Standard and extended frames sharing a numeric identifier resolve, aggregate, filter, and report independently.
- AC5: All new frame identity and decode tests run only after implementation across all dependent layers is complete.

# AC Traceability
- request-AC7 -> This backlog slice. Proof: AC1: Rx and Tx data and remote records round-trip direction, declared DLC, identifier format, channel, timestamp, and payload wherever applicable.
- request-AC8 -> This backlog slice. Proof: AC2: A remote frame with a matching DBC definition remains visible and counted without entering payload decode or raising from the ingestion slot.
- request-AC9 -> This backlog slice. Proof: AC3: A short or invalid payload receives an explicit decode status while its raw frame still reaches authoritative session state.
- request-AC13 -> This backlog slice. Proof: AC5: All new frame identity and decode tests run only after implementation across all dependent layers is complete.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_018_peaklive_trustworthy_measurement_identity_and_recoverable_local_evidence`
- Architecture decision(s): (none yet)
- Request: `req_019_eliminate_peaklive_second_pass_integrity_identity_and_recovery_gaps`
- Primary task(s): `task_019_implement_every_second_pass_peaklive_integrity_and_recovery_correction`

# Priority
- Priority: High - remote DLC, Tx direction, and standard-versus-extended identity are measurement facts that are currently lost or decoded incorrectly.
- Rationale: Set by scaffold input or defaulted for grooming.
