from . import graph_defs
from .. import graph_ops
from flangoberry import logger


class SomePostSubclass(graph_defs.Post):
    ptype = "SomePostSubclass"


def test_init_post_subclass(tests_conn, cleanup):
    p = graph_ops.create_vertex(SomePostSubclass())
    assert p["_id"]
    assert p["ptype"] == "SomePostSubclass"
