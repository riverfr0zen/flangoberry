from flask import Flask
from strawberry.flask.views import GraphQLView
from flangoberry import settings
from flangoberry.graphql.schema import schema
from flangoberry.db import get_connection


def create_app(settings=settings, schema=schema, test_config=None):
    #
    # App and config
    #

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile("settings.py")
    if test_config:
        app.config.from_mapping(test_config)

    #
    # Database
    #

    dbsettings = settings.DBCONF
    if app.config["USE_TEST_DBCONF"]:
        dbsettings = settings.TEST_DBCONF
    app.config["DBCONN"] = get_connection(dbsettings=dbsettings)

    #
    # Routes
    #

    @app.route("/")
    def info():
        """Basic info display"""
        return "Sure, he's a regular Davinci-man I bet."

    app.add_url_rule(
        "/graphql",
        view_func=GraphQLView.as_view(
            "graphql",
            schema=schema,
            graphiql=settings.SHOW_GRAPHIQL,
        ),
    )

    return app
