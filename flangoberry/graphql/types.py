import strawberry
from datetime import datetime


@strawberry.type
class BaseVertexFieldsMixin:
    id: str
    key: str
    rev: str
    created: datetime
    modified: datetime
