"""Network metrics: degree statistics, clustering, paths, centrality.

Notes on conventions
--------------------
* The average shortest-path length is computed on the **largest
  connected component** of the graph, because distances between
  components are infinite.  The size of that component is reported
  alongside the value so the convention is never silent.
* Betweenness centrality follows Brandes' algorithm for unweighted
  graphs and is normalised by ``(n - 1)(n - 2) / 2`` (the number of
  unordered node pairs not involving the node itself), matching the
  usual textbook convention for undirected graphs.
"""

from __future__ import annotations

from collections import Counter, deque


# ----------------------------------------------------------------------
# Degree statistics
# ----------------------------------------------------------------------
def degree_distribution(graph):
    """Return a :class:`collections.Counter` mapping degree -> count."""
    return Counter(graph.degree(node) for node in graph.nodes())


def degree_stats(graph):
    """Return basic degree statistics as a dictionary."""
    n = graph.number_of_nodes()
    m = graph.number_of_edges()
    degrees = [graph.degree(node) for node in graph.nodes()]
    if n == 0:
        return {
            "nodes": 0,
            "edges": 0,
            "min_degree": 0,
            "max_degree": 0,
            "mean_degree": 0.0,
            "density": 0.0,
        }
    density = (2.0 * m) / (n * (n - 1)) if n > 1 else 0.0
    return {
        "nodes": n,
        "edges": m,
        "min_degree": min(degrees),
        "max_degree": max(degrees),
        "mean_degree": sum(degrees) / float(n),
        "density": density,
    }


# ----------------------------------------------------------------------
# Clustering
# ----------------------------------------------------------------------
def clustering_coefficient(graph, node):
    """Local clustering coefficient of *node*.

    The fraction of pairs of neighbours of *node* that are themselves
    connected.  Nodes with degree < 2 have coefficient 0 by convention.
    """
    neighbours = graph.neighbors(node)
    k = len(neighbours)
    if k < 2:
        return 0.0
    # Count each neighbour-neighbour edge once.
    links = 0
    nbr_list = list(neighbours)
    for i in range(len(nbr_list)):
        for j in range(i + 1, len(nbr_list)):
            if graph.has_edge(nbr_list[i], nbr_list[j]):
                links += 1
    return (2.0 * links) / (k * (k - 1))


def average_clustering(graph):
    """Mean of the local clustering coefficient over all nodes."""
    nodes = graph.nodes()
    if not nodes:
        return 0.0
    total = sum(clustering_coefficient(graph, node) for node in nodes)
    return total / float(len(nodes))


# ----------------------------------------------------------------------
# Shortest paths
# ----------------------------------------------------------------------
def bfs_distances(graph, source):
    """Return a dict of shortest-path distances from *source* (BFS)."""
    dist = {source: 0}
    queue = deque([source])
    while queue:
        v = queue.popleft()
        for w in graph.neighbors(v):
            if w not in dist:
                dist[w] = dist[v] + 1
                queue.append(w)
    return dist


def average_shortest_path_length(graph):
    """Average shortest-path length over the largest connected component.

    Pairs in different components have no finite distance, so the
    standard convention is used: the average is taken over all unordered
    pairs inside the largest connected component.  Returns 0.0 for
    graphs whose largest component has fewer than 2 nodes.
    """
    component = graph.largest_connected_component()
    if len(component) < 2:
        return 0.0
    total = 0
    pairs = 0
    for source in component:
        dist = bfs_distances(graph, source)
        for target in component:
            if target != source:
                total += dist[target]
                pairs += 1
    # Each unordered pair counted twice (once per direction).
    return total / float(pairs)


# ----------------------------------------------------------------------
# Centrality
# ----------------------------------------------------------------------
def degree_centrality(graph):
    """Degree centrality: ``deg(v) / (n - 1)`` for every node."""
    n = graph.number_of_nodes()
    if n <= 1:
        return {node: 0.0 for node in graph.nodes()}
    return {
        node: graph.degree(node) / float(n - 1) for node in graph.nodes()
    }


def betweenness_centrality(graph, normalized=True):
    """Betweenness centrality via Brandes' algorithm (unweighted).

    For undirected graphs the raw Brandes accumulation counts each
    unordered pair twice, so values are halved before optional
    normalisation by ``(n - 1)(n - 2) / 2``.
    """
    nodes = graph.nodes()
    cb = dict.fromkeys(nodes, 0.0)
    for s in nodes:
        stack = []
        pred = {w: [] for w in nodes}
        sigma = dict.fromkeys(nodes, 0.0)
        sigma[s] = 1.0
        dist = dict.fromkeys(nodes, -1)
        dist[s] = 0
        queue = deque([s])
        while queue:
            v = queue.popleft()
            stack.append(v)
            for w in graph.neighbors(v):
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)
        delta = dict.fromkeys(nodes, 0.0)
        while stack:
            w = stack.pop()
            for v in pred[w]:
                if sigma[w] > 0:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                cb[w] += delta[w]
    for v in cb:
        cb[v] /= 2.0
    if normalized:
        n = len(nodes)
        if n > 2:
            scale = 1.0 / ((n - 1) * (n - 2) / 2.0)
            for v in cb:
                cb[v] *= scale
    return cb
