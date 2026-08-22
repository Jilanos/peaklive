from peaklive.i18n import translate


def test_english_catalog_uses_semantic_keys():
    assert translate("acquisition.start") == "Start Acquisition"
    assert translate("workspace.trace") == "Trace"
