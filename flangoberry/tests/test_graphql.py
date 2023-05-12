from flangoberry import logger


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
