import pytest
from flangoberry import logger
from flangoberry.db import connections
from datetime import datetime
from .graph_defs import ExampleNode, ExamplePerson, ExampleEdge
from .. import graph_ops
from arango.database import StandardDatabase
from arango.collection import VertexCollection, EdgeCollection
from arango.graph import Graph


def test_resolve_vertex_storage(tests_conn, cleanup):
    eg_node = ExampleNode(attr1="val1", attr2="val2")
    storage = graph_ops.resolve_vertex_storage(eg_node)
    assert isinstance(storage, graph_ops.VertexStorage)
    assert isinstance(storage.db, StandardDatabase)
    assert storage.db.name == "flangoberry_test"
    assert isinstance(storage.graph, Graph)
    assert storage.graph.name == "default"
    assert isinstance(storage.collection, VertexCollection)
    assert storage.collection.name == "example_nodes"
    # Check that the unique (persistent) index for attr2 was created
    indexes = storage.collection.indexes()
    # logger.debug(f"INDEXES: {indexes}")
    assert len(indexes) == 2
    persistent_index = [i for i in indexes if i["type"] == "persistent"][0]
    assert persistent_index["type"] == "persistent"
    assert "attr2" in persistent_index["fields"]
    assert persistent_index["unique"] is True
    assert persistent_index["sparse"] is True

    # resolve a second time to test items that were already created
    # -- second time around, we pass in the vertex class instead of
    # an instance
    storage = graph_ops.resolve_vertex_storage(ExampleNode)
    assert isinstance(storage, graph_ops.VertexStorage)
    assert isinstance(storage.db, StandardDatabase)
    assert storage.db.name == "flangoberry_test"
    assert isinstance(storage.graph, Graph)
    assert storage.graph.name == "default"
    assert isinstance(storage.collection, VertexCollection)
    assert storage.collection.name == "example_nodes"
    # Check that unique index for attr2 was not created a second time
    indexes = storage.collection.indexes()
    assert len(indexes) == 2

    alt_storage = {
        "connection_alias": "default",
        "db_alias": "flangoberry",
        "graph": "another_graph",
        "collection": "example_noodles",
    }

    storage = graph_ops.resolve_vertex_storage(ExampleNode, storage_def=alt_storage)
    assert isinstance(storage, graph_ops.VertexStorage)
    assert isinstance(storage.db, StandardDatabase)
    assert storage.db.name == "flangoberry_test"
    assert isinstance(storage.graph, Graph)
    assert storage.graph.name == "another_graph"
    assert isinstance(storage.collection, VertexCollection)
    assert storage.collection.name == "example_noodles"

    # The following should fail since the db_alias has not been
    # defined in settings
    alt_storage = {
        "connection_alias": "default",
        "db_alias": "flangoberry_nonexistent",
        "graph": "another_graph",
        "collection": "example_noodles",
    }
    with pytest.raises(KeyError):
        eg_node = ExampleNode(attr1="val1", attr2="val2")
        storage = graph_ops.resolve_vertex_storage(eg_node, storage_def=alt_storage)


def test_create_vertex(tests_conn, cleanup):
    with pytest.raises(graph_ops.DataOpsException) as einfo:
        result = graph_ops.create_vertex({"some": "invalid", "dict": "fails"})
    assert "must be an instance of BaseVertex" in str(einfo)

    eg_node = ExampleNode(attr1="val1", attr2="val2")
    result = graph_ops.create_vertex(eg_node)

    storage = graph_ops.resolve_vertex_storage(ExampleNode)
    eg_node_from_db = storage.collection.get(result["_key"])
    assert eg_node_from_db["created"] == eg_node["created"]
    assert eg_node_from_db["modified"] == eg_node["modified"]
    assert eg_node_from_db["attr1"] == eg_node["attr1"]
    assert eg_node_from_db["attr2"] == eg_node["attr2"]

    eg_node = ExampleNode(_key="myspecialkey", attr1="myspecialval1")
    result = graph_ops.create_vertex(eg_node)
    assert result["_key"] == "myspecialkey"
    assert storage.collection.get(result["_key"])

    # Test DataOpsException if db returns DocumentInsertError
    with pytest.raises(graph_ops.DataOpsException) as einfo:
        result = graph_ops.create_vertex(eg_node)
    assert "unique constraint violated" in str(einfo)


