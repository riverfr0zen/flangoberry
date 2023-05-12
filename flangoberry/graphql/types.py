import strawberry
from datetime import datetime
from typing import Annotated


@strawberry.type
class BaseVertexFieldsMixin:
    id: str
    key: str
    rev: str
    created: datetime
    modified: datetime


@strawberry.type
class PostFieldsMixin(BaseVertexFieldsMixin):
    ptype: str


@strawberry.type
class Note(PostFieldsMixin):
    name: str
    body: str


@strawberry.input
class NoteInput:
    name: str
    body: str


@strawberry.type
class CreateNoteResponse:
    existed: bool = strawberry.field(
        description="Whether the result had previously existed or was just created"
    )
    note: Note


@strawberry.type
class Bookmark(Note):
    url: str


@strawberry.input
class BookmarkInput(NoteInput):
    url: str


@strawberry.type
class CreateBookmarkResponse:
    existed: bool = strawberry.field(
        description="Whether the result had previously existed or was just created"
    )
    bookmark: Bookmark
