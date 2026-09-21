## item_146_establish_bilingual_catalogs_and_an_application_scoped_locale_preference - Establish bilingual catalogs and an application-scoped locale preference
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 10%
> Complexity: Medium
> Theme: Locale service, complete catalogs and durable application preferences
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-21 13:59:59

# AI Context
- Summary: Deliver locale lookup, catalog parity and application-scoped persistence.
- Keywords: establish, bilingual, catalogs, application, scoped, locale, preference
- Use when: implementing the locale foundation and startup behavior.
- Skip when: building UI retranslation before the service contract exists.

# Problem
- translate(key) reads only en.json and the application has no locale preference or notification contract.
- Storing language in measurement profiles would make changing a vehicle setup unexpectedly change the UI language.

# Scope
- In:
  - Add a locale-aware translation service retaining the semantic translate(key) entry point, with en/fr validation, locale-indexed caching, deterministic source fallback and an explicit language-change notification integrated on the GUI thread.
  - Add a complete fr.json based on an inventory of en.json and newly extracted product-owned prose; enforce leaf-key and placeholder parity, encoding and nonempty values. Record unavoidable technical literals in a bounded, justified allowlist.
  - Persist the selected locale in a dedicated ui-settings.json under the app data directory, honoring PEAKLIVE_DATA_DIR; use atomic writes, preserve unrelated future settings, recover invalid/unsupported values safely, and surface write failures without corrupting profiles.
  - Initialize the selected locale before window construction, use en for fresh installs and invalid preferences, and keep it stable across measurement profile selection or duplication.
  - Extend logics/i18n/contract.json during implementation to list en and fr, retaining en as source/default/fallback; include startup and failure tests and isolated locale reset between tests.
  - Allow runtime fallback for damaged deployments while requiring complete translated catalogs in validation; avoid logging a missing-key warning per received frame.
- Out:
  - Replacing the profile storage schema or moving measurement settings.
  - OS locale inference, locale-specific numerical formatting or a translation service dependency.
  - Claiming that changing the catalog alone retranslates already constructed widgets.

# Acceptance criteria
- AC1: en and fr translation lookup, cache isolation and two-way locale changes produce the intended text with tested English fallback for missing French content.
- AC2: French and English catalogs pass exact leaf-key, nonempty-value and formatting-placeholder/specification checks; absent keys in both catalogs fail validation and cannot crash an active window.
- AC3: Restart restores the application locale before the first rendered window; profile switches and duplication do not alter it or rewrite profile content.
- AC4: Missing, malformed, unknown-locale and unwritable preference cases have deterministic tested behavior, preserve measurement setups and provide a localized user warning where persistence fails.
- AC5: The updated i18n contract validates both catalogs, tests restore global locale state, and diagnostics for fallback are bounded.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: en and fr translation lookup, cache isolation and two-way locale changes produce the intended text with tested English fallback for missing French content.
- request-AC3 -> This backlog slice. Proof: AC2: French and English catalogs pass exact leaf-key, nonempty-value and formatting-placeholder/specification checks; absent keys in both catalogs fail validation and cannot crash an active window.
- request-AC4 -> This backlog slice. Proof: AC3: Restart restores the application locale before the first rendered window; profile switches and duplication do not alter it or rewrite profile content.
- request-AC6 -> This backlog slice. Proof: AC4: Missing, malformed, unknown-locale and unwritable preference cases have deterministic tested behavior, preserve measurement setups and provide a localized user warning where persistence fails.
- request-AC8 -> This backlog slice. Proof: AC5: The updated i18n contract validates both catalogs, tests restore global locale state, and diagnostics for fallback are bounded.
- request-AC10 -> This backlog slice. Proof: AC5: The updated i18n contract validates both catalogs, tests restore global locale state, and diagnostics for fallback are bounded.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_032_peaklive_french_and_english_operator_experience`
- Architecture decision(s): (none yet)
- Request: `req_035_add_persistent_french_and_english_language_selection_across_peaklive`
- Primary task(s): `task_033_deliver_complete_persistent_french_and_english_language_switching_in_peaklive`

# Priority
- Priority: Medium - required foundation for the bilingual workflow; schedule after higher-priority capture integrity work.
- Rationale: Set by scaffold input or defaulted for grooming.
