# Bilingual Windows smoke run

Evidence for the French/English interface on Windows (task_033). It records what
was actually observed and, just as deliberately, what this run does not cover.

## Build under test

| Field | Value |
| --- | --- |
| Identifier | `0.1.2+t033bilingual` |
| SHA-256 | `79046BEA1BCAF796F93D86A3F8305694B5FCD8C01760E00ACAA6CCD50027E342` |
| Built (UTC) | 2026-09-21T13:57:49Z |
| Host | Windows 10.0.26200 x64, PowerShell 5.1 |
| Command | `scripts\build-windows.ps1 -SkipValidation` with `PEAKLIVE_BUILD_TAG=t033bilingual` |

## Bundle contents

Read back from the packaged executable's own archive, not from the build tree:

```
peaklive\i18n\en.json
peaklive\i18n\fr.json
PySide6\Qt\translations\qtbase_fr.qm
PySide6\translations\qtbase_fr.qm
```

Both application catalogs ship, and so does Qt's French catalog, which is what
standard button captions and file-dialog chrome are drawn from.

## Packaged executable, observed

Each run used a fresh `PEAKLIVE_DATA_DIR` so nothing carried over.

| Check | Result |
| --- | --- |
| First run, no stored preference | Starts in English. `artifacts/bilingual-windows/packaged-first-run-english.png` |
| Restart with `{"locale": "fr"}` stored | Starts in French. `artifacts/bilingual-windows/packaged-restart-french.png` |
| Menu bar in French | Fichier, Enregistrement, Configuration, Affichage, DBC, Aide — mnemonics underlined |
| Accented text | Événements, Affichés seuls, tracé, échantillon all render correctly |
| Layout at 1086x759 | No clipping or overlap; every panel and command readable |
| Status bar | `Déconnecté`, build `v0.1.2+t033bilingual` |
| Synthetic lane naming | `Octet brut 0` in both the plot and the measurement row |

This run also found a real defect, since fixed: the stored preference was
written by PowerShell and therefore carried a UTF-8 byte-order mark, which made
the file parse as corrupt. The application recovered exactly as designed —
English, a logged warning, measurement profiles untouched — but a BOM is
ordinary on Windows, so the preference is now read with `utf-8-sig`.

## Native Windows behaviour

The behavioural suite was also run on Windows with the **native** Qt platform
rather than `offscreen`, so real windows, real dialogs and real geometry were
exercised:

```
uv run python -m pytest tests/test_ui_language.py tests/test_bilingual_packaging.py \
                        tests/test_i18n.py tests/test_ui_settings.py
70 passed
```

That covers the language menu, two-way switching, dialogs opened before and
after a switch, the three supported viewports, switching during a live simulated
acquisition with worker and session continuity, and byte-identical CSV export
across a switch.

The full suite on the same host:

```
$env:QT_QPA_PLATFORM="offscreen"; uv run python -m pytest
832 passed, 2 skipped, 7 xfailed, 5 xpassed, 1 failed
```

The single failure is `test_replay_backpressure.py::
test_replaying_onto_slow_persistence_never_blocks_the_event_loop` (event loop
stalled ~0.5 s against a 0.25 s budget). It reproduces identically at the
pre-task commit `570cfd0` on this host under full-suite load and passes in
isolation, so it is a pre-existing, load-sensitive failure unrelated to this
work.

## Not covered by this run

- **Selecting the language from inside the packaged executable.** The packaged
  build was driven through its stored preference, not through
  **Configuration > Langue**. Synthetic keyboard input could not be delivered to
  the application from the automation session used here, so `F5`, menu mnemonics
  and menu navigation in the packaged binary were not exercised. The same
  interactions are covered against native Windows widgets by the suite above.
- **Physical CAN hardware.** Every session here used the simulated adapter
  (`PEAKLIVE_ADAPTER=fake`). Nothing in this document is evidence of hardware
  qualification; see `docs/windows-hardware-acceptance.md` for that.
