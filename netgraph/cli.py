"""Command-line interface for netgraph-toolkit.

Subcommands
-----------
gen      Generate a random graph (ER / WS / BA) and print its report.
analyze  Load an edge-list file and print its report.
demo     Analyse a small built-in example graph and print its report.
"""

from __future__ import annotations

import argparse
import sys

from .graph import Graph, load_edgelist
from .models import barabasi_albert, erdos_renyi, watts_strogatz
from .report import render_report


def build_demo_graph():
    """A small two-community example graph (14 nodes).

    Two 6-node cliques joined by a single bridge edge, plus two extra
    nodes attached to the second clique and the first clique
    respectively -- a miniature of the "two factions" structure made
    famous by Zachary's karate club network.
    """
    graph = Graph()

    def clique(nodes):
        for i, u in enumerate(nodes):
            for v in nodes[i + 1:]:
                graph.add_edge(u, v)

    clique(list(range(0, 6)))
    clique(list(range(6, 12)))
    graph.add_edge(2, 8)    # the bridge between the two groups
    graph.add_edge(0, 12)   # pendant node on group A
    graph.add_edge(9, 13)   # extra node attached inside group B
    graph.add_edge(10, 13)
    return graph


def _emit(report, out):
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(report)
        print("Report written to {}".format(out), file=sys.stderr)
    else:
        print(report)


def _cmd_gen(args):
    if args.model == "er":
        graph = erdos_renyi(args.n, args.p, seed=args.seed)
        title = "Erdos-Renyi G({}, p={})".format(args.n, args.p)
    elif args.model == "ws":
        graph = watts_strogatz(args.n, args.k, args.beta, seed=args.seed)
        title = "Watts-Strogatz (n={}, k={}, beta={})".format(
            args.n, args.k, args.beta
        )
    else:  # ba
        graph = barabasi_albert(args.n, args.m, seed=args.seed)
        title = "Barabasi-Albert (n={}, m={})".format(args.n, args.m)
    _emit(render_report(graph, title=title, seed=args.seed), args.out)
    return 0


def _cmd_analyze(args):
    graph = load_edgelist(args.file)
    title = "Network Report: {}".format(args.file)
    _emit(render_report(graph, title=title, seed=args.seed), args.out)
    return 0


def _cmd_demo(args):
    graph = build_demo_graph()
    _emit(
        render_report(graph, title="Demo Network", seed=args.seed),
        args.out,
    )
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="netgraph",
        description=(
            "Complex network analysis toolkit: metrics, random graph "
            "models, and community detection (standard library only)."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("gen", help="generate a random graph and report")
    p_gen.add_argument(
        "--model",
        choices=["er", "ws", "ba"],
        default="ba",
        help="random graph model: er=Erdos-Renyi, ws=Watts-Strogatz, "
        "ba=Barabasi-Albert (default: ba)",
    )
    p_gen.add_argument("--n", type=int, default=100, help="number of nodes")
    p_gen.add_argument(
        "--p", type=float, default=0.05, help="ER edge probability"
    )
    p_gen.add_argument(
        "--k", type=int, default=4, help="WS neighbours per node (even)"
    )
    p_gen.add_argument(
        "--beta", type=float, default=0.1, help="WS rewiring probability"
    )
    p_gen.add_argument(
        "--m", type=int, default=3, help="BA edges per new node"
    )
    p_gen.add_argument("--seed", type=int, default=42, help="random seed")
    p_gen.add_argument("--out", help="write report to this file")
    p_gen.set_defaults(func=_cmd_gen)

    p_an = sub.add_parser("analyze", help="analyse an edge-list file")
    p_an.add_argument("file", help="path to the edge-list file")
    p_an.add_argument("--seed", type=int, default=42, help="random seed")
    p_an.add_argument("--out", help="write report to this file")
    p_an.set_defaults(func=_cmd_analyze)

    p_demo = sub.add_parser("demo", help="run the built-in demo graph")
    p_demo.add_argument("--seed", type=int, default=42, help="random seed")
    p_demo.add_argument("--out", help="write report to this file")
    p_demo.set_defaults(func=_cmd_demo)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
