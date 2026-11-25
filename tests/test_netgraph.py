"""Unit tests for netgraph-toolkit.

Expected values in these tests are computed by hand on small graphs so
the tests double as executable documentation of the definitions used.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from netgraph import Graph, graph_from_edgelist_text
from netgraph import models
from netgraph.community import (
    communities_from_labels,
    label_propagation,
    modularity,
)
from netgraph.metrics import (
    average_clustering,
    average_shortest_path_length,
    betweenness_centrality,
    clustering_coefficient,
)


def path_graph(n):
    g = Graph()
    for i in range(n - 1):
        g.add_edge(i, i + 1)
    return g


def two_triangles_with_bridge():
    g = Graph()
    for u, v in [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (2, 3)]:
        g.add_edge(u, v)
    return g


class TestGraphBasics(unittest.TestCase):
    def test_degree_and_counts(self):
        g = Graph()
        g.add_edge("a", "b")
        g.add_edge("a", "c")
        g.add_edge("a", "d")
        self.assertEqual(g.number_of_nodes(), 4)
        self.assertEqual(g.number_of_edges(), 3)
        self.assertEqual(g.degree("a"), 3)
        self.assertEqual(g.degree("b"), 1)
        self.assertEqual(g.neighbors("a"), {"b", "c", "d"})
        # Re-adding an edge must not create a multi-edge.
        g.add_edge("a", "b")
        self.assertEqual(g.number_of_edges(), 3)

    def test_edgelist_parsing_with_comments(self):
        text = "# a comment line\n\n0 1\n1 2   # trailing tokens ignored\n7\n"
        g = graph_from_edgelist_text(text)
        self.assertEqual(g.number_of_nodes(), 4)  # 0, 1, 2 and isolated 7
        self.assertEqual(g.number_of_edges(), 2)
        self.assertEqual(g.degree("7"), 0)


class TestMetrics(unittest.TestCase):
    def test_clustering_triangle_and_path(self):
        triangle = Graph()
        for u, v in [(0, 1), (1, 2), (0, 2)]:
            triangle.add_edge(u, v)
        self.assertAlmostEqual(average_clustering(triangle), 1.0)
        self.assertAlmostEqual(clustering_coefficient(triangle, 0), 1.0)
        # A path has no triangles, so clustering is 0 everywhere.
        self.assertAlmostEqual(average_clustering(path_graph(4)), 0.0)

    def test_average_shortest_path_path4(self):
        # Path 0-1-2-3: pairwise distances are 1,2,3,1,2,1 -> mean 10/6.
        self.assertAlmostEqual(
            average_shortest_path_length(path_graph(4)), 10.0 / 6.0
        )

    def test_betweenness_path4(self):
        # Hand count on path 0-1-2-3: node 1 lies on shortest paths for
        # pairs (0,2) and (0,3) -> raw 2; node 2 symmetric; endpoints 0.
        # Normalisation divides by (n-1)(n-2)/2 = 3.
        bc = betweenness_centrality(path_graph(4))
        self.assertAlmostEqual(bc[1], 2.0 / 3.0)
        self.assertAlmostEqual(bc[2], 2.0 / 3.0)
        self.assertAlmostEqual(bc[0], 0.0)
        self.assertAlmostEqual(bc[3], 0.0)


class TestModels(unittest.TestCase):
    def test_ba_edge_count(self):
        # BA starts from an m-clique and adds m edges per new node:
        # edges = m(m-1)/2 + m(n-m) = 1 + 2*18 = 37 for n=20, m=2.
        g = models.barabasi_albert(20, 2, seed=1)
        self.assertEqual(g.number_of_nodes(), 20)
        self.assertEqual(g.number_of_edges(), 37)
        # m=1 yields a tree: n-1 edges.
        tree = models.barabasi_albert(15, 1, seed=1)
        self.assertEqual(tree.number_of_edges(), 14)

    def test_ws_edge_count_is_nk_over_2(self):
        # Rewiring preserves the edge count of the ring lattice.
        for beta in (0.0, 0.5, 1.0):
            g = models.watts_strogatz(20, 4, beta, seed=3)
            self.assertEqual(g.number_of_nodes(), 20)
            self.assertEqual(g.number_of_edges(), 40)

    def test_er_reproducible_and_bounded(self):
        g1 = models.erdos_renyi(30, 0.2, seed=7)
        g2 = models.erdos_renyi(30, 0.2, seed=7)
        self.assertEqual(g1.number_of_nodes(), 30)
        self.assertEqual(
            sorted(map(str, g1.edges())), sorted(map(str, g2.edges()))
        )
        self.assertLessEqual(g1.number_of_edges(), 30 * 29 // 2)
        # p=0 and p=1 are exact.
        self.assertEqual(models.erdos_renyi(10, 0.0).number_of_edges(), 0)
        self.assertEqual(models.erdos_renyi(10, 1.0).number_of_edges(), 45)


class TestCommunity(unittest.TestCase):
    def test_label_propagation_two_cliques(self):
        g = two_triangles_with_bridge()
        labels = label_propagation(g, seed=42)
        communities = communities_from_labels(labels)
        self.assertEqual(len(communities), 2)
        sizes = sorted(len(c) for c in communities)
        self.assertEqual(sizes, [3, 3])

    def test_modularity_known_partition(self):
        # Two triangles joined by one bridge (m=7). For the natural
        # split: each side has l_c=3 internal edges and degree sum 7,
        # so Q = 2 * (3/7 - (7/14)^2) = 5/14.
        g = two_triangles_with_bridge()
        partition = {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1}
        self.assertAlmostEqual(modularity(g, partition), 5.0 / 14.0)
        # Putting everything in one community gives Q = 0.
        one = {node: 0 for node in g.nodes()}
        self.assertAlmostEqual(modularity(g, one), 0.0)


if __name__ == "__main__":
    unittest.main()
