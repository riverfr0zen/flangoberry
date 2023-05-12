import json
import pytest
from flangoberry import settings, logger, db
from ..appfactory import create_app

# from ..appfactory import create_app


@pytest.fixture
def tests_conn():
    """This fixture would be used in tests that require the
    app to be set up, e.g. API tests, auth tests, etc. etc."""
    yield db.get_connection(dbsettings=settings.TEST_DBCONF)


def testapp_fixture(create_app_func):
    def _fixture():
        return create_app_func(
            test_config={
                "USE_TEST_DBCONF": True,
            }
        )

    return _fixture


@pytest.fixture
def testapp():
    """This fixture would be used in tests that require the
    app to be set up, e.g. API tests, auth tests, etc. etc.

    It yields an app configured with test db settings via appfactory
    """
    yield testapp_fixture(create_app)()


def gql_query_func(appcli):
    def gql(headers={}, query="", variables={}):
        """Do a graphql query/mutation via a flask app test client"""
        res = appcli.post(
            "/graphql",
            data=json.dumps(dict(query=query, variables=variables)),
            content_type="application/json",
            headers=headers,
        )
        return res

    return gql


def testappcli_fixture(create_app_func):
    def _fixture():
        appclient = create_app_func(
            test_config={
                "USE_TEST_DBCONF": True,
            }
        ).test_client()
        appclient.gql = gql_query_func(appclient)
        return appclient

    return _fixture


@pytest.fixture
def testappcli():
    """This fixture provides a flask test client for a testapp configured
    as above. A gql() method is also appended to simplify making GraphQL
    queries (see gql_query_func::gql above for method signature)"""
    yield testappcli_fixture(create_app)()


@pytest.fixture
def cleanup(tests_conn):
    """Clear graphs & collections in each database  after a test"""
    yield
    for alias, dbase in tests_conn["dbs"].items():
        for graphdef in dbase.graphs():
            dbase.delete_graph(graphdef["name"], drop_collections=True)
