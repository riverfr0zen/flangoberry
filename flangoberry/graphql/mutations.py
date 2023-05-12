import strawberry
from typing import List, Optional
from dataclasses import asdict
from . import types
from .. import graph_ops
from .. import graph_defs
from .. import simple_assoc_builder as builder


class FormattingException(Exception):
    pass


def _build_relationships(starting_node_str: str, relationships: List[Optional[str]]):
    mybuilder = builder.SimpleAssociationBuilder(
        node_defs=[graph_defs.Note, graph_defs.Bookmark, graph_defs.Topic],
        edge_defs=[graph_defs.IsAbout, graph_defs.IsTypeOf],
    )
    for rel in relationships:
        # Currently some very basic validation
        if rel.lstrip()[0] != "-":
            raise FormattingException(
                f"Each relationship should start with an Edge, but got: {rel}"
            )
        entry = f"{starting_node_str} {rel}"
        assocs_res = mybuilder.build_associations(entry)


@strawberry.mutation
def get_or_create_note(
    self, note: types.NoteInput, relationships: Optional[List[Optional[str]]] = None
) -> types.CreateNoteResponse:
    """If a Note with the same `name` exists, return that. Otherwise create a new Note
    with given properties."""
    relationships = relationships if relationships else []

    existed = False
    if existing_note := graph_ops.get_vertex(graph_defs.Note, {"name": note.name}):
        existed = True
        note = existing_note
    else:
        note = graph_defs.Note(**asdict(note))
        note = graph_ops.create_vertex(note)
    note = graph_ops.to_gql(note)

    _build_relationships(f"Note:{note['name']}", relationships)

    return types.CreateNoteResponse(existed=existed, note=types.Note(**note))


@strawberry.mutation
def get_or_create_bookmark(
    self,
    bookmark: types.BookmarkInput,
    relationships: Optional[List[Optional[str]]] = None,
) -> types.CreateBookmarkResponse:
    """If a Bookmark with the same `url` exists, return that. Otherwise create a new Bookmark
    with given properties."""
    relationships = relationships if relationships else []

    existed = False
    if existing_bookmark := graph_ops.get_vertex(
        graph_defs.Bookmark, {"url": bookmark.url}
    ):
        existed = True
        bookmark = existing_bookmark
    else:
        bookmark = graph_defs.Bookmark(**asdict(bookmark))
        bookmark = graph_ops.create_vertex(bookmark)
    bookmark = graph_ops.to_gql(bookmark)

    _build_relationships(f"Bookmark:{bookmark['name']}", relationships)

    return types.CreateBookmarkResponse(
        existed=existed, bookmark=types.Bookmark(**bookmark)
    )
