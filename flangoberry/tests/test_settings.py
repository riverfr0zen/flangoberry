from flangoberry import default_settings


def test_set_default_db_alias():
    default_conf = default_settings.DBCONF["default"]["db_connect_conf"]
    test_conf = default_settings.TEST_DBCONF["default"]["db_connect_conf"]

    assert "flangoberry" in default_conf
    assert default_conf["flangoberry"]["name"] == "flangoberry"
    assert "flangoberry" in test_conf
    assert test_conf["flangoberry"]["name"] == "flangoberry_test"
    assert test_conf["flangoberry"]["username"] == "flangodev"
    assert test_conf["flangoberry"]["password"] == "somepass"

    default_settings.set_default_db_alias(
        name="new_db", username="newdev", password="newpass"
    )
    assert "flangoberry" not in default_conf
    assert "new_db" in default_conf
    assert default_conf["new_db"]["name"] == "new_db"
    assert default_conf["new_db"]["username"] == "newdev"
    assert default_conf["new_db"]["password"] == "newpass"
    assert "flangoberry" not in test_conf
    assert "new_db" in test_conf
    assert test_conf["new_db"]["name"] == "new_db_test"
    assert test_conf["new_db"]["username"] == "newdev"
    assert test_conf["new_db"]["password"] == "newpass"
