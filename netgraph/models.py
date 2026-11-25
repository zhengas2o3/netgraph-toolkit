"""Random graph generators.

All generators take an explicit ``seed`` so experiments are reproducible.
Only the Python standard library is used.
"""

from __future__ import annotations

import random

from .graph import Graph


def erdos_renyi(n, p, seed=42):
    """Return a G(n, p) Erdos-Renyi random graph.

    Each of the ``n * (n - 1) / 2`` possible edges is present
    independently with probability ``p``.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0, 1]")
    rng = random.Random(seed)
    graph = Graph()
    for i in range(n):
        graph.add_node(i)
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                graph.add_edge(i, j)
    return graph


def watts_strogatz(n, k, beta, seed=42):
    """Return a Watts-Strogatz small-world graph.

    Starts from a ring lattice where each node is connected to its ``k``
    nearest neighbours (``k`` must be even), then rewires each edge with
    probability ``beta``.  The number of edges is always ``n * k / 2``.
    """
    if k % 2 != 0:
        raise ValueError("k must be even")
    if k < 0 or k >= n:
        raise ValueError("k must satisfy 0 <= k < n")
    if not 0.0 <= beta <= 1.0:
        raise ValueError("beta must be in [0, 1]")
    rng = random.Random(seed)
    graph = Graph()
    for i in range(n):
        graph.add_node(i)
    half = k // 2
    lattice_edges = []
    for i in range(n):
        for j in range(1, half + 1):
            lattice_edges.append((i, (i + j) % n))
    for u, v in lattice_edges:
        graph.add_edge(u, v)
    # Rewire: visit each lattice edge once; with probability beta replace
    # its "forward" endpoint by a uniformly chosen non-neighbour.
    for u, v in lattice_edges:
        if rng.random() < beta:
            candidates = [
                x for x in range(n) if x != u and x not in graph.neighbors(u)
            ]
            if not candidates:
                continue
            new_v = rng.choice(candidates)
            graph.remove_edge(u, v)
            graph.add_edge(u, new_v)
    return graph


def barabasi_albert(n, m, seed=42):
    """Return a Barabasi-Albert preferential-attachment graph.

    The graph starts from a clique of ``m`` nodes; each subsequent node
    attaches to ``m`` existing nodes chosen with probability proportional
    to their degree.  The resulting graph has exactly
    ``m * (m - 1) / 2 + m * (n - m)`` edges.
    """
    if m < 1:
        raise ValueError("m must be at least 1")
    if n <= m:
        raise ValueError("n must be greater than m")
    rng = random.Random(seed)
    graph = Graph()
    for i in range(m):
        graph.add_node(i)
    for i in range(m):
        for j in range(i + 1, m):
            graph.add_edge(i, j)
    # Multiset of nodes repeated by degree, for preferential attachment.
    repeated = []
    for node in graph.nodes():
        repeated.extend([node] * graph.degree(node))
    for new in range(m, n):
        targets = set()
        while len(targets) < m:
            if repeated:
                targets.add(rng.choice(repeated))
            else:
                targets.add(rng.choice(graph.nodes()))
        graph.add_node(new)
        for t in targets:
            graph.add_edge(new, t)
        repeated.extend([new] * m)
        for t in targets:
            repeated.append(t)
    return graph
