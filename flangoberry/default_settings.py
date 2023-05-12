import logging


VERSION = "0.1.0"


#
# GraphQL
#
SHOW_GRAPHIQL = True


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
                "username": "dev",
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
                "username": "dev",
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
