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


def test_helper_to_gql():
    # Test without passing a custom object_type, should still catch 'created' and 'modified' fields
    orig = {
        "_key": "somekey",
        "_rev": "somerev",
        "_id": "someid",
        "animal": "monkey",
        "created": datetime.now().isoformat(),
        "modified": datetime.now().isoformat(),
    }
    obj = helpers.to_gql(orig)
    assert "_key" not in obj
    assert obj["key"] == orig["_key"]
    assert "_rev" not in obj
    assert obj["rev"] == orig["_rev"]
    assert "_id" not in obj
    assert obj["id"] == orig["_id"]
    assert isinstance(obj["created"], datetime)
    assert isinstance(obj["modified"], datetime)

    # Test passing a custom object_type
    @strawberry.type
    class MyVertexType(types.BaseVertexFieldsMixin):
        animal: str
        some_custom_datetime: datetime

    orig = {
        "_key": "somekey",
        "_rev": "somerev",
        "_id": "someid",
        "animal": "monkey",
        "created": datetime.now().isoformat(),
        "modified": datetime.now().isoformat(),
        "some_custom_datetime": datetime.now().isoformat(),
    }
    obj = helpers.to_gql(orig, MyVertexType)
    assert "_key" not in obj
    assert obj["key"] == orig["_key"]
    assert "_rev" not in obj
    assert obj["rev"] == orig["_rev"]
    assert "_id" not in obj
    assert obj["id"] == orig["_id"]
    assert isinstance(obj["created"], datetime)
    assert isinstance(obj["modified"], datetime)
    assert isinstance(obj["some_custom_datetime"], datetime)
