"""item_032 - one authoritative build identity, consistent everywhere."""

import re
import sys
from importlib.metadata import version as metadata_version
from pathlib import Path

import peaklive
from peaklive import version as version_module
from peaklive.version import BuildInfo, base_version, build_identifier, build_info


def test_package_metadata_and_runtime_value_agree():
    assert metadata_version("peaklive") == peaklive.__version__
    assert peaklive.__version__ == base_version()


def test_the_version_is_declared_in_exactly_one_place():
    root = Path(__file__).parents[1]
    declared = (root / "src" / "peaklive" / "_version.py").read_text(encoding="utf-8")

    assert f'__version__ = "{base_version()}"' in declared
    # pyproject must derive the version rather than restate it.
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'dynamic = ["version"]' in pyproject
    assert 'path = "src/peaklive/_version.py"' in pyproject
    assert f'version = "{base_version()}"' not in pyproject


def test_an_untagged_build_identifies_as_the_bare_version(monkeypatch):
    monkeypatch.setattr(version_module, "build_tag", lambda: "")

    assert version_module.build_identifier() == base_version()


def test_a_tagged_rebuild_is_distinguishable_from_the_plain_build(monkeypatch):
    monkeypatch.setattr(version_module, "build_tag", lambda: "b202608271530")

    identifier = version_module.build_identifier()

    assert identifier == f"{base_version()}+b202608271530"
    assert identifier != base_version()


def test_two_rebuilds_of_one_version_are_distinguishable(monkeypatch):
    monkeypatch.setattr(version_module, "build_tag", lambda: "b202608271530")
    first = version_module.build_identifier()
    monkeypatch.setattr(version_module, "build_tag", lambda: "b202608271815")
    second = version_module.build_identifier()

    assert first != second


def test_the_build_tag_comes_from_a_baked_module_not_the_environment(monkeypatch):
    monkeypatch.setenv("PEAKLIVE_BUILD_TAG", "b_from_the_environment")

    # An environment variable on the test machine says nothing about which
    # executable was built, so it must not reach the identifier.
    assert "environment" not in build_identifier()


def test_build_info_describes_the_running_build():
    info = build_info()

    assert isinstance(info, BuildInfo)
    assert info.identifier == build_identifier()
    assert info.base_version == base_version()
    assert info.packaged is bool(getattr(sys, "frozen", False))
    assert info.is_test_rebuild == bool(info.build_tag)


def test_the_identifier_matches_the_documented_convention():
    assert re.fullmatch(r"\d+\.\d+\.\d+(\+[A-Za-z0-9.\-]+)?", build_identifier())


def test_the_packaging_spec_reads_the_same_authoritative_source():
    spec = (Path(__file__).parents[1] / "peaklive.spec").read_text(encoding="utf-8")

    assert "from peaklive.version import build_identifier" in spec
    # The lazily imported build module must be named, or it is dropped silently.
    assert "peaklive._build" in spec


def test_the_build_script_bakes_the_tag_and_records_the_executable():
    script = (
        Path(__file__).parents[1] / "scripts" / "build-windows.ps1"
    ).read_text(encoding="utf-8")

    assert "src/peaklive/_build.py" in script
    assert "PEAKLIVE_BUILD_TAG" in script
    # Evidence tying a reported observation back to one executable.
    assert "PeakLive.build.txt" in script
    assert "SHA256" in script


def test_ci_publishes_the_build_evidence_beside_the_executable():
    """The identifier and hash must travel with the artifact, not stay on the runner."""
    workflow = (
        Path(__file__).parents[1] / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")

    assert "dist/PeakLive.exe" in workflow
    assert "dist/PeakLive.build.txt" in workflow
