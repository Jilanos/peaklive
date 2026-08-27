"""item_032 - the build identifier is visible, subtle, and consistent."""

from peaklive.adapters import FakeCanAdapter
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow
from peaklive.version import base_version, build_identifier


def _window(qtbot, tmp_path, show: bool = True):
    window = MainWindow(ProfileStore(tmp_path), adapter_factory=FakeCanAdapter)
    qtbot.addWidget(window)
    if show:
        window.show()
    return window


def test_the_identifier_is_visible_in_the_normal_application_chrome(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    assert window.build.isVisible()
    assert build_identifier() in window.build.text()
    assert window.build.accessibleName() == "Application build identifier"
    assert build_identifier() in window.build.toolTip()


def test_the_identifier_does_not_obstruct_the_workspace(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    # It lives in the status bar, not over the analysis surfaces.
    assert window.build.parent() is window.status
    assert window.build.objectName() == "buildIdentifier"
    # Small enough to stay out of the way, and it never grows with the window.
    assert window.build.height() <= 32
    assert window.build.width() < window.width() // 4


def test_the_identifier_stays_put_across_an_acquisition(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    before = window.build.text()

    window._start_acquisition()
    qtbot.waitUntil(lambda: window.trace_table.rowCount() > 0)
    window._stop_acquisition()
    qtbot.waitUntil(lambda: window.start_button.isEnabled())

    assert window.build.text() == before


def test_about_states_the_same_identifier_as_the_chrome(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    text = window.about_text()

    assert build_identifier() in text
    assert build_identifier() in window.build.text()
    # The product description survives alongside the build facts.
    assert "never transmits" in text


def test_about_says_whether_this_is_a_packaged_build(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    # The suite runs from source, never from the packaged executable.
    assert "Running from source." in window.about_text()


def test_about_calls_out_a_tagged_test_rebuild(qtbot, tmp_path, monkeypatch):
    import peaklive.ui.main_window as main_window
    from peaklive.version import BuildInfo

    monkeypatch.setattr(
        main_window,
        "build_info",
        lambda: BuildInfo(
            identifier=f"{base_version()}+b202608271530",
            base_version=base_version(),
            build_tag="b202608271530",
            packaged=True,
        ),
    )
    window = _window(qtbot, tmp_path)
    text = window.about_text()

    assert f"{base_version()}+b202608271530" in text
    assert "tagged test rebuild" in text
    assert "packaged Windows executable" in text
    assert f"v{base_version()}+b202608271530" == window.build.text()
