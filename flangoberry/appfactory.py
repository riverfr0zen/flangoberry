from flask import Flask
from strawberry.flask.views import GraphQLView
from flangoberry.tests.schema import schema
from flangoberry.db import get_connection

# from flangoberry import settings


def create_app(settings_file="default_settings.py", schema=schema, test_config=None):
    """Utility to create and preconfigure Flask app. If schema is not provided,
    `flangoberry.tests.schema` will be used."""

    #
    # App and config
    #

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile(settings_file)
    if test_config:
        app.config.from_mapping(test_config)

    #
    # Database
    #

    dbsettings = app.config["DBCONF"]
    if app.config["USE_TEST_DBCONF"]:
        dbsettings = app.config["TEST_DBCONF"]
    app.config["DBCONN"] = get_connection(dbsettings=dbsettings)

    #
    # Routes
    #

    @app.route("/flangoberry")
    def info():
        """Basic info display"""
        return "Drink flangoberry for flowery fluctuations"

    app.add_url_rule(
        "/graphql",
        view_func=GraphQLView.as_view(
            "graphql",
            schema=schema,
            graphiql=app.config["SHOW_GRAPHIQL"],
        ),
    )

    return app
