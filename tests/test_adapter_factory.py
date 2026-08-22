from peaklive.adapters import FakeCanAdapter, PcanAdapter, default_adapter


def test_factory_honours_explicit_offline_mode(monkeypatch):
    monkeypatch.setenv("PEAKLIVE_ADAPTER", "fake")
    assert isinstance(default_adapter(), FakeCanAdapter)


def test_factory_uses_pcan_on_windows(monkeypatch):
    monkeypatch.delenv("PEAKLIVE_ADAPTER", raising=False)
    monkeypatch.setattr("peaklive.adapters.factory.platform.system", lambda: "Windows")
    assert isinstance(default_adapter(), PcanAdapter)