def test_update_vertex(tests_conn, cleanup):
    with pytest.raises(graph_ops.DataOpsException) as einfo:
        result = graph_ops.update_vertex({"some": "invalid", "dict": "fails"})
    assert "must be an instance of BaseVertex" in str(einfo)

    eg_node = ExampleNode(attr1="attr1_rev1", attr2="attr2_rev1")
    insert_result = graph_ops.create_vertex(eg_node)
    # logger.debug(insert_result)

    eg_node = ExampleNode(_id=insert_result["_id"], attr1="attr1_rev2")
    update_result = graph_ops.update_vertex(eg_node)
    # logger.debug(update_result)
    assert update_result["_id"] == insert_result["_id"]
    assert update_result["_key"] == insert_result["_key"]
    assert datetime.fromisoformat(update_result["created"]) == datetime.fromisoformat(
        insert_result["created"]
    )
    assert datetime.fromisoformat(update_result["modified"]) > datetime.fromisoformat(
        insert_result["modified"]
    )

    storage = graph_ops.resolve_vertex_storage(ExampleNode)
    updated_node_from_db = storage.collection.get(insert_result["_key"])
    assert updated_node_from_db["attr1"] == "attr1_rev2"
    assert updated_node_from_db["attr2"] == "attr2_rev1"
    assert datetime.fromisoformat(
        updated_node_from_db["modified"]
    ) > datetime.fromisoformat(updated_node_from_db["created"])

    # Test DataOpsException if db returns DocumentUpdateError
    non_existent_node = ExampleNode(
        _id="example_nodes/non_existent_id", attr1="not real"
    )
    with pytest.raises(graph_ops.DataOpsException) as einfo:
        result = graph_ops.update_vertex(non_existent_node)
    assert "DocumentUpdateError" in str(einfo)


def test_get_vertex(tests_conn, cleanup):
    result = graph_ops.get_vertex(ExampleNode, {"attr1": "nonexistent"})
    assert result is None

    eg_node = graph_ops.create_vertex(ExampleNode(attr1="unique example", attr2="val2"))

    result = graph_ops.get_vertex(ExampleNode, {"attr1": "unique example"})
    assert result["_key"]
    assert result["attr1"] == eg_node["attr1"]

    eg_node2 = graph_ops.create_vertex(ExampleNode(attr1="dupe example", attr2="xxx"))
    eg_node2_copy = graph_ops.create_vertex(
        ExampleNode(attr1="dupe example", attr2="yyy")
    )

    with pytest.raises(graph_ops.DataOpsException, match="Expected one result but got"):
        result = graph_ops.get_vertex(ExampleNode, {"attr1": "dupe example"})


def test_get_or_create_vertex(tests_conn, cleanup):
    existed, result = graph_ops.get_or_create_vertex(
        ExampleNode, {"attr1": "soon_to_exist"}
    )
    assert existed is False
    assert result["_key"]
    assert result["attr1"] == "soon_to_exist"

    existed, result2 = graph_ops.get_or_create_vertex(
        ExampleNode, {"attr1": "soon_to_exist"}
    )
    assert existed is True
    assert result2["_key"] == result["_key"]

    existed, result3 = graph_ops.get_or_create_vertex(
        ExampleNode, {"attr1": "wont_exist"}, new_doc={"attr2": "soon_to_exist"}
    )
    assert existed is False
    assert result3["_key"] != result["_key"]
    assert result3["_key"] != result2["_key"]
    assert "attr1" not in result3
    assert result3["attr2"] == "soon_to_exist"

    storage = graph_ops.resolve_vertex_storage(ExampleNode)
    db_result = storage.collection.find({"attr1": "soon_to_exist"})
    assert db_result.count() == 1


