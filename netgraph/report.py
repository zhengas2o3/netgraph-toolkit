"""Render a full Markdown analysis report for a graph."""

from __future__ import annotations

from . import metrics
from .community import communities_from_labels, label_propagation, modularity


def _fmt(x):
    return "{:.4f}".format(x)


def _top_items(scores, limit=5):
    return sorted(scores.items(), key=lambda kv: (-kv[1], str(kv[0])))[:limit]


def render_report(graph, title="Network Report", seed=42):
    """Return a Markdown report with metrics and community structure.

    The report contains: size and degree statistics, the degree
    distribution, average clustering, average shortest-path length
    (with the connected-component convention stated explicitly), the
    top nodes by degree and betweenness centrality, and the label
    propagation communities together with their modularity.
    """
    stats = metrics.degree_stats(graph)
    components = graph.connected_components()
    largest = graph.largest_connected_component()
    labels = label_propagation(graph, seed=seed)
    communities = communities_from_labels(labels)
    q = modularity(graph, labels)
    deg_cent = metrics.degree_centrality(graph)
    bet_cent = metrics.betweenness_centrality(graph)
    distribution = metrics.degree_distribution(graph)

    lines = []
    lines.append("# {}".format(title))
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("| Quantity | Value |")
    lines.append("| --- | --- |")
    lines.append("| Nodes | {} |".format(stats["nodes"]))
    lines.append("| Edges | {} |".format(stats["edges"]))
    lines.append("| Density | {} |".format(_fmt(stats["density"])))
    lines.append("| Connected components | {} |".format(len(components)))
    lines.append(
        "| Largest component size | {} |".format(len(largest))
    )
    lines.append("")
    lines.append("## Degree statistics")
    lines.append("")
    lines.append("| Quantity | Value |")
    lines.append("| --- | --- |")
    lines.append("| Min degree | {} |".format(stats["min_degree"]))
    lines.append("| Max degree | {} |".format(stats["max_degree"]))
    lines.append("| Mean degree | {} |".format(_fmt(stats["mean_degree"])))
    lines.append("")
    lines.append("Degree distribution (degree: number of nodes):")
    lines.append("")
    lines.append("```text")
    for degree in sorted(distribution):
        lines.append("{}: {}".format(degree, distribution[degree]))
    lines.append("```")
    lines.append("")
    lines.append("## Global metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    lines.append(
        "| Average clustering coefficient | {} |".format(
            _fmt(metrics.average_clustering(graph))
        )
    )
    lines.append(
        "| Average shortest-path length | {} |".format(
            _fmt(metrics.average_shortest_path_length(graph))
        )
    )
    lines.append("")
    lines.append(
        "_Shortest paths are averaged over the largest connected "
        "component ({} of {} nodes); distances between components are "
        "undefined._".format(len(largest), stats["nodes"])
    )
    lines.append("")
    lines.append("## Most central nodes")
    lines.append("")
    lines.append("By degree centrality:")
    lines.append("")
    for node, score in _top_items(deg_cent):
        lines.append("- `{}`: {}".format(node, _fmt(score)))
    lines.append("")
    lines.append("By betweenness centrality:")
    lines.append("")
    for node, score in _top_items(bet_cent):
        lines.append("- `{}`: {}".format(node, _fmt(score)))
    lines.append("")
    lines.append("## Communities (label propagation)")
    lines.append("")
    lines.append(
        "Detected **{}** communities; modularity Q = {}.".format(
            len(communities), _fmt(q)
        )
    )
    lines.append("")
    ordered = sorted(communities, key=lambda c: (-len(c), str(min(c, key=str))))
    for idx, comm in enumerate(ordered, start=1):
        members = ", ".join(str(x) for x in sorted(comm, key=str))
        lines.append(
            "- Community {} ({} nodes): {}".format(idx, len(comm), members)
        )
    lines.append("")
    return "\n".join(lines)
