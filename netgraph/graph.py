"""Core undirected graph data structure.

The graph is stored as an adjacency dictionary mapping each node to the
set of its neighbours.  Nodes may be any hashable objects; graphs loaded
from edge-list files use string labels, while the random graph generators
in :mod:`netgraph.models` use integer labels.
"""

from __future__ import annotations

from collections import deque


class Graph:
    """A simple undirected graph without self-loops or multi-edges."""

    def __init__(self):
        self._adj = {}

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def add_node(self, node):
        """Add *node* to the graph (no-op if it already exists)."""
        self._adj.setdefault(node, set())

    def add_edge(self, u, v):
        """Add the undirected edge ``u -- v``.

        Self-loops are ignored (the node itself is still registered).
        Adding an edge implicitly adds its endpoints.
        """
        self.add_node(u)
        self.add_node(v)
        if u == v:
            return
        self._adj[u].add(v)
        self._adj[v].add(u)

    def remove_edge(self, u, v):
        """Remove the edge ``u -- v`` if present."""
        if u in self._adj:
            self._adj[u].discard(v)
        if v in self._adj:
            self._adj[v].discard(u)

    # ------------------------------------------------------------------
    # Basic queries
    # ------------------------------------------------------------------
    def nodes(self):
        """Return a list of all nodes (insertion order)."""
        return list(self._adj.keys())

    def number_of_nodes(self):
        return len(self._adj)

    def number_of_edges(self):
        return sum(len(nbrs) for nbrs in self._adj.values()) // 2

    def edges(self):
        """Return a list of edges as ``(u, v)`` tuples, each listed once."""
        out = []
        seen = set()
        for u, nbrs in self._adj.items():
            for v in nbrs:
                if (v, u) not in seen:
                    seen.add((u, v))
                    out.append((u, v))
        return out

    def neighbors(self, node):
        """Return a copy of the neighbour set of *node*."""
        return set(self._adj.get(node, ()))

    def degree(self, node):
        """Return the degree of *node* (0 for unknown nodes)."""
        return len(self._adj.get(node, ()))

    def has_node(self, node):
        return node in self._adj

    def has_edge(self, u, v):
        return v in self._adj.get(u, ())

    def __contains__(self, node):
        return node in self._adj

    def __iter__(self):
        return iter(self._adj)

    def __len__(self):
        return len(self._adj)

    def __repr__(self):
        return "Graph(nodes={}, edges={})".format(
            self.number_of_nodes(), self.number_of_edges()
        )

    # ------------------------------------------------------------------
    # Connectivity helpers
    # ------------------------------------------------------------------
    def connected_components(self):
        """Return a list of connected components, each a set of nodes."""
        visited = set()
        components = []
        for start in self._adj:
            if start in visited:
                continue
            comp = set()
            queue = deque([start])
            visited.add(start)
            while queue:
                v = queue.popleft()
                comp.add(v)
                for w in self._adj[v]:
                    if w not in visited:
                        visited.add(w)
                        queue.append(w)
            components.append(comp)
        return components

    def largest_connected_component(self):
        """Return the largest connected component as a set of nodes."""
        components = self.connected_components()
        if not components:
            return set()
        return max(components, key=len)


# ----------------------------------------------------------------------
# Edge-list loading
# ----------------------------------------------------------------------
def graph_from_edgelist_text(text):
    """Build a :class:`Graph` from edge-list text.

    Format: one edge per line, two whitespace-separated node labels.
    Blank lines and lines starting with ``#`` are ignored.  A line with a
    single token registers an isolated node.  Extra columns after the
    first two tokens are ignored, so simple weighted files still load.
    Node labels are kept as strings.
    """
    graph = Graph()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) == 1:
            graph.add_node(parts[0])
        else:
            graph.add_edge(parts[0], parts[1])
    return graph


def load_edgelist(path):
    """Load a graph from an edge-list file at *path*."""
    with open(path, "r", encoding="utf-8") as fh:
        return graph_from_edgelist_text(fh.read())
