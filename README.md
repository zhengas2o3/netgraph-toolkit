# netgraph-toolkit

A dependency-free command-line toolkit for **complex network analysis** — network metrics, random graph models, and community detection, implemented from scratch with nothing but the Python standard library.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none-green)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-orange)

No NetworkX, no NumPy, no build headaches. Every algorithm — BFS shortest paths, Brandes betweenness, label propagation, preferential attachment — is implemented in plain Python in this repository, so it is easy to read, audit, and hack on.

## Features

- **Graph core** — undirected graph with an adjacency-set representation; load networks from plain-text edge lists (`#` comments supported).
- **Metrics**
  - Degree statistics and the full degree distribution
  - Average clustering coefficient
  - Average shortest-path length (BFS, computed on the largest connected component — the convention is stated in every report)
  - Degree centrality and betweenness centrality (Brandes' algorithm)
- **Random graph models** — Erdős–Rényi G(n, p), Watts–Strogatz small-world, and Barabási–Albert preferential attachment, all with explicit seeds for reproducible experiments.
- **Community detection** — label propagation, scored with Newman–Girvan modularity.
- **Markdown reports** — every command produces a clean, self-contained Markdown report you can paste into notes, papers, or issues.
- **Zero dependencies** — runs anywhere Python 3.9+ runs.

## Installation

From a clone of this repository:

```bash
git clone https://github.com/zhengas2o3/netgraph-toolkit.git
cd netgraph-toolkit
pip install .
```

This installs the `netgraph` command. Without installing, you can also run everything from the repository root as `python -m netgraph ...`.

## Quickstart

Analyse the built-in demo network (two factions joined by a bridge — a miniature of Zachary's karate club):

```bash
$ netgraph demo
```

```markdown
# Demo Network

## Overview

| Quantity | Value |
| --- | --- |
| Nodes | 14 |
| Edges | 34 |
| Density | 0.3736 |
| Connected components | 1 |
| Largest component size | 14 |

## Global metrics

| Metric | Value |
| --- | --- |
| Average clustering coefficient | 0.8190 |
| Average shortest-path length | 2.1758 |

## Communities (label propagation)

Detected **2** communities; modularity Q = 0.4702.

- Community 1 (7 nodes): 0, 1, 12, 2, 3, 4, 5
- Community 2 (7 nodes): 10, 11, 13, 6, 7, 8, 9
```

Generate a Barabási–Albert scale-free network and report on it:

```bash
$ netgraph gen --model ba --n 500 --m 3 --seed 7 --out ba-report.md
```

Analyse your own edge-list file (one `source target` pair per line, `#` comments allowed):

```bash
$ netgraph analyze examples/example_edges.txt
```

Use it as a library:

```python
from netgraph import barabasi_albert
from netgraph.metrics import average_clustering, betweenness_centrality
from netgraph.community import label_propagation, modularity

g = barabasi_albert(200, 3, seed=42)
print(average_clustering(g))          # -> e.g. 0.09...
labels = label_propagation(g, seed=42)
print(modularity(g, labels))
```

## Metrics and models

### Metrics

| Metric | Definition used here |
| --- | --- |
| Degree distribution | Histogram of node degrees over the whole graph |
| Clustering coefficient | For a node, the fraction of neighbour pairs that are themselves connected; averaged over all nodes |
| Average shortest-path length | Mean BFS distance over all unordered pairs in the **largest connected component** (inter-component distances are undefined) |
| Degree centrality | `deg(v) / (n - 1)` |
| Betweenness centrality | Brandes' algorithm; normalised by `(n - 1)(n - 2) / 2` for undirected graphs |
| Modularity | Newman–Girvan Q of a partition: `Σ_c [ l_c/m − (d_c/2m)² ]` |

### Random graph models

| Model | Command | Parameters |
| --- | --- | --- |
| Erdős–Rényi G(n, p) | `netgraph gen --model er` | `--n`, `--p` |
| Watts–Strogatz small-world | `netgraph gen --model ws` | `--n`, `--k` (even), `--beta` |
| Barabási–Albert scale-free | `netgraph gen --model ba` | `--n`, `--m` |

All generators accept `--seed` and are fully deterministic for a given seed.

### Community detection

Label propagation: every node starts with its own label and repeatedly adopts the most frequent label among its neighbours (ties broken at random from the seeded generator) until the labelling stabilises. The resulting partition is reported together with its modularity.

## Project structure

```text
netgraph-toolkit/
├── netgraph/
│   ├── __init__.py      # public API re-exports
│   ├── __main__.py      # python -m netgraph
│   ├── graph.py         # undirected graph + edge-list loading
│   ├── models.py        # ER / WS / BA generators
│   ├── metrics.py       # degree stats, clustering, paths, centrality
│   ├── community.py     # label propagation + modularity
│   ├── report.py        # Markdown report rendering
│   └── cli.py           # argparse CLI (gen / analyze / demo)
├── tests/
│   └── test_netgraph.py # unittest suite, hand-computed expectations
├── examples/
│   ├── example_edges.txt
│   └── sample-report.md
├── pyproject.toml
└── README.md
```

## Running the tests

```bash
python -m unittest discover -s tests
```

The tests verify hand-computed values on small graphs (clustering on triangles and paths, shortest paths and betweenness on a 4-node path, modularity of a known partition), exact edge counts of the BA and WS models, and that label propagation separates two cliques joined by a bridge.

## Roadmap

- [ ] Directed and weighted graphs
- [ ] Louvain community detection
- [ ] k-core decomposition and assortativity
- [ ] Export to GraphML / GEXF
- [ ] Configuration-model generator with a given degree sequence

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Ruizhao Zheng.
