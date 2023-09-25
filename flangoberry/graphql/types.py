import strawberry
from datetime import datetime
from typing import Any, get_type_hints
from .helpers import to_py_date
from dataclasses import asdict


@strawberry.type
class BaseMetadataMixin:
    created: datetime
    modified: datetime

class BaseVertexMethodsMixin:
    def to_dbdoc(self) -> dict[str, Any]:
        """Returns a dict with core prop names prefixed with underscore as expected by db
        @TODO: Might need to handle datetime too in the future (see `from_dbdoc` sister 
        method below)"""
        def _keyf(k):
            if k in ['key', 'id', 'rev']:
                return f'_{k}'
            return k
        return {_keyf(k):v for k,v in asdict(self).items()}

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
class BaseVertexFieldsMixin(BaseVertexMethodsMixin, BaseMetadataMixin):
    id: str
    key: str
    rev: str
    # created: datetime
    # modified: datetime
    is_root: bool
    is_leaf: bool


@strawberry.type
class BaseEdgeFieldsMixin(BaseMetadataMixin):
    id: str
    key: str
    rev: str
    frm: str
    to: str
    # created: datetime
    # modified: datetime

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
