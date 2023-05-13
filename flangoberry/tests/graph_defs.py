from .. import graph_ops
from typing import Optional
from flangoberry.graph_defs import NamedVertex, BaseEdge


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
