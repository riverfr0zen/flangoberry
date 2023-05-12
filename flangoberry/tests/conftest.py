import json
import pytest
from flangoberry import settings, logger, db

# from ..appfactory import create_app


@pytest.fixture
def tests_conn():
    """This fixture would be used in tests that require the
    app to be set up, e.g. API tests, auth tests, etc. etc."""
    yield db.get_connection(dbsettings=settings.TEST_DBCONF)


@pytest.fixture
def cleanup(tests_conn):
    """Clear graphs & collections in each database  after a test"""
    yield
    for alias, dbase in tests_conn["dbs"].items():
        for graphdef in dbase.graphs():
            dbase.delete_graph(graphdef["name"], drop_collections=True)
