## item_052_create_and_package_the_peaklive_application_icon - Create and package the PeakLive application icon
> From version: 1.0.0
> Schema version: 1.0
> Status: Ready
> Understanding: 90%
> Confidence: 85%
> Progress: 0%
> Complexity: Medium
> Theme: Desktop application identity
> Reminder: Update status/understanding/confidence/progress and linked request/task references when you edit this doc.
> Indicators reviewed: 2026-09-03 12:02:14

# AI Context
- Summary: Delivers one owned visual identity asset through both the live Qt application and the frozen Windows executable.
- Keywords: create, package, peaklive, application, icon
- Use when: Creating the licensed icon asset, resolving application resources, assigning QIcon, or configuring PyInstaller icon embedding.
- Skip when: Changing measurement setup data or recording filename policy.

# Problem
- PeakLive starts without an application icon, leaving the taskbar and window chrome unidentified.
- The current PyInstaller specification does not embed an icon or declare an owned icon asset.

# Scope
- In:
  - Create an original, license-safe PeakLive icon source suitable for a CAN measurement workstation, plus the platform packaging format(s) required by the current Windows build.
  - Store the asset at a stable project-owned path and include it in source and frozen-resource discovery.
  - Assign the icon to QApplication before MainWindow construction and configure the existing PyInstaller specification to embed the matching Windows executable icon.
  - Test asset availability, Qt application/window icon assignment, and the packaging manifest/specification without requiring a Windows GUI during Linux CI.
- Out:
  - Using third-party logos, trademarked vendor marks, or unlicensed icon packs.
  - A system tray feature, notifications, installer redesign, or broad visual rebrand.
  - Claiming pixel-level OS taskbar behavior that cannot be deterministically asserted outside the target desktop environment.

# Acceptance criteria
- AC1: The repository contains an original, documented, license-safe icon asset and the formats the current packaged Windows workflow requires.
- AC2: QApplication receives a non-null PeakLive icon before MainWindow is created, and the MainWindow inherits or explicitly uses it.
- AC3: peaklive.spec embeds the matching icon and includes any runtime resource needed by the frozen build.
- AC4: Automated tests verify source asset resolution, application/window icon configuration, and spec references; a release build validates the Windows artifact when that platform is available.

# AC Traceability
- request-AC6 -> This backlog slice. Proof: AC1: The repository contains an original, documented, license-safe icon asset and the formats the current packaged Windows workflow requires.
- request-AC7 -> This backlog slice. Proof: AC2: QApplication receives a non-null PeakLive icon before MainWindow is created, and the MainWindow inherits or explicitly uses it.

# Decision framing
- Product framing: Not needed
- Architecture framing: Not needed

# Links
- Product brief(s): `prod_014_peaklive_reusable_measurement_setups_and_identifiable_recording_workspace`
- Architecture decision(s): (none yet)
- Request: `req_014_manage_reusable_peaklive_measurement_setups_recording_text_and_desktop_application_identity`
- Primary task(s): `task_015_deliver_reusable_measurement_setups_recording_text_and_application_icon_identity`

# Priority
- Priority: Medium - a visible app identity materially improves desktop usability but does not alter measurement correctness.
- Rationale: Set by scaffold input or defaulted for grooming.
