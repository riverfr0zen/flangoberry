from arango import ArangoClient


def test_testapp_fixture(testapp):
    assert "DBCONN" in testapp.config
    assert testapp.config["DBCONN"]["alias"] == "default"
    assert isinstance(testapp.config["DBCONN"]["client"], ArangoClient)
    # logger.debug(testapp.config['DBCONN'])
    # logger.debug(testapp.config)


def test_testapp_index_route(testappcli):
    res = testappcli.get("/")
    assert res.data == b"Sure, he's a regular Davinci-man I bet."
