import networkx as nx
from app.services.failure_impact_analyzer import calculate_impact


def _depth(graph: nx.DiGraph, node: str) -> int:
    distances = nx.single_source_shortest_path_length(graph, node)
    return max(distances.values(), default=0)


def analyze_structure(graph: nx.DiGraph) -> dict:
    degree = dict(graph.degree())
    centrality = nx.betweenness_centrality(graph)
    rows = []
    for node in graph.nodes:
        impact = calculate_impact(graph, node)
        rows.append({"name": node, "connections": degree[node], "downstream_reach": impact["blast_radius"],
                     "betweenness_centrality": round(centrality[node], 4), "dependency_depth": _depth(graph, node)})
    rows.sort(key=lambda item: (-item["connections"], item["name"]))
    cycles = []
    for cycle in nx.simple_cycles(graph):
        start = min(range(len(cycle)), key=lambda index: cycle[index])
        canonical = cycle[start:] + cycle[:start]
        cycles.append(canonical + [canonical[0]])
    cycles = sorted(cycles, key=lambda c: (len(c), c))[:20]
    paths = []
    condensed = nx.condensation(graph)
    if nx.is_directed_acyclic_graph(condensed):
        for source in sorted(n for n in graph if graph.in_degree(n) == 0):
            for target in sorted(n for n in graph if graph.out_degree(n) == 0):
                for path in nx.all_simple_paths(graph, source, target, cutoff=8):
                    if len(path) >= 3:
                        paths.append(path)
    paths = sorted(paths, key=lambda p: (-len(p), p))[:5]
    return {"components": rows, "most_connected": rows[:5], "cycles": cycles,
            "critical_paths": [{"path": path, "length": len(path) - 1, "affected_components": len(path) - 1} for path in paths]}
