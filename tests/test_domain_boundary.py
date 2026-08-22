from pathlib import Path


def test_domain_does_not_depend_on_qt_or_vendor_api():
    domain = Path(__file__).parents[1] / "src" / "peaklive" / "domain"
    source = "\n".join(path.read_text(encoding="utf-8") for path in domain.glob("*.py"))

    assert "PySide6" not in source
    assert "PCAN" not in source
