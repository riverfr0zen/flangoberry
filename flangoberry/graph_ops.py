from collections import namedtuple
from flangoberry import logger
from flangoberry import db
from .graph_defs import BaseVertex, BaseEdge
from datetime import datetime, timezone
from arango.exceptions import DocumentInsertError, DocumentUpdateError
from strawberry import UNSET as STRAWBERRY_UNSET
from arango.cursor import Cursor


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

    # @TODO Add test coverage. See how it's done for vertices.
    if persistent_indexes := storage_def.get("persistent_indexes", None):
        for p_index in persistent_indexes:
            p_index["in_background"] = True
            coll.add_persistent_index(**p_index)

    return EdgeStorage(dbase, graph, coll)


def create_vertex(vertex: BaseVertex, storage_def=None) -> dict:
    if not isinstance(vertex, BaseVertex):
        raise DataOpsException("`vertex` must be an instance of BaseVertex")

    storage = resolve_vertex_storage(vertex, storage_def)
    try:
        return storage.collection.insert(vertex, return_new=True)["new"]
    except DocumentInsertError as e:
        raise DataOpsException(f"arango.exceptions.DocumentInsertError: {e}")


def update_vertex(vertex: BaseVertex, storage_def=None) -> dict:
    if not isinstance(vertex, BaseVertex):
        raise DataOpsException("`vertex` must be an instance of BaseVertex")

    if "created" in vertex:
        del vertex["created"]
    vertex["modified"] = datetime.now(timezone.utc).isoformat()
    # Making use of the strawberry.UNSET value to remove optional fields that weren't set
    unset_fields = [f for f, v in vertex.items() if v == STRAWBERRY_UNSET]
    for field in unset_fields:
        vertex.pop(field)

    storage = resolve_vertex_storage(vertex, storage_def)
    try:
        return storage.collection.update(vertex, return_new=True)["new"]
    except DocumentUpdateError as e:
        raise DataOpsException(f"arango.exceptions.DocumentUpdateError: {e}")


def delete_vertex(vertex_def: type[BaseVertex], id: str, storage_def=None) -> bool:
    storage = resolve_vertex_storage(vertex_def, storage_def)
    return storage.collection.delete({"_id": id})


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
    vertex_def: type[BaseVertex],
    search: dict,
    new_doc: dict | None = None,
    storage_def: dict = None,
) -> tuple[bool, dict]:
    """
    Example: `already_existed, vertex = get_or_create_vertex(SomeVertexType, {'name': 'Some name'})`

    Tries to find a vertex of type `vertex_def` that has the properties in `search`,
    otherwise creates a new vertex with said properties.
    """
    if vertex := get_vertex(vertex_def, search, storage_def):
        return True, vertex
    if not new_doc:
        new_doc = search
    return False, create_vertex(vertex_def(**new_doc))


def create_edge(edge: BaseEdge, storage_def=None) -> dict:
    if not isinstance(edge, BaseEdge):
        raise DataOpsException("`edge` must be an instance of BaseEdge")

    storage = resolve_edge_storage(edge, storage_def)
    try:
        edge = storage.collection.insert(edge, return_new=True)
        now = datetime.now(timezone.utc).isoformat()
        storage.db.update_document(
            {"_id": edge["new"]["_to"], "is_root": False, "inbound_modified": now}
        )
        storage.db.update_document({"_id": edge["new"]["_from"], "is_leaf": False})
        return edge["new"]
    except DocumentInsertError as e:
        raise DataOpsException(f"arango.exceptions.DocumentInsertError: {e}")


def update_edge(edge: BaseEdge, storage_def=None) -> dict:
    if not isinstance(edge, BaseEdge):
        raise DataOpsException("`edge` must be an instance of BaseEdge")

    if "created" in edge:
        del edge["created"]
    edge["modified"] = datetime.now(timezone.utc).isoformat()

    storage = resolve_edge_storage(edge, storage_def)
    try:
        return storage.collection.update(edge, return_new=True)["new"]
    except DocumentUpdateError as e:
        raise DataOpsException(f"arango.exceptions.DocumentUpdateError: {e}")


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
    new_doc: dict = None,
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
    if new_doc:
        new_doc = _handle_get_edge_search_args(new_doc, frm, to)
    else:
        new_doc = _handle_get_edge_search_args(search, frm, to)

    return False, create_edge(edge_def(**new_doc), storage_def)


def list_vertex_edges_by_id(
    db,
    graph_name: str,
    vertex_id: str,
    outbound_only: bool = False,
    inbound_only: bool = False,
) -> Cursor:
    direction = "ANY"
    if outbound_only:
        direction = "OUTBOUND"
    if inbound_only:
        direction = "INBOUND"
    bind_vars = {
        "graph_name": graph_name,
        "vertex_id": vertex_id,
    }

    query = f"""
        FOR v, e IN 1 {direction} @vertex_id
        GRAPH @graph_name
        SORT
            e.modified DESC
        RETURN {{
            vertex: v,
            edge: e,
            direction: e._to == v._id ? 'outbound' : 'inbound'
        }}
    """

    return db.aql.execute(query, bind_vars=bind_vars, count=True)


def list_vertex_edges(
    vertex_def: type[BaseVertex],
    vertex_id: str,
    outbound_only: bool = False,
    inbound_only: bool = False,
) -> Cursor:
    """Returns the immediate (depth == 1) edges of the vertex"""
    (db, graph, collection) = resolve_vertex_storage(vertex_def)
    return list_vertex_edges_by_id(
        db, graph.name, vertex_id, outbound_only, inbound_only
    )


def delete_edge(edge_def: type[BaseEdge], id: str, storage_def=None) -> bool:
    storage = resolve_edge_storage(edge_def, storage_def)
    res = storage.collection.delete({"_id": id}, return_old=True)
    # logger.debug(res)
    if res:
        from_vertex_id = res["old"]["_from"]
        edges_cursor = list_vertex_edges_by_id(
            storage.db, storage.graph.name, from_vertex_id, outbound_only=True
        )
        if edges_cursor.count() == 0:
            res = storage.graph.update_vertex({"_id": from_vertex_id, "is_leaf": True})
        return True
    return False


def get_collection_name_from_id(id: str):
    return id.split("/")[0]
