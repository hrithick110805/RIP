import networkx as nx
from app.services.failure_impact_analyzer import calculate_impact


def deploy_ripple_stopper(graph: nx.DiGraph, failed_component: str, protected_consumer: str) -> dict:
    """Recalculate propagation after isolating one consumer from a failed dependency.

    Graph edges point consumer -> dependency, so protecting Payment Service -> Order
    Service means temporarily removing Order Service -> Payment Service on a copy.
    The stored architecture is never modified.
    """
    if failed_component not in graph or protected_consumer not in graph:
        raise KeyError("The failed component or protected consumer does not exist")
    if not graph.has_edge(protected_consumer, failed_component):
        raise ValueError(f"{protected_consumer} is not a direct consumer of {failed_component}")

    before = calculate_impact(graph, failed_component)
    protected_graph = graph.copy()
    protected_graph.remove_edge(protected_consumer, failed_component)
    after = calculate_impact(protected_graph, failed_component)
    before_affected = set(before["direct_impact"] + before["indirect_impact"])
    after_affected = set(after["direct_impact"] + after["indirect_impact"])
    saved = sorted(before_affected - after_affected)

    return {
        "failed_component": failed_component,
        **after,
        "stopper_deployed": True,
        "protected_link": {"source": failed_component, "target": protected_consumer},
        "original_blast_radius": before["blast_radius"],
        "reduced_blast_radius": after["blast_radius"],
        "systems_saved": len(saved),
        "saved_components": saved,
        "original_direct_impact": before["direct_impact"],
        "original_indirect_impact": before["indirect_impact"],
        "protection_options": ["Queue", "Retry process", "Cache", "Backup route"],
        "explanation": "The protection layer isolates this dependency link and recalculates failure propagation without changing the stored architecture.",
    }
