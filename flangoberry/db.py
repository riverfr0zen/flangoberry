from arango import ArangoClient

connections = {}


class DBException(Exception):
    pass


def get_connection(alias="default", dbsettings=None):
    try:
        return connections[alias]
    except KeyError:
        if not dbsettings:
            raise DBException(
                "Database settings must be provided "
                "to establish an initial connection."
            )
        conf = dbsettings[alias]
        connections[alias] = {
            "alias": alias,
            "client_conf": conf["client_conf"],
            "db_connect_conf": conf["db_connect_conf"],
        }
        connections[alias]["client"] = ArangoClient(**conf["client_conf"])
        connections[alias]["dbs"] = {}
        return connections[alias]


def get_db(db_alias, connection_alias="default"):
    conn = get_connection(connection_alias)
    try:
        return conn["dbs"][db_alias]
    except KeyError:
        db_conf = conn["db_connect_conf"][db_alias]
        # print(db_conf)
        conn["dbs"][db_alias] = conn["client"].db(**db_conf)
        return conn["dbs"][db_alias]