def test_resolve_edge_storage(tests_conn, cleanup):
    eg_edge = ExampleEdge(attr1="val1", attr2="val2")
    storage = graph_ops.resolve_edge_storage(eg_edge)
    assert isinstance(storage, graph_ops.EdgeStorage)
    assert isinstance(storage.db, StandardDatabase)
    assert storage.db.name == "flangoberry_test"
    assert isinstance(storage.graph, Graph)
    assert storage.graph.name == "default"
    assert isinstance(storage.collection, EdgeCollection)
    assert storage.collection.name == "example_edges"

    # resolve a second time to test items that were already created
    storage = graph_ops.resolve_edge_storage(ExampleEdge)
    assert isinstance(storage, graph_ops.EdgeStorage)
    assert isinstance(storage.db, StandardDatabase)
    assert storage.db.name == "flangoberry_test"
    assert isinstance(storage.graph, Graph)
    assert storage.graph.name == "default"
    assert isinstance(storage.collection, EdgeCollection)
    assert storage.collection.name == "example_edges"

    alt_storage = {
        "connection_alias": "default",
        "db_alias": "flangoberry",
        "graph": "another_edge_graph",
        "edge_definition": {
            "edge_collection": "example_edgos",
            "from_vertex_collections": ["example_nodes"],
            "to_vertex_collections": ["example_people"],
        },
    }

    storage = graph_ops.resolve_edge_storage(ExampleEdge, storage_def=alt_storage)
    assert isinstance(storage, graph_ops.EdgeStorage)
    assert isinstance(storage.db, StandardDatabase)
    assert storage.db.name == "flangoberry_test"
    assert isinstance(storage.graph, Graph)
    assert storage.graph.name == "another_edge_graph"
    assert isinstance(storage.collection, EdgeCollection)
    assert storage.collection.name == "example_edgos"


def test_create_edge(tests_conn, cleanup):
    with pytest.raises(graph_ops.DataOpsException) as einfo:
        result = graph_ops.create_edge({"some": "invalid", "dict": "fails"})
    assert "must be an instance of BaseEdge" in str(einfo)

    eg_node = graph_ops.create_vertex(ExampleNode(attr1="val1", attr2="val2"))
    eg_person = graph_ops.create_vertex(ExamplePerson(attr1="p1", attr2="p2"))
    eg_edge = ExampleEdge(_from=eg_node["_id"], _to=eg_person["_id"], attr1="rel1")
    result = graph_ops.create_edge(eg_edge)
    storage = graph_ops.resolve_edge_storage(eg_edge)
    eg_edge_from_db = storage.collection.get(result["_key"])
    assert eg_edge_from_db["_from"] == eg_node["_id"]
    assert eg_edge_from_db["_to"] == eg_person["_id"]
    assert eg_edge_from_db["created"] == eg_edge["created"]
    assert eg_edge_from_db["modified"] == eg_edge["modified"]
    assert eg_edge_from_db["attr1"] == eg_edge["attr1"]

    # An easier way of creating an edge by passing node objects (instead of ids).
    # Also shows how to set a custom _key value.
    eg_edge = ExampleEdge(
        _key="myspecialedgekey", frm=eg_node, to=eg_person, attr1="rel1"
    )
    result = graph_ops.create_edge(eg_edge)
    assert result["_key"] == "myspecialedgekey"
    eg_edge_from_db = storage.collection.get(result["_key"])
    assert eg_edge_from_db["_from"] == eg_node["_id"]
    assert eg_edge_from_db["_to"] == eg_person["_id"]

    # Test DataOpsException if db returns DocumentInsertError
    with pytest.raises(graph_ops.DataOpsException) as einfo:
        result = graph_ops.create_edge(eg_edge)
    assert "unique constraint violated" in str(einfo)


