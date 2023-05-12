import pytest
from flangoberry import logger
from flangoberry.graph_defs import Note, Topic, IsAbout, IsTypeOf
from .. import simple_assoc_builder as builder


def test_split_tokens_fail():
    with pytest.raises(ValueError, match="must be a node, not an edge"):
        entry = "-IsAbout-> Topic:ArangoDB -IsTypeOf-> Topic:Graph Databases"
        tokens = builder._split_tokens(entry)
        logger.debug(tokens)


def test_split_tokens():
    entry = "Note:MyNote -IsAbout-> Topic:ArangoDB -IsTypeOf-> Topic:Graph Databases"
    tokens = builder._split_tokens(entry)
    # logger.debug(tokens)
    assert len(tokens) == 5
    assert tokens[0] == "Note:MyNote"
    assert tokens[1] == "IsAbout"
    assert tokens[2] == "Topic:ArangoDB"
    assert tokens[3] == "IsTypeOf"
    assert tokens[4] == "Topic:Graph Databases"


def test_tokenize():
    entry = "Note:MyNote -IsAbout-> Topic:ArangoDB -IsTypeOf-> Topic:Graph Databases"
    tokens = builder.tokenize(entry)
    # logger.debug(tokens)
    assert len(tokens) == 5
    assert tokens[0] == ("Note", "MyNote")
    assert tokens[1] == "IsAbout"
    assert tokens[2] == ("Topic", "ArangoDB")
    assert tokens[3] == "IsTypeOf"
    assert tokens[4] == ("Topic", "Graph Databases")


def test_builder_get_node_def():
    mybuilder = builder.SimpleAssociationBuilder(
        node_defs=[Note, Topic], edge_defs=[IsAbout, IsTypeOf]
    )
    assert mybuilder.get_node_def("Topic") is Topic
    with pytest.raises(IndexError):
        mybuilder.get_node_def("SomeNonExistentClass")


def test_builder_get_edge_def():
    mybuilder = builder.SimpleAssociationBuilder(
        node_defs=[Note, Topic], edge_defs=[IsAbout, IsTypeOf]
    )
    assert mybuilder.get_edge_def("IsAbout") is IsAbout
    with pytest.raises(IndexError):
        mybuilder.get_edge_def("SomeNonExistentClass")


def test_builder_build_associations(tests_conn, cleanup):
    mybuilder = builder.SimpleAssociationBuilder(
        node_defs=[Note, Topic], edge_defs=[IsAbout, IsTypeOf]
    )

    entry = "Note:MyNote -IsAbout-> Topic:ArangoDB -IsTypeOf-> Topic:Graph Databases"
    mybuilder.build_associations(entry)
    pass
