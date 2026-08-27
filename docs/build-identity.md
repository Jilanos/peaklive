# Build Identity

An operator testing PeakLive on the bench has to be able to say *which*
executable produced a result. This is how that question is answered.

## One authoritative source

`src/peaklive/_version.py` declares the version. Everything else derives from it:

| Consumer | How it resolves |
| --- | --- |
| Package metadata (`pip show peaklive`) | `pyproject.toml` `[tool.hatch.version]` reads the file |
| `peaklive.__version__` | re-exported from `_version.py` |
| Status-bar identifier and About dialog | `peaklive.version.build_identifier()` |
| `peaklive.spec` (PyInstaller) | imports the same `build_identifier()` |

Nothing else may declare a version. Changing the release version means editing
`_version.py` and nothing more.

## The build tag

The identifier is:

```
<version>              a plain build, e.g. 0.1.0
<version>+<tag>        a tagged rebuild, e.g. 0.1.0+b202608271530
```

The tag is **baked in at package time**, not read from the environment when the
application starts. `scripts/build-windows.ps1` writes `src/peaklive/_build.py`
immediately before PyInstaller runs; that generated file is untracked and is the
only place a tag ever lives. An environment variable on the test machine would
say nothing about which executable was actually built, which is the whole point
of the identifier.

### Convention

- Default: `b` followed by a UTC timestamp, `bYYYYMMDDHHMM`. Two rebuilds of the
  same version are therefore always distinguishable, in build order.
- To label a rebuild for a specific test, set `PEAKLIVE_BUILD_TAG` before
  building, e.g. `$env:PEAKLIVE_BUILD_TAG = "b202608271530-shutdown-fix"`.
- Keep tags to letters, digits, dots, and hyphens.

A build with no tag is a plain build of the declared version; a build *with* one
is a rebuild produced for operator testing, and the About dialog says so.

## Where the operator sees it

- **Status bar, right-hand side**: `v0.1.0+b202608271530`, muted and small. It
  is deliberately unobtrusive — it must not consume workspace needed for CAN
  analysis — with the full identifier in its tooltip.
- **Help → About PeakLive**: the identifier, whether the application is running
  from the packaged executable or from source, and whether it is a tagged test
  rebuild.

Both are local. Neither requires a network connection.

## Windows packaged-executable smoke check

Run after `scripts/build-windows.ps1`, on the machine that will be tested.

1. Read `dist/PeakLive.build.txt`. Note the `identifier` and `sha256`.
2. Confirm the executable's hash still matches after any copy or transfer:
   `Get-FileHash -Path .\PeakLive.exe -Algorithm SHA256`.
3. Start `PeakLive.exe`. Confirm the status bar shows `v<identifier>` and that
   it is legible at the display scaling in use (100%, 125%, 150%).
4. Open **Help → About PeakLive**. Confirm the identifier matches step 1, and
   that it reports *Running from the packaged Windows executable*.
5. Disconnect the machine from the network and repeat steps 3–4. The identifier
   must be unchanged.
6. Record the identifier, the SHA-256, and the machine in the test feedback, so
   a reported observation can be tied back to one executable.

If step 3 or 4 disagrees with `dist/PeakLive.build.txt`, the executable under
test is not the one that was just built — check for a stale copy on the bench
before investigating anything else.
