from datetime import datetime, timezone
from typing import Optional


class BaseVertex(dict):
    default_storage = {
        "connection_alias": "default",
        "db_alias": "flangoberry",
        "graph": "default",
        "collection": None,
        "persistent_indexes": [
            #
            # Persistent index properties should match function signature here:
            # https://docs.python-arango.com/en/main/specs.html#arango.collection.Collection.add_persistent_index
            #
            # {"fields": ["some_field_name"], "unique": True, "sparse": True},
        ],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        now = datetime.now(timezone.utc).isoformat()
        if "created" not in self:
            self["created"] = now
        if "modified" not in self:
            self["modified"] = now
        if "is_root" not in self:
            self['is_root'] = True
        if "is_leaf" not in self:
            self['is_leaf'] = True


class BaseEdge(dict):
    default_storage = {
        "connection_alias": "default",
        "db_alias": "flangoberry",
        "graph": "default",
        "edge_definition": {
            "edge_collection": None,
            "from_vertex_collections": [],
            "to_vertex_collections": [],
        },
    }

    def __init__(self, **kwargs):
        if "frm" in kwargs:
            kwargs["_from"] = kwargs.pop("frm")["_id"]
        if "to" in kwargs:
            kwargs["_to"] = kwargs.pop("to")["_id"]

        super().__init__(**kwargs)
        now = datetime.now(timezone.utc).isoformat()
        if "created" not in self:
            self["created"] = now
        if "modified" not in self:
            self["modified"] = now


class NamedVertex(BaseVertex):
    # Assign a new default_storage for this class that has a unique index
    # for the name field. "|" is the new merge operator for dicts in Python 3.9
    default_storage = BaseVertex.default_storage | {
        "persistent_indexes": [{"fields": ["name"], "unique": True}],
    }
