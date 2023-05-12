from .. import graph_ops
from typing import Optional
from flangoberry.graph_defs import NamedVertex, BaseEdge


class Topic(NamedVertex):
    default_storage = NamedVertex.default_storage | {
        "collection": "topics",
    }


class Post(NamedVertex):
    default_storage = NamedVertex.default_storage | {
        "collection": "posts",
    }

    ptype: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["ptype"] = self.ptype


class Note(Post):
    ptype: Optional[str] = "Note"


class Bookmark(Note):
    default_storage = Note.default_storage | {
        "persistent_indexes": [{"fields": ["url"], "unique": True, "sparse": True}],
    }

    ptype: Optional[str] = "Bookmark"


class IsAbout(BaseEdge):
    default_storage = {
        "connection_alias": "default",
        "db_alias": "flangoberry",
        "graph": "default",
        "edge_definition": {
            "edge_collection": "is_about",
            "from_vertex_collections": [
                Post.default_storage["collection"],
                Topic.default_storage["collection"],
            ],
            "to_vertex_collections": [Topic.default_storage["collection"]],
        },
    }


class IsTypeOf(BaseEdge):
    default_storage = {
        "connection_alias": "default",
        "db_alias": "flangoberry",
        "graph": "default",
        "edge_definition": {
            "edge_collection": "is_type_of",
            "from_vertex_collections": [Topic.default_storage["collection"]],
            "to_vertex_collections": [Topic.default_storage["collection"]],
        },
    }


class ExampleNode(graph_ops.BaseVertex):
    default_storage = {
        "connection_alias": "default",
        "db_alias": "flangoberry",
        "graph": "default",
        "collection": "example_nodes",
        "persistent_indexes": [
            # Persistent index properties should match function signature here:
            # https://docs.python-arango.com/en/main/specs.html#arango.collection.Collection.add_persistent_index
            {"fields": ["attr2"], "unique": True, "sparse": True}
        ],
    }


class ExamplePerson(graph_ops.BaseVertex):
    default_storage = {
        "connection_alias": "default",
        "db_alias": "flangoberry",
        "graph": "default",
        "collection": "example_people",
    }


class ExampleEdge(graph_ops.BaseEdge):
    default_storage = {
        "connection_alias": "default",
        "db_alias": "flangoberry",
        "graph": "default",
        "edge_definition": {
            "edge_collection": "example_edges",
            "from_vertex_collections": ["example_nodes"],
            "to_vertex_collections": ["example_people"],
        },
    }
