import pytest
from flangoberry.default_settings import TEST_DBCONF
from flangoberry import db
from arango import ArangoClient
from arango.database import StandardDatabase


def test_get_connection():
    alias = "default"
    testconf = TEST_DBCONF[alias]

    db.connections = {}
    with pytest.raises(db.DBException) as excinfo:
        conn = db.get_connection()
    assert "Database settings must be provided" in str(excinfo.value)

    db.connections = {}
    conn = db.get_connection(dbsettings=TEST_DBCONF)
    assert conn["alias"] == alias
    assert conn["client_conf"] == testconf["client_conf"]
    assert conn["db_connect_conf"] == testconf["db_connect_conf"]
    assert isinstance(conn["client"], ArangoClient)

    db.connections = {}
    conn = db.get_connection(alias="default", dbsettings=TEST_DBCONF)
    assert conn["alias"] == alias
    assert conn["client_conf"] == testconf["client_conf"]
    assert conn["db_connect_conf"] == testconf["db_connect_conf"]
    assert isinstance(conn["client"], ArangoClient)


def test_get_db():
    db.connections = {}
    with pytest.raises(db.DBException) as excinfo:
        db.get_db("flangoberry")
    assert "Database settings must be provided" in str(excinfo.value)

    db.get_connection(dbsettings=TEST_DBCONF)
    dbase = db.get_db("flangoberry")
    assert isinstance(dbase, StandardDatabase)
    alias = "default"
    db_conf = TEST_DBCONF[alias]["db_connect_conf"]["flangoberry"]
    assert dbase.name == db_conf["name"]
