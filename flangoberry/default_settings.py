import logging


VERSION = "0.1.0"


#
# GraphQL
#
SHOW_GRAPHIQL = True

#
# CORS
#
CORS_RESOURCES = {
    #
    # Allow everything (discouraged)
    # r"/graphql/*": {"origins": "*"}
    #
    # Sveltekit local dev server
    # r"/graphql": {"origins": "http://localhost:5173"}
    #
}

#
# ArangoDb
#

#
# Whether to use TEST_DBCONF instead of DBCONF for database
# settings. Can be set to True in, for e.g., a pytest fixture
# to configure appfactory to use TEST_DBCONF.
#
USE_TEST_DBCONF = False

#
# List of db aliases and respective configuration details
# for the app.
#
DBCONF = {
    #
    # The 'default' client alias.
    #
    # You can set up other client aliases for use in the application
    # if you, for e.g. want to connect to a different
    # ArangoDB instance/cluster.
    #
    "default": {
        "client_conf": {
            "hosts": ("http://localhost:8529",),
        },
        "db_connect_conf": {
            "flangoberry": {
                "name": "flangoberry",
                "username": "flangodev",
                "password": "somepass",
                "verify": True,
            }
        },
    },
    #
    # Example of another alias
    #
    # 'some_other_cli_alias': {
    #     'client_conf': {
    #         'hosts': (
    #             'http://anotherhost:8529',
    #         ),
    #     },
    #     'db_connect_conf': [
    #         {
    #             'name': 'anotherdatabase',
    #             'username': 'dev',
    #             'password': 'somepass',
    #             'verify': True
    #         }
    #     ]
    # },
}


#
# Since the application can use multiple aliases, a corresponding
# list of aliases must configured for tests.
#
TEST_DBCONF = {
    "default": {
        "client_conf": {
            "hosts": ("http://localhost:8529",),
        },
        "db_connect_conf": {
            "flangoberry": {
                "name": "flangoberry_test",
                "username": "flangodev",
                "password": "somepass",
                "verify": True,
            }
        },
    },
}


#
# Logging
#

LOG_LEVELS = {
    "flangoberry": logging.DEBUG,
    "passlib": logging.WARN,
    "botocore": logging.WARN,
    "boto3": logging.WARN,
    "requests": logging.WARN,
    "urllib3": logging.WARN,
    "twilio.http_client": logging.WARN,
}


#
# Settings utils
#


def set_default_db_alias(name: str, username: str, password: str):
    """Util to quick-configure a different default database than 'flangoberry'.
    For simplicity, this assumes you are only using one database. For more complex
    setups, please review the structure of `flangoberry.default_settings.DBCONF` and
    `flangoberry.default_settings.TEST_DBCONF` and configure manually."""

    DBCONF["default"]["db_connect_conf"][name] = DBCONF["default"]["db_connect_conf"][
        "flangoberry"
    ]
    DBCONF["default"]["db_connect_conf"][name]["name"] = name
    DBCONF["default"]["db_connect_conf"][name]["username"] = username
    DBCONF["default"]["db_connect_conf"][name]["password"] = password
    # print(DBCONF["default"]["db_connect_conf"][name])

    TEST_DBCONF["default"]["db_connect_conf"][name] = TEST_DBCONF["default"][
        "db_connect_conf"
    ]["flangoberry"]
    TEST_DBCONF["default"]["db_connect_conf"][name]["name"] = f"{name}_test"
    TEST_DBCONF["default"]["db_connect_conf"][name]["username"] = username
    TEST_DBCONF["default"]["db_connect_conf"][name]["password"] = password
    # print(TEST_DBCONF["default"]["db_connect_conf"][name])