def test_set_root_and_leaf_attrs(tests_conn, cleanup):
    eg_node = graph_ops.create_vertex(ExampleNode(attr1="val1", attr2="val2"))
    eg_node2 = graph_ops.create_vertex(ExampleNode(attr1="n2-val1", attr2="n2-val2"))
    eg_node3 = graph_ops.create_vertex(ExampleNode(attr1="n3-val1", attr2="n3-val2"))
    eg_person = graph_ops.create_vertex(ExamplePerson(attr1="p1", attr2="p2"))
    eg_edge_node_person = ExampleEdge(frm=eg_node, to=eg_person, attr1="rel1")
    graph_ops.create_edge(eg_edge_node_person)
    eg_edge_node_node2 = ExampleEdge(frm=eg_node, to=eg_node2, attr1="n-n2")
    graph_ops.create_edge(eg_edge_node_node2)
    eg_edge_node2_person = ExampleEdge(frm=eg_node2, to=eg_person, attr1="n2-person")
    graph_ops.create_edge(eg_edge_node2_person)
    eg_edge_node3_person = ExampleEdge(frm=eg_node3, to=eg_person, attr1="n3-person")
    graph_ops.create_edge(eg_edge_node3_person)

    # Fetch from db and check
    eg_node = graph_ops.get_vertex(ExampleNode, {"_id": eg_node["_id"]})
    assert eg_node["is_root"] == True
    eg_node2 = graph_ops.get_vertex(ExampleNode, {"_id": eg_node2["_id"]})
    assert eg_node2["is_root"] == False
    assert eg_node2["is_leaf"] == False
    eg_node3 = graph_ops.get_vertex(ExampleNode, {"_id": eg_node3["_id"]})
    assert eg_node3["is_root"] == True
    eg_person = graph_ops.get_vertex(ExamplePerson, {"_id": eg_person["_id"]})
    assert eg_person["is_root"] == False
    assert eg_person["is_leaf"] == True


def test_update_edge(tests_conn, cleanup):
    with pytest.raises(graph_ops.DataOpsException) as einfo:
        graph_ops.update_edge({"some": "invalid", "dict": "fails"})
    assert "must be an instance of BaseEdge" in str(einfo)

    eg_node = graph_ops.create_vertex(ExampleNode(attr1="val1", attr2="val2"))
    eg_person = graph_ops.create_vertex(ExamplePerson(attr1="p1", attr2="p2"))
    eg_edge = ExampleEdge(frm=eg_node, to=eg_person, attr1="attr1")
    insert_result = graph_ops.create_edge(eg_edge)

    eg_edge_update = ExampleEdge(_id=insert_result["_id"], attr1="updated attr1")
    update_result = graph_ops.update_edge(eg_edge_update)
    # logger.debug(update_result)
    assert update_result["_id"] == insert_result["_id"]
    assert update_result["_key"] == insert_result["_key"]
    assert datetime.fromisoformat(update_result["created"]) == datetime.fromisoformat(
        insert_result["created"]
    )
    assert datetime.fromisoformat(update_result["modified"]) > datetime.fromisoformat(
        insert_result["modified"]
    )

    storage = graph_ops.resolve_edge_storage(eg_edge)
    eg_edge_from_db = storage.collection.get(insert_result["_key"])
    assert eg_edge_from_db["_from"] == eg_node["_id"]
    assert eg_edge_from_db["_to"] == eg_person["_id"]
    assert eg_edge_from_db["created"] == eg_edge["created"]
    assert datetime.fromisoformat(eg_edge_from_db["modified"]) > datetime.fromisoformat(
        eg_edge_from_db["created"]
    )
    assert eg_edge_from_db["attr1"] == eg_edge_update["attr1"]

    # Test DataOpsException if db returns DocumentUpdateError
    non_existent_edge = ExampleEdge(
        _id="example_edges/non_existent_id", attr1="not real"
    )
    with pytest.raises(graph_ops.DataOpsException) as einfo:
        result = graph_ops.update_edge(non_existent_edge)
    assert "DocumentUpdateError" in str(einfo)


