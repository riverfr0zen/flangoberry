from flangoberry import default_settings


def test_set_default_db_alias():
    default_conf = default_settings.DBCONF["default"]["db_connect_conf"]
    test_conf = default_settings.TEST_DBCONF["default"]["db_connect_conf"]

    assert "flangoberry" in default_conf
    assert default_conf["flangoberry"]["name"] == "flangoberry"
    assert "flangoberry" in test_conf
    assert test_conf["flangoberry"]["name"] == "flangoberry_test"

    default_settings.set_default_db_alias("new_db")
    assert "flangoberry" not in default_conf
    assert "new_db" in default_conf
    assert default_conf["new_db"]["name"] == "new_db"
    assert "flangoberry" not in test_conf
    assert "new_db" in test_conf
    assert test_conf["new_db"]["name"] == "new_db_test"
