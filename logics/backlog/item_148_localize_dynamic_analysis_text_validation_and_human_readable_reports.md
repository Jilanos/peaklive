## item_148_localize_dynamic_analysis_text_validation_and_human_readable_reports - Localize dynamic analysis text, validation and human-readable reports
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 90%
> Confidence: 85%
> Progress: 100%
> Complexity: High
> Theme: Dynamic presentation completeness and stable domain data
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-21 16:04:44

# AI Context
- Summary: Translate dynamic status, errors and reports while preserving domain identities.
- Keywords: localize, dynamic, analysis, text, validation, human, readable, reports
- Use when: localizing runtime messages and analysis presentation.
- Skip when: altering raw recordings, data schemas or user-authored content.

# Problem
- Hardcoded report prose, service validation messages and raw status codes can remain English even after widgets adopt a French catalog.
- Mutating domain codes or already-recorded messages to translate their display would compromise filtering, diagnostics and interchange compatibility.

# Scope
- In:
  - Inventory runtime prose in the UI, analysis renderers and service error paths; map app-owned states and validations to semantic keys with parameters instead of string-matching already formatted English messages.
  - Translate display representations of decode states, bus/lifecycle states, progress, empty/loading/error states, filter chips, cursor/statistics headings and inspector descriptions, retaining stable underlying codes and numerical values.
  - Retain semantic state for currently visible app-generated messages, inspector content and reports so they can be re-rendered on language change; preserve selected records and dialog input edits.
  - Adapt ReportRenderer to produce a localized human-readable report without introducing Qt dependencies into the analysis layer; newly exported text matches the current report locale and unchanged facts.
  - Render worker outcomes in the active UI language when delivered, and preserve raw OS/driver/file details inside localized surrounding messages; keep technical logs and previously saved artifacts unchanged.
  - Prove raw ASC/TRC and JSON sidecar contracts plus CSV/Parquet names, schema, units and values remain stable; localize only the export dialog and human-readable report prose.
- Out:
  - Translating DBC enumeration strings, user-authored setup or recording labels, source filenames or raw exception details supplied by third parties.
  - Changing report calculations, timestamps, decimal conventions or measurement units.
  - Retroactively rewriting stored captures, reports or developer logs.

# Acceptance criteria
- AC1: French and English render all inventoried app-owned runtime messages and analysis prose, including ProfileNameError validation and report headings; a populated inspector/report updates without reselection or a manual refresh.
- AC2: A worker started under en and completed under fr reports its app-owned status in French; existing displayed warnings also update while raw diagnostic details remain verbatim.
- AC3: Human-readable reports in both languages represent identical session facts and newly exported reports use the selected language.
- AC4: Stable identity codes, filters, DBC names, enum text, numerical values and machine-readable capture/export contracts are unchanged by switching language.
- AC5: Coverage tests exercise dynamic key paths, formatted values, error recovery and missing-translation fallback rather than relying solely on scanning literal translate calls.

# AC Traceability
- request-AC2 -> This backlog slice. Proof: AC1: French and English render all inventoried app-owned runtime messages and analysis prose, including ProfileNameError validation and report headings; a populated inspector/report updates without reselection or a manual refresh.
- request-AC4 -> This backlog slice. Proof: AC2: A worker started under en and completed under fr reports its app-owned status in French; existing displayed warnings also update while raw diagnostic details remain verbatim.
- request-AC5 -> This backlog slice. Proof: AC3: Human-readable reports in both languages represent identical session facts and newly exported reports use the selected language.
- request-AC6 -> This backlog slice. Proof: AC4: Stable identity codes, filters, DBC names, enum text, numerical values and machine-readable capture/export contracts are unchanged by switching language.
- request-AC7 -> This backlog slice. Proof: AC5: Coverage tests exercise dynamic key paths, formatted values, error recovery and missing-translation fallback rather than relying solely on scanning literal translate calls.
- request-AC8 -> This backlog slice. Proof: AC5: Coverage tests exercise dynamic key paths, formatted values, error recovery and missing-translation fallback rather than relying solely on scanning literal translate calls.
- request-AC10 -> This backlog slice. Proof: AC5: Coverage tests exercise dynamic key paths, formatted values, error recovery and missing-translation fallback rather than relying solely on scanning literal translate calls.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_032_peaklive_french_and_english_operator_experience`
- Architecture decision(s): (none yet)
- Request: `req_035_add_persistent_french_and_english_language_selection_across_peaklive`
- Primary task(s): `task_033_deliver_complete_persistent_french_and_english_language_switching_in_peaklive`

# Priority
- Priority: Medium - completes whole-interface coverage beyond static labels and protects language-independent data contracts.
- Rationale: Set by scaffold input or defaulted for grooming.

# Tasks
- `task_033_deliver_complete_persistent_french_and_english_language_switching_in_peaklive`

# Notes
- Task `task_033_deliver_complete_persistent_french_and_english_language_switching_in_peaklive` was finished via `logics-manager flow finish task` on 2026-09-21.