def test_get_edge(tests_conn, cleanup):
    with pytest.raises(graph_ops.DataOpsException, match="At least one"):
        graph_ops.get_edge(ExampleEdge)

    result = graph_ops.get_edge(ExampleEdge, {"someattr": "nonexistent"})
    assert result is None

    eg_node = graph_ops.create_vertex(ExampleNode(attr1="val1", attr2="val2"))
    eg_person = graph_ops.create_vertex(ExamplePerson(attr1="p1", attr2="p2"))
    eg_edge = graph_ops.create_edge(
        ExampleEdge(_from=eg_node["_id"], _to=eg_person["_id"], attr1="rel1")
    )
    result = graph_ops.get_edge(
        ExampleEdge, {"_from": eg_node["_id"], "_to": eg_person["_id"]}
    )
    assert result["_key"] == eg_edge["_key"]

    # Demonstrate "frm" and "to" params for passing BaseVertex instances (or dicts resembling them)
    # into search
    result = graph_ops.get_edge(ExampleEdge, frm=eg_node, to=eg_person)
    assert result["_key"] == eg_edge["_key"]

    eg_edge = graph_ops.create_edge(
        ExampleEdge(_from=eg_node["_id"], _to=eg_person["_id"], attr1="rel1")
    )

    with pytest.raises(graph_ops.DataOpsException, match="Expected one result but got"):
        result = graph_ops.get_edge(ExampleEdge, frm=eg_node, to=eg_person)


def test_get_or_create_edge(tests_conn, cleanup):
    eg_node = graph_ops.create_vertex(ExampleNode(attr1="val1", attr2="val2"))
    eg_person = graph_ops.create_vertex(ExamplePerson(attr1="p1", attr2="p2"))

    existed, eg_edge = graph_ops.get_or_create_edge(
        ExampleEdge, search={"_from": eg_node["_id"], "_to": eg_person["_id"]}
    )
    assert existed is False
    assert eg_edge["_key"]
    assert eg_edge["_from"] == eg_node["_id"]
    assert eg_edge["_to"] == eg_person["_id"]

    existed, eg_edge2 = graph_ops.get_or_create_edge(
        ExampleEdge, frm=eg_node, to=eg_person
    )
    assert existed is True
    assert eg_edge2["_key"] == eg_edge["_key"]
    assert eg_edge2["_from"] == eg_node["_id"]
    assert eg_edge2["_to"] == eg_person["_id"]

    # This will create a new edge because of the new property
    existed, eg_edge3 = graph_ops.get_or_create_edge(
        ExampleEdge, frm=eg_node, to=eg_person, search={"some_new_attr": "something"}
    )
    assert existed is False
    assert eg_edge3["_key"] != eg_edge["_key"]
    assert eg_edge3["_from"] == eg_node["_id"]
    assert eg_edge3["_to"] == eg_person["_id"]
    assert eg_edge3["some_new_attr"] == "something"

    # This will create a new edge because of no match, but the new edge will be based on
    # `new_doc` not `search`
    existed, eg_edge4 = graph_ops.get_or_create_edge(
        ExampleEdge,
        frm=eg_node,
        to=eg_person,
        search={"some_new_attr": "something different"},
        new_doc={"some_new_prop": "hi"},
    )
    assert existed is False
    assert eg_edge4["_key"] != eg_edge["_key"]
    assert eg_edge4["_key"] != eg_edge3["_key"]
    assert eg_edge4["_from"] == eg_node["_id"]
    assert eg_edge4["_to"] == eg_person["_id"]
    assert "some_new_attr" not in eg_edge4
    assert eg_edge4["some_new_prop"] == "hi"


