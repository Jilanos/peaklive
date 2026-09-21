## item_147_add_a_language_menu_and_retranslate_the_workspace_without_resetting_sessions - Add a language menu and retranslate the workspace without resetting sessions
> From version: 1.0.0
> Schema version: 1.0
> Status: In progress
> Understanding: 90%
> Confidence: 85%
> Progress: 45%
> Complexity: High
> Theme: State-preserving runtime UI retranslation
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-21 13:59:59

# AI Context
- Summary: Deliver a language menu and in-place retranslation with session continuity.
- Keywords: add, language, menu, retranslate, workspace, resetting, sessions
- Use when: wiring locale changes into existing Qt widgets and menus.
- Skip when: changing worker ownership or rebuilding sessions.

# Problem
- Most controls capture translated strings during construction, so changing a global catalog would leave the visible application in mixed languages.
- Rebuilding the main window or using translated labels as identities risks losing session state or duplicating worker connections and actions.

# Scope
- In:
  - After the locale foundation, add Setup > Language / Configuration > Langue with French and English autonyms, exclusive check state, stable en/fr action data, keyboard access and localized accessibility metadata.
  - Implement explicit retranslate methods or a Qt language-change event adapter for the existing shell, menus, panels, widgets, overflow actions and dialogs; keep retranslation ownership separate from construction and session-reset paths.
  - Update combo display text in place using stable item data, preserve action enabled/checked states and shortcuts, block configuration-changing signals where necessary, and prevent duplicate menu registrations or signal connections.
  - Preserve filters, user inputs, trace selection and scroll, expanded tree nodes, shown/favorite signals, layout, cursors and graph viewport; hidden/collapsed views and new dialogs must use the current locale when shown.
  - Cover product-owned standard buttons and file/input/message dialogs through packaged Qt translations or app-controlled non-native dialogs when native OS chrome cannot follow the app locale; do not change OS settings.
  - Keep language selection available during background work and ensure callbacks reaching the UI after a switch use its new locale without restarting any acquisition/replay/export/DBC worker.
  - Test repeated switches with a fake live recorder and replay/export/catalog operations, asserting continuity and retained state rather than only checking changed captions.
- Out:
  - Replacing MainWindow, reconnecting the bus or rebuilding graphs as a language-switch shortcut.
  - Changing stable object names, stored enum keys, CAN content, profile names or DBC signal identities.
  - Rearchitecting unrelated active replay and graph performance work.

# Acceptance criteria
- AC1: The localized language submenu has exactly two exclusive choices labelled Français and English, and reflects persisted/current en or fr with unchanged shortcuts and usable keyboard navigation.
- AC2: en-to-fr-to-en updates existing menus, controls, headings, placeholders, tooltips and accessible names immediately, including overflow actions and hidden views on reopening; new dialogs and standard button text use the active language.
- AC3: Switching while live capture, recording, replay, export or DBC loading runs preserves worker identity, operation progress, session identity and capture data, with no new bus connection or duplicated handler.
- AC4: A populated workspace retains exact selected signals, favorites, filters, current trace selection, cursor positions, zoom, layout, scroll and user input after repeated switches.
- AC5: Menus, active/disabled states and profile settings stay coherent; changing translated combo captions does not issue a configuration mutation.
- AC6: Both language layouts pass the three supported size checks, including accented text and long labels, and all commands remain reachable.

# AC Traceability
- request-AC1 -> This backlog slice. Proof: AC1: The localized language submenu has exactly two exclusive choices labelled Français and English, and reflects persisted/current en or fr with unchanged shortcuts and usable keyboard navigation.
- request-AC2 -> This backlog slice. Proof: AC2: en-to-fr-to-en updates existing menus, controls, headings, placeholders, tooltips and accessible names immediately, including overflow actions and hidden views on reopening; new dialogs and standard button text use the active language.
- request-AC3 -> This backlog slice. Proof: AC3: Switching while live capture, recording, replay, export or DBC loading runs preserves worker identity, operation progress, session identity and capture data, with no new bus connection or duplicated handler.
- request-AC5 -> This backlog slice. Proof: AC4: A populated workspace retains exact selected signals, favorites, filters, current trace selection, cursor positions, zoom, layout, scroll and user input after repeated switches.
- request-AC6 -> This backlog slice. Proof: AC5: Menus, active/disabled states and profile settings stay coherent; changing translated combo captions does not issue a configuration mutation.
- request-AC9 -> This backlog slice. Proof: AC6: Both language layouts pass the three supported size checks, including accented text and long labels, and all commands remain reachable.
- request-AC10 -> This backlog slice. Proof: AC6: Both language layouts pass the three supported size checks, including accented text and long labels, and all commands remain reachable.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_032_peaklive_french_and_english_operator_experience`
- Architecture decision(s): (none yet)
- Request: `req_035_add_persistent_french_and_english_language_selection_across_peaklive`
- Primary task(s): `task_033_deliver_complete_persistent_french_and_english_language_switching_in_peaklive`

# Priority
- Priority: Medium - delivers the operator-visible choice after the locale foundation, with live-session safety as its acceptance gate.
- Rationale: Set by scaffold input or defaulted for grooming.
