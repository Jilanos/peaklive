## req_035_add_persistent_french_and_english_language_selection_across_peaklive - Add persistent French and English language selection across PeakLive
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Complexity: High
> Theme: Complete French and English interface localization with safe runtime switching
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.
> Indicators reviewed: 2026-09-21 13:37:00

# AI Context
- Summary: Specify complete French/English selection, persistence and safe live retranslation.
- Keywords: add, persistent, french, english, language, selection, across, peaklive
- Use when: scoping or implementing PeakLive language selection.
- Skip when: changing CAN data, signal aliases or adding more locales.

# Needs
- Let an operator choose French or English and make every application-owned interface text use that language immediately, without restarting PeakLive.
- Keep the selected language between launches as an application preference independent of measurement profiles.
- Cover menus, panels, dialogs, table and graph labels, tooltips, accessibility names, prompts, validation, status and error messages, inspector prose and session reports, including already visible and subsequently created content.
- Preserve the ongoing acquisition, recording, replay, analysis state and all original measurement data when switching languages.

# Context
- The user's reference to a game is interpreted as this repository's PeakLive desktop application; no game or separate application is introduced.
- src/peaklive/i18n.py exposes translate(key), backed by one cached en.json file. It has no selected-locale state, locale-aware cache or language-change notification. Many widgets evaluate translations only during construction.
- The existing Logics i18n contract is valid, lists only en, and declares English as source, default and fallback. Extend this contract to en and fr during implementation; this planning corpus does not change the runtime contract.
- ReportRenderer in analysis/session.py hardcodes English prose; ProfileNameError messages are shown through str(error); internal decode status codes and other dynamic content require a presentation mapping rather than translating domain identities.
- The existing profile store owns measurement setups, revision-aware atomic saves and corruption recovery. Language must be application-scoped; a small separately owned ui-settings.json in the same application data directory is the planned persistence boundary, avoiding a profile-schema migration solely for language.
- Setup already groups application configuration. Add Setup > Language / Configuration > Langue with the stable autonyms Français and English, represented by locale codes fr and en. The selected entry is checked and keyboard accessible.
- Keep English as the initial default and fallback for compatibility. Do not automatically follow the OS language in this scope. Load the persisted choice before constructing the main window and app-owned dialogs.
- Active workspace and replay work touches actions.py, main_window.py and presentation controllers. Reconcile with their current APIs at implementation time; avoid replacing the application shell or duplicating their worker and lifecycle ownership.
- Medium priority: this is a complete operator-facing capability, sequenced after existing higher-priority acquisition and replay integrity work. Within this chain the locale foundation precedes runtime retranslation and completeness qualification.

# Acceptance criteria
- AC1: Setup > Language / Configuration > Langue provides exactly Français and English as mutually exclusive, keyboard-accessible choices; en is the initial default, fr and en are stable stored codes, and the current language is always marked.
- AC2: Choosing a language immediately updates all visible application-owned text and subsequently created views without restart, including open non-modal dialogs, collapsed or hidden panels when reopened, menus and overflow actions, static and dynamic content, tooltips, accessibility descriptions, table headers, graph axes, inspector prose, status messages and report text. Modal dialogs opened afterward inherit the current language; app-owned standard dialog buttons and file-dialog chrome also follow it.
- AC3: The app-scoped preference is loaded before first UI construction and survives restart, profile switching and Save setup as. Missing settings use en; unknown locale values or malformed settings recover safely to en without changing profiles. A failed save leaves the selected runtime language usable and displays a localized persistence warning without claiming it was saved.
- AC4: en.json and fr.json have identical leaf-key sets, nonempty string values and compatible formatting placeholders and specifications. All application-owned user-facing prose, including hardcoded report and profile validation strings, is inventoried and localized; release validation rejects accidental English leftovers in French through targeted expectations and a reviewed technical-literal allowlist.
- AC5: Repeated en-to-fr-to-en switching during live acquisition/recording, replay loading, DBC loading and signal export neither starts, stops nor replaces workers, loses or duplicates frames, resets progress, changes session identity or connects to the bus. Filters, shown signals, favorites, selected trace record, cursors, zoom, scroll position, panel state, input edits and enabled/checked action states are retained.
- AC6: CAN/DBC identifiers, message and signal names, DBC enumeration text, units, file paths, operator-entered names and labels, stored filter keys and all numeric values remain unchanged. Raw ASC/TRC and sidecar formats, CSV/Parquet schemas and machine-readable status codes remain stable. Translate their presentation labels only; numerical/date formatting stays as currently defined in this scope.
- AC7: Application-generated warnings and errors, currently displayed states and newly arriving worker outcomes render in the selected language; diagnostic details from a driver, OS or DBC remain verbatim inside a translated explanation. The on-screen and newly exported human-readable session report use the selected language with identical facts; already written files and technical logs are not rewritten.
- AC8: Missing French resources or keys fall back deterministically to the English source without crashing the live UI; fallback is observable in diagnostics, while complete catalog parity remains mandatory for a delivered build. A key absent from both catalogs is detected by validation and has a safe non-crashing runtime diagnostic presentation.
- AC9: Both languages remain readable and operable at 1024x768, 1280x720 and 1600x900, with correct accented characters, discoverable menu mnemonics, existing shortcuts and no inaccessible commands or overlapping controls. Windows packaging includes both catalogs and the selected Qt translations or controlled app-owned dialog equivalent.
- AC10: Focused automated tests cover catalog completeness, placeholders, startup/persistence/recovery, two-way runtime retranslation, deferred UI, dynamic errors, unchanged data/export contracts and session continuity. Headless regression tests, Ruff, i18n validation and Logics checks pass; a Windows smoke run covers French/English menus, dialogs and a live simulated or replay session without claiming physical CAN qualification. README and product scope describe bilingual behavior and its data boundaries.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_032_peaklive_french_and_english_operator_experience`
- Architecture decision(s): (none yet)

# References
- src/peaklive/i18n.py
- src/peaklive/i18n/en.json
- logics/i18n/contract.json
- src/peaklive/app.py
- src/peaklive/services/profiles.py
- src/peaklive/ui/main_window.py
- src/peaklive/ui/actions.py
- src/peaklive/ui/profile_controller.py
- src/peaklive/ui/workspace_center.py
- src/peaklive/ui/widgets.py
- src/peaklive/ui/panels/inspector.py
- src/peaklive/ui/panels/report.py
- src/peaklive/analysis/session.py
- src/peaklive/analysis/trace.py
- tests/test_i18n.py
- tests/test_ui_structure.py
- tests/test_ui_analyst.py
- tests/test_ui_menu_lifecycle.py
- tests/test_profiles.py
- tests/test_session_report.py
- docs/product-scope.md
- README.md

# Backlog
- `item_146_establish_bilingual_catalogs_and_an_application_scoped_locale_preference`
- `item_147_add_a_language_menu_and_retranslate_the_workspace_without_resetting_sessions`
- `item_148_localize_dynamic_analysis_text_validation_and_human_readable_reports`
- `item_149_qualify_bilingual_coverage_windows_packaging_and_operator_documentation`
