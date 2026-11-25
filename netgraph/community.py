"""Community detection: label propagation and modularity."""

from __future__ import annotations

import random
from collections import Counter


def label_propagation(graph, seed=42, max_iter=100):
    """Detect communities with the label propagation algorithm.

    Every node starts with its own label.  In each round, nodes are
    visited in a random (seeded) order and adopt the most frequent label
    among their neighbours; ties are broken uniformly at random using
    the seeded generator, so results are reproducible for a given seed.
    Iteration stops when no label changes or after ``max_iter`` rounds.

    Returns a dict mapping each node to its community label.
    """
    rng = random.Random(seed)
    labels = {node: node for node in graph.nodes()}
    nodes = graph.nodes()
    for _ in range(max_iter):
        order = list(nodes)
        rng.shuffle(order)
        changed = False
        for node in order:
            neighbours = graph.neighbors(node)
            if not neighbours:
                continue
            counts = Counter(labels[nbr] for nbr in neighbours)
            best_count = max(counts.values())
            candidates = [
                lab for lab, c in counts.items() if c == best_count
            ]
            best = rng.choice(candidates)
            if labels[node] != best:
                labels[node] = best
                changed = True
        if not changed:
            break
    return labels


def communities_from_labels(labels):
    """Group a node->label dict into a list of node sets."""
    groups = {}
    for node, lab in labels.items():
        groups.setdefault(lab, set()).add(node)
    return list(groups.values())


def modularity(graph, partition):
    """Newman-Girvan modularity of a partition.

    ``partition`` is a dict mapping each node to a community id.
    ``Q = sum_c [ l_c / m - (d_c / 2m)^2 ]`` where ``l_c`` is the number
    of edges inside community ``c``, ``d_c`` the sum of degrees in
    ``c``, and ``m`` the total number of edges.
    """
    m = graph.number_of_edges()
    if m == 0:
        return 0.0
    internal = Counter()
    degree_sum = Counter()
    for node in graph.nodes():
        degree_sum[partition[node]] += graph.degree(node)
    for u, v in graph.edges():
        if partition[u] == partition[v]:
            internal[partition[u]] += 1
    two_m = 2.0 * m
    q = 0.0
    for comm in degree_sum:
        q += (internal[comm] / float(m)) - (degree_sum[comm] / two_m) ** 2
    return q
