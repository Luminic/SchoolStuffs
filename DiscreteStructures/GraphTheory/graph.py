from __future__ import annotations
from collections import defaultdict
from typing import Union, Optional
import warnings

import os
import sys

# Try to import linear algebra
la_available: bool
try:
    # Add a couple paths that might work
    sys.path.append(os.getcwd() + "/LinearAlg")
    sys.path.append(os.getcwd() + "/../../LinearAlg")
    import linear_alg as la
    la_available = True
except ImportError:
    la_available = False
    warnings.warn("Failed to load linear_alg. Some functionality may be unavailable", ImportWarning)


class Vertex:
    """
    `name` is just there to be nice. The important part of a Vertex is its id
    """
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"Vertex({self.name})"

    def __str__(self) -> str:
        return self.name


class Edge:
    """An edge between `v1` and `v2`

    If `directed` is `False`, `id(v1)` will always be less than `id(v2)` so an
    there should only be one possible representation of an edge between two points
    """

    _v1: Vertex
    _v2: Vertex
    _directed: bool

    def __init__(self, v1: Vertex, v2: Vertex, directed: bool = False):
        self._directed = directed

        if not self._directed:
            if id(v2) < id(v1):
                (v1, v2) = (v2, v1)

        self._v1 = v1
        self._v2 = v2
    
    @property
    def v1(self) -> Vertex: return self._v1
    
    @property
    def v2(self) -> Vertex: return self._v2
    
    @property
    def directed(self) -> bool: return self._directed

    def __str__(self) -> str:
        res = f"{self.v1}, {self.v2}"
        if self.directed:
            return "(" + res + ")"
        else:
            return "{" + res + "}"
    
    def __repr__(self) -> str:
        return f"Edge({self.v1}, {self.v2}, {self.directed})"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Edge):
            return self.v1 == other.v1 and self.v2 == other.v2 and self.directed == other.directed
        return False

    def __hash__(self) -> int:
        return hash((self.v1, self.v2, self.directed,))
    
    def is_loop(self) -> bool:
        return self.v1 == self.v2
    
    def directional_counterpart(self) -> Edge:
        assert self.directed
        return Edge(self.v2, self.v1, self.directed)
    
    def has_vertex(self, vertex: Vertex) -> bool:
        return vertex == self.v1 or vertex == self.v2


class Graph:
    """Constructs a graph with `vertices` and `edges`

    TODO: actually write documentation lol
    """
    vertices: set[Vertex]
    edges: defaultdict[Edge,int]
    simple: bool
    directed: bool

    def __init__(self,
        vertices: Optional[set[Vertex]] = None,
        edges: Union[dict[Edge, int], set[Edge, int], None] = None,
        simple: bool = False,
        directed: bool = False,
    ) -> None:
        """Initializes the Graph as you'd expect

        `edges` will be converted into a `defaultdict`
        """

        self.simple = simple
        self.directed = directed

        self.vertices = vertices if vertices != None else set()

        if edges == None: edges = {}
        if (isinstance(edges, set)): # Convert the set into a dict
            edges = {e:1 for e in edges}
        
        self.edges = defaultdict(lambda: 0, edges)
    
    def __str__(self):
        return "({" + ", ".join(map(str, self.vertices)) + "}, {" + ", ".join(map(str, self.edges)) + "})"
    
    def has_vertex(self, vertex: Vertex) -> bool:
        return vertex in self.vertices
    
    def add_vertex(self, vertex: Vertex) -> None:
        self.vertices.add(vertex)
    
    def remove_vertex(self, vertex: Vertex, remove_hanging_edges: bool = True) -> None:
        if remove_hanging_edges:
            for edge in list(self.edges.keys()):
                if edge.has_vertex(vertex):
                    del self.edges[edge]

        self.vertices.remove(vertex)

    def has_edge(self, edge: Edge) -> bool:
        """Checks if `edge` is in the graph"""

        if self.edges[edge] > 0: return True
        return False
    
    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph"""

        self.edges[edge] += 1
    
    def add_edge_safe(self, edge: Edge, convert: bool=False) -> bool:
        """Add an edge to the graph if the edge is valid.
        
        If `convert` is `True` it will try to convert the edge into a valid form

        Returns `True` if the edge is sucessfully added to the graph. Returns `False` otherwise.
        """

        if self.directed != edge.directed:
            if convert: edge = Edge(edge.v1, edge.v2, self.directed)
            else: return False
        
        if self.simple:
            if edge.is_loop(): return False
            if self.has_edge(edge): return False # no parallel edges

        self.edges[edge] += 1
        return True

    def remove_edge(self, edge: Edge, remove_all: bool = False) -> None:
        if remove_all or self.edges[edge] <= 1: del self.edges[edge]
        else: self.edges[edge] -= 1

    def clear(self) -> None:
        self.vertices = set()
        self.edges = defaultdict(lambda: 0)
    
    def adjacency_matrix_list(self, vertex_order: Union[list[Vertex], dict[Vertex, int], None] = None) -> list[list[int]]:
        """Returns a row-major adjacency matrix for the graph as nested lists"""
        if not isinstance(vertex_order, dict):
            if vertex_order == None:
                vertex_order = sorted(self.vertices, key=lambda v: v.name)
            vertex_order = {v:i for i,v in enumerate(vertex_order)}

        adj_mat = []
        for _ in range(len(self.vertices)): adj_mat.append([0]*len(self.vertices))

        for edge, multiplicity in self.edges.items():
            if self.directed or edge.is_loop():
                adj_mat[vertex_order[edge.v1]][vertex_order[edge.v2]] += multiplicity
            else:
                adj_mat[vertex_order[edge.v1]][vertex_order[edge.v2]] += multiplicity
                adj_mat[vertex_order[edge.v2]][vertex_order[edge.v1]] += multiplicity
                
        return adj_mat
    
    def adjacency_matrix(self) -> Optional[la.Matrix]:
        """Returns the adjacency matrix

        If the linear algebra import failed (`la_available=False`), it will return
        `None`. For a function that will never fail, see `adjacency_matrix_list`.
        """
        if la_available and len(self.vertices) > 0:
            return la.Matrix(self.adjacency_matrix_list())
        return None


if __name__ == "__main__":
    a = Vertex("A")
    b = Vertex("B")
    c = Vertex("C")

    edges = {Edge(a,b), Edge(a,c)}

    # g = Graph({a,b,c}, edges, simple=True)
    g = Graph()
    print(g)


    # from pprint import pprint
    # import inspect
    # pprint(inspect.getmembers(Edge, inspect.isfunction))
