"""The authoritative PeakLive version.

This file is the single source of truth. `pyproject.toml` reads it as the
package version, `peaklive.__version__` re-exports it, and
`peaklive.version.build_identifier()` builds the operator-facing identifier from
it. Nothing else may declare a version of its own.
"""

__version__ = "0.1.0"
