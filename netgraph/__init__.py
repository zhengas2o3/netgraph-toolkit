"""netgraph-toolkit: dependency-free complex network analysis.

Provides an undirected graph data structure, network metrics
(clustering, shortest paths, centrality), random graph generators
(Erdos-Renyi, Watts-Strogatz, Barabasi-Albert), and label propagation
community detection with modularity scoring.
"""

from .graph import Graph, graph_from_edgelist_text, load_edgelist
from .models import barabasi_albert, erdos_renyi, watts_strogatz

__version__ = "0.1.0"

__all__ = [
    "Graph",
    "graph_from_edgelist_text",
    "load_edgelist",
    "erdos_renyi",
    "watts_strogatz",
    "barabasi_albert",
    "__version__",
]