def test_delete_vertex(tests_conn, cleanup):
    v1 = graph_ops.create_vertex(ExampleNode(attr1="v1a1", attr2="v1a2"))
    v2 = graph_ops.create_vertex(ExampleNode(attr1="v2a1", attr2="v2a2"))
    v3 = graph_ops.create_vertex(ExampleNode(attr1="v3a1", attr2="v3a2"))

    v1_v2 = graph_ops.create_edge(ExampleEdge(frm=v1, to=v2, attr1="v1v2"))
    v1_v3 = graph_ops.create_edge(ExampleEdge(frm=v1, to=v3, attr1="v1v3"))
    v2_v3 = graph_ops.create_edge(ExampleEdge(frm=v2, to=v3, attr1="v2v3"))

    delete_ok = graph_ops.delete_vertex(ExampleNode, v1["_id"])
    assert delete_ok

    # Edges connected to v1 should be deleted too
    v1 = graph_ops.get_vertex(ExampleNode, {"_id": v1["_id"]})
    assert not v1

    v1_v2 = graph_ops.get_edge(ExampleEdge, {"_id": v1_v2["_id"]})
    assert not v1_v2

    v1_v3 = graph_ops.get_edge(ExampleEdge, {"_id": v1_v3["_id"]})
    assert not v1_v3

    v2_v3 = graph_ops.get_edge(ExampleEdge, {"_id": v2_v3["_id"]})
    assert v2_v3


def test_list_vertex_edges(tests_conn, cleanup):
    v1 = graph_ops.create_vertex(ExampleNode(attr1="v1a1", attr2="v1a2"))
    v2 = graph_ops.create_vertex(ExampleNode(attr1="v2a1", attr2="v2a2"))
    v3 = graph_ops.create_vertex(ExampleNode(attr1="v3a1", attr2="v3a2"))
    v4 = graph_ops.create_vertex(ExampleNode(attr1="v4a1", attr2="v4a2"))

    v1_v2 = graph_ops.create_edge(ExampleEdge(frm=v1, to=v2, attr1="v1v2"))
    v1_v3 = graph_ops.create_edge(ExampleEdge(frm=v1, to=v3, attr1="v1v3"))
    v2_v3 = graph_ops.create_edge(ExampleEdge(frm=v2, to=v3, attr1="v2v3"))
    v3_v4 = graph_ops.create_edge(ExampleEdge(frm=v3, to=v4, attr1="v3v4"))

    cursor = graph_ops.list_vertex_edges(ExampleNode, v1["_id"], outbound_only=True)
    assert cursor.count() == 2
    for strand in cursor:
        assert strand["direction"] == "outbound"

    cursor = graph_ops.list_vertex_edges(ExampleNode, v3["_id"], inbound_only=True)
    assert cursor.count() == 2
    for strand in cursor:
        assert strand["direction"] == "inbound"

    cursor = graph_ops.list_vertex_edges(ExampleNode, v3["_id"])
    for strand in cursor:
        if strand["vertex"]["_id"] == v1["_id"]:
            assert strand["direction"] == "inbound"
        if strand["vertex"]["_id"] == v2["_id"]:
            assert strand["direction"] == "inbound"
        if strand["vertex"]["_id"] == v4["_id"]:
            assert strand["direction"] == "outbound"
    assert cursor.count() == 3


def test_delete_edge(tests_conn, cleanup):
    v1 = graph_ops.create_vertex(ExampleNode(attr1="v1a1", attr2="v1a2"))
    v2 = graph_ops.create_vertex(ExampleNode(attr1="v2a1", attr2="v2a2"))
    v3 = graph_ops.create_vertex(ExampleNode(attr1="v3a1", attr2="v3a2"))

    v1_v2 = graph_ops.create_edge(ExampleEdge(frm=v1, to=v2, attr1="v1v2"))
    v1_v3 = graph_ops.create_edge(ExampleEdge(frm=v1, to=v3, attr1="v1v3"))
    v2_v3 = graph_ops.create_edge(ExampleEdge(frm=v2, to=v3, attr1="v2v3"))

    v2 = graph_ops.get_vertex(ExampleNode, {"_id": v2["_id"]})
    assert not v2["is_leaf"]

    delete_ok = graph_ops.delete_edge(ExampleEdge, v2_v3["_id"])
    assert graph_ops.get_edge(ExampleEdge, {"_id": v1_v2["_id"]})
    assert graph_ops.get_edge(ExampleEdge, {"_id": v1_v3["_id"]})
    assert graph_ops.get_edge(ExampleEdge, {"_id": v2_v3["_id"]}) is None
    v2 = graph_ops.get_vertex(ExampleNode, {"_id": v2["_id"]})
    assert v2["is_leaf"]
