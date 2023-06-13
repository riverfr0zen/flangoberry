from datetime import datetime
from flangoberry import logger
from .types import BaseVertexFieldsMixin
from typing import Optional, get_type_hints


def to_py_date(iso_date) -> datetime:
    return datetime.fromisoformat(iso_date)


def to_gql(
    data: dict,
    object_type: Optional[type[BaseVertexFieldsMixin]] = BaseVertexFieldsMixin,
) -> dict:
    """Converts the _key, _id, and _rev field names from the database to GQL-acceptable ones"""
    # This comprehension *may* be more performant (untested) but is kind of hard to read
    # return {
    #     k.replace("_", "")
    #     if (k in ["_key", "_id", "_rev"])
    #     else k: to_py_date(v)
    #     if (k in ["created", "modified"])
    #     else v
    #     for k, v in data.items()
    # }

    obj_type_hints = get_type_hints(object_type)
    datetime_field_names = [k for k, v in obj_type_hints.items() if v is datetime]
    logger.debug(datetime_field_names)
    converted_data = {}
    for k, v in data.items():
        if k in ["_key", "_id", "_rev"]:
            k = k.replace("_", "")
        if k in datetime_field_names:
            v = to_py_date(v)
        converted_data[k] = v
    return converted_data
