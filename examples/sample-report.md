# Network Report: examples/example_edges.txt

## Overview

| Quantity | Value |
| --- | --- |
| Nodes | 11 |
| Edges | 22 |
| Density | 0.4000 |
| Connected components | 1 |
| Largest component size | 11 |

## Degree statistics

| Quantity | Value |
| --- | --- |
| Min degree | 1 |
| Max degree | 5 |
| Mean degree | 4.0000 |

Degree distribution (degree: number of nodes):

```text
1: 1
4: 7
5: 3
```

## Global metrics

| Metric | Value |
| --- | --- |
| Average clustering coefficient | 0.8000 |
| Average shortest-path length | 2.0545 |

_Shortest paths are averaged over the largest connected component (11 of 11 nodes); distances between components are undefined._

## Most central nodes

By degree centrality:

- `a1`: 0.5000
- `a3`: 0.5000
- `b3`: 0.5000
- `a2`: 0.4000
- `a4`: 0.4000

By betweenness centrality:

- `a3`: 0.5556
- `b3`: 0.5333
- `a1`: 0.2000
- `a2`: 0.0000
- `a4`: 0.0000

## Communities (label propagation)

Detected **2** communities; modularity Q = 0.4535.

- Community 1 (6 nodes): a1, a2, a3, a4, a5, x1
- Community 2 (5 nodes): b1, b2, b3, b4, b5
