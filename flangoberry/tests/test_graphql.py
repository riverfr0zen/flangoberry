import strawberry
from datetime import datetime
from flangoberry import logger
from flangoberry.graphql import helpers, types


def test_eg_field_query(testappcli):
    query = """
        query egfield($testVar: String!) {
          egfield(testVar: $testVar)
        }
    """
    res = testappcli.gql(
        headers={"Test-Header": "someheader"},
        variables={"testVar": "somevar"},
        query=query,
    )
    # logger.debug(res)
    # logger.debug(res.json)
    assert res.json["data"]["egfield"] == "Example field, someheader, somevar"


@strawberry.type
class MyVertexType(types.BaseVertexFieldsMixin):
    animal: str
    some_custom_datetime: datetime


def test_vertex_from_dbdoc():
    doc = {
        "_key": "somekey",
        "_rev": "somerev",
        "_id": "someid",
        "animal": "monkey",
        "created": datetime.now().isoformat(),
        "modified": datetime.now().isoformat(),
        "some_custom_datetime": datetime.now().isoformat(),
    }

    obj = MyVertexType.from_dbdoc(doc)
    assert not hasattr(obj, "_key")
    assert obj.key == doc["_key"]
    assert not hasattr(obj, "_rev")
    assert obj.rev == doc["_rev"]
    assert not hasattr(obj, "_id")
    assert obj.id == doc["_id"]
    assert obj.animal == "monkey"
    assert isinstance(obj.created, datetime)
    assert isinstance(obj.modified, datetime)
    assert isinstance(obj.some_custom_datetime, datetime)


@strawberry.type
class MyEdgeType(types.BaseEdgeFieldsMixin):
    animal: str
    some_custom_datetime: datetime


def test_edge_from_dbdoc():
    doc = {
        "_key": "somekey",
        "_rev": "somerev",
        "_id": "someid",
        "_from": "somefrom",
        "_to": "someto",
        "animal": "eel",
        "created": datetime.now().isoformat(),
        "modified": datetime.now().isoformat(),
        "some_custom_datetime": datetime.now().isoformat(),
    }

    obj = MyEdgeType.from_dbdoc(doc)
    assert not hasattr(obj, "_key")
    assert obj.key == doc["_key"]
    assert not hasattr(obj, "_rev")
    assert obj.rev == doc["_rev"]
    assert not hasattr(obj, "_id")
    assert obj.id == doc["_id"]
    assert not hasattr(obj, "_from")
    assert obj.frm == doc["_from"]
    assert not hasattr(obj, "_to")
    assert obj.to == doc["_to"]
    assert obj.animal == "eel"
    assert isinstance(obj.created, datetime)
    assert isinstance(obj.modified, datetime)
    assert isinstance(obj.some_custom_datetime, datetime)
