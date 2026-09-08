# Windows CI build under test

This document records the external packaged artifact qualified by the Windows
test battery. It keeps the Logics corpus repository-relative while the binary
itself is delivered alongside the repository checkout.

| Field | Value |
| --- | --- |
| Delivered file | `../PeakLive.exe` relative to this repository checkout |
| Build metadata | `../PeakLive.build.txt` relative to this repository checkout |
| Identifier | `0.1.2+b202609071506` |
| Build tag | `b202609071506` |
| SHA-256 | `E8E062387148A890AAB7FAE107D2A45F0F38269188CB36D789E7EF0FD28D4C21` |
| Built UTC | `2026-09-07T15:08:02.2669244Z` |

The qualification harness must read its executable and metadata paths as
explicit inputs, recompute the executable hash, and reject a mismatch before
launching the application. This record is evidence for the current run, not a
replacement for `PeakLive.build.txt`.
