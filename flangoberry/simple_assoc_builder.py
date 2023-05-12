import re
from typing import List, Type, Tuple, Optional
from dataclasses import dataclass
from flangoberry import logger
from .graph_defs import BaseVertex, BaseEdge
from .graph_ops import get_or_create_vertex, get_or_create_edge


def _split_tokens(text: str) -> List[str]:
    if text.lstrip()[0] == "-":
        raise ValueError(
            f"First item in description must be a node, not an edge: {text}"
        )
    rel_pattern = r" \-([a-zA-Z]+)\-\> "
    return re.split(rel_pattern, text)


def tokenize(text: str) -> List[Tuple[str, str] | str]:
    """Breaks up text into a python dict representing the operations
    that should take place"""
    return [
        tuple(token.split(":")) if ":" in token else token
        for token in _split_tokens(text)
    ]


@dataclass
class SimpleAssociationBuilder:
    node_defs: List[Type[BaseVertex]]
    edge_defs: List[Type[BaseEdge]]

    def get_node_def(self, def_cls_name: str) -> Type[BaseVertex]:
        try:
            return [cls for cls in self.node_defs if cls.__name__ == def_cls_name][0]
        except IndexError:
            raise IndexError(f"Builder does not know about node_def `{def_cls_name}`")

    def get_edge_def(self, def_cls_name: str) -> Type[BaseEdge]:
        try:
            return [cls for cls in self.edge_defs if cls.__name__ == def_cls_name][0]
        except IndexError:
            raise IndexError(f"Builder does not know about edge_def `{def_cls_name}`")

    def build_associations(self, description: str) -> List[BaseVertex | BaseEdge]:
        """Create associations outward from a node based on a simple description format.

        `Note:MyNote -IsAbout-> Topic:ArangoDB -IsTypeOf-> Topic:Graph Databases`

        If any node described in the input does not exist (based on the specified type and name),
        a new node of that type will be created, featuring a `name` property assigned with the
        specified name."""
        tokens = tokenize(description)
        objs = self.process_tokens(tokens)
        return objs

    def process_tokens(
        self,
        tokens: List[Tuple[str, str] | str],
        pos: int = 0,
        graph_objs: Optional[List[BaseVertex | BaseEdge]] = None,
    ) -> List[BaseVertex | BaseEdge]:
        """Recursively go through list of tokens to build association"""
        if not graph_objs:
            graph_objs = []
        token = tokens[pos]
        if type(token) is tuple:
            node_type, node_name = token
            # logger.debug(f"Examining node {node_name} of type {node_type}")
            node_cls = self.get_node_def(node_type)
            existed, node_data = get_or_create_vertex(node_cls, {"name": node_name})
            if pos > 0:
                # logger.debug(f"Looking at preceding items...")
                parent_node_data = graph_objs[pos - 2]
                # Given the expected input, the incoming edge type would be in the token
                # before this one
                edge_cls = self.get_edge_def(tokens[pos - 1])
                existed, edge_data = get_or_create_edge(
                    edge_cls, frm=parent_node_data, to=node_data
                )
                graph_objs.append(edge_data)
            graph_objs.append(node_data)
        # Nothing to do for edges
        # if type(token) is str:
        #     logger.debug(f"Examining edge {token}")
        #     logger.debug("Leaving...\n")

        if pos + 1 < len(tokens):
            return self.process_tokens(tokens, pos + 1, graph_objs)
        return graph_objs
