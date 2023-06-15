import strawberry
from datetime import datetime
from typing import Optional, get_type_hints
from .helpers import to_py_date


@strawberry.type
class BaseVertexFieldsMixin:
    id: str
    key: str
    rev: str
    created: datetime
    modified: datetime

    @classmethod
    def from_dbdoc(cls, doc: dict) -> dict:
        """
        Prepares data from the database for population into the Strawberry object:
        * Converts the _key, _id, and _rev field names from the database to GQL-acceptable ones.
        * Converts any fields destined for datetime attrs to Python datetimes.
        """
        obj_type_hints = get_type_hints(cls)
        datetime_attrs = [k for k, v in obj_type_hints.items() if v is datetime]
        # logger.debug(datetime_attrs)
        converted_data = {}
        for k, v in doc.items():
            if k in ["_key", "_id", "_rev"]:
                k = k.replace("_", "")
            if k in datetime_attrs:
                v = to_py_date(v)
            converted_data[k] = v
        return cls(**converted_data)


@strawberry.type
class BaseEdgeFieldsMixin:
    id: str
    key: str
    rev: str
    frm: str
    to: str
    created: datetime
    modified: datetime

    @classmethod
    def from_dbdoc(cls, doc: dict) -> dict:
        """
        Prepares data from the database for population into the Strawberry object:
        * Converts the _key, _id, and _rev, _to, _from field names from the database to GQL-acceptable ones.
        * Converts any fields destined for datetime attrs to Python datetimes.
        """
        obj_type_hints = get_type_hints(cls)
        datetime_attrs = [k for k, v in obj_type_hints.items() if v is datetime]
        # logger.debug(datetime_attrs)
        converted_data = {}
        for k, v in doc.items():
            if k in ["_key", "_id", "_rev", "_to"]:
                k = k.replace("_", "")
            if k == "_from":
                k = "frm"
            if k in datetime_attrs:
                v = to_py_date(v)
            converted_data[k] = v
        return cls(**converted_data)
