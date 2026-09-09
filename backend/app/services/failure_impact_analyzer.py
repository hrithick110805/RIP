from collections import deque
import networkx as nx


def calculate_impact(graph: nx.DiGraph, component: str) -> dict:
    if component not in graph:
        raise KeyError(component)
    distances: dict[str, int] = {}
    queue = deque((consumer, 1) for consumer in sorted(graph.predecessors(component)))
    while queue:
        node, distance = queue.popleft()
        if node == component or (node in distances and distances[node] <= distance):
            continue
        distances[node] = distance
        queue.extend((consumer, distance + 1) for consumer in sorted(graph.predecessors(node)))
    direct = sorted(node for node, distance in distances.items() if distance == 1)
    indirect = sorted(node for node, distance in distances.items() if distance > 1)
    categorized = {kind: [] for kind in ("application", "database", "external_system", "service", "unresolved")}
    for node in distances:
        categorized.setdefault(graph.nodes[node].get("type", "unresolved"), []).append(node)
    return {"component": component, "upstream": sorted(graph.successors(component)), "direct_impact": direct,
            "indirect_impact": indirect, "blast_radius": len(distances), "distances": distances,
            "affected_applications": sorted(categorized["application"]), "affected_databases": sorted(categorized["database"]),
            "affected_external_systems": sorted(categorized["external_system"]), "affected_services": sorted(categorized["service"])}
