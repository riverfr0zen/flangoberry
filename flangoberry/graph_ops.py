from collections import namedtuple
from flangoberry import logger
from flangoberry import db
from .graph_defs import BaseVertex, BaseEdge


class DataOpsException(Exception):
    pass


VertexStorage = namedtuple("VertexStorage", "db graph collection")

EdgeStorage = namedtuple("EdgeStorage", "db graph collection")


def resolve_vertex_storage(vertex: BaseVertex | type[BaseVertex], storage_def=None):
    if storage_def is None:
        storage_def = vertex.default_storage
    # logger.debug(storage_def)

    dbase = db.get_db(storage_def["db_alias"], storage_def["connection_alias"])
    graph = None
    if dbase.has_graph(storage_def["graph"]):
        graph = dbase.graph(storage_def["graph"])
    else:
        graph = dbase.create_graph(storage_def["graph"])

    coll = None
    if graph.has_vertex_collection(storage_def["collection"]):
        coll = graph.vertex_collection(storage_def["collection"])
    else:
        coll = graph.create_vertex_collection(storage_def["collection"])

    if persistent_indexes := storage_def.get("persistent_indexes", None):
        for p_index in persistent_indexes:
            p_index["in_background"] = True
            coll.add_persistent_index(**p_index)

    return VertexStorage(dbase, graph, coll)


def resolve_edge_storage(edge: BaseEdge | type[BaseEdge], storage_def=None):
    if storage_def is None:
        storage_def = edge.default_storage
    # logger.debug(storage_def)

    dbase = db.get_db(storage_def["db_alias"], storage_def["connection_alias"])
    graph = None
    if dbase.has_graph(storage_def["graph"]):
        graph = dbase.graph(storage_def["graph"])
    else:
        graph = dbase.create_graph(storage_def["graph"])

    coll = None
    edge_def = storage_def["edge_definition"]
    if graph.has_edge_definition(edge_def["edge_collection"]):
        coll = graph.edge_collection(edge_def["edge_collection"])
    else:
        coll = graph.create_edge_definition(**edge_def)

    if persistent_indexes := storage_def.get("persistent_indexes", None):
        for p_index in persistent_indexes:
            p_index["in_background"] = True
            coll.add_persistent_index(**p_index)

    return EdgeStorage(dbase, graph, coll)


def create_vertex(vertex: BaseVertex, storage_def=None) -> dict:
    if not isinstance(vertex, BaseVertex):
        raise DataOpsException("`vertex` must be an instance of BaseVertex")

    storage = resolve_vertex_storage(vertex, storage_def)
    return storage.collection.insert(vertex, return_new=True)["new"]


def get_vertex(
    vertex_def: type[BaseVertex], search: dict, storage_def=None
) -> dict | None:
    storage = resolve_vertex_storage(vertex_def, storage_def)
    res = storage.collection.find(search)
    if res.count() == 0:
        return None
    if res.count() > 1:
        raise DataOpsException("Expected one result but got more")
    return res.next()


def get_or_create_vertex(
    vertex_def: type[BaseVertex], search: dict, storage_def: dict = None
) -> tuple[bool, dict]:
    """
    Example: `already_existed, vertex = get_or_create_vertex(SomeVertexType, {'name': 'Some name'})`

    Tries to find a vertex of type `vertex_def` that has the properties in `search`,
    otherwise creates a new vertex with said properties.
    """
    if vertex := get_vertex(vertex_def, search, storage_def):
        return True, vertex
    return False, create_vertex(vertex_def(**search))


def create_edge(edge: BaseEdge, storage_def=None) -> dict:
    if not isinstance(edge, BaseEdge):
        raise DataOpsException("`edge` must be an instance of BaseEdge")

    storage = resolve_edge_storage(edge, storage_def)
    return storage.collection.insert(edge, return_new=True)["new"]


def _handle_get_edge_search_args(
    search: dict = None,
    frm: BaseVertex = None,
    to: BaseVertex = None,
) -> dict:
    if search is None:
        search = {}
    if frm:
        search["_from"] = frm["_id"]
    if to:
        search["_to"] = to["_id"]
    if not search:
        raise DataOpsException(
            "At least one of `search`, `frm`, or `to` must be provided"
        )
    return search


def get_edge(
    edge_def: type[BaseEdge],
    search: dict = None,
    frm: BaseVertex = None,
    to: BaseVertex = None,
    storage_def=None,
) -> dict | None:
    search = _handle_get_edge_search_args(search, frm, to)
    storage = resolve_edge_storage(edge_def, storage_def)
    res = storage.collection.find(search)
    if res.count() == 0:
        return None
    if res.count() > 1:
        raise DataOpsException("Expected one result but got more")
    return res.next()


def get_or_create_edge(
    edge_def: type[BaseEdge],
    search: dict = None,
    frm: BaseVertex = None,
    to: BaseVertex = None,
    storage_def=None,
) -> tuple[bool, dict]:
    """
    Example: `already_existed, edge = get_or_create_edge(SomeEdgeType, frm=obj1, to=obj2)`

    Tries to find an edge of type `edge_def` that matches `search` / `frm` / `to`,
    otherwise creates a new edge with said properties.

    `frm` and `to` are convenience params for passing in BaseVertexes. Same as
    specifying '_from' or '_to' keys in the `search` param.
    """
    if edge := get_edge(
        edge_def, search=search, frm=frm, to=to, storage_def=storage_def
    ):
        return True, edge
    search = _handle_get_edge_search_args(search, frm, to)
    return False, create_edge(edge_def(**search), storage_def)
