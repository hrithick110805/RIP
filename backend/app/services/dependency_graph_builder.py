import networkx as nx
from app.models.analysis_models import ComponentDefinition


def build_dependency_graph(components: list[ComponentDefinition]) -> nx.DiGraph:
    graph = nx.DiGraph()
    canonical = {component.name.casefold(): component.name for component in components}
    for component in components:
        graph.add_node(component.name, type=component.type, unresolved=False)
    def ensure(name: str) -> str:
        clean = str(name).strip()
        actual = canonical.get(clean.casefold(), clean)
        if actual not in graph:
            graph.add_node(actual, type="unresolved", unresolved=True)
        return actual
    for component in components:
        for dependency in component.dependencies:
            graph.add_edge(component.name, ensure(dependency), relationship="depends_on")
        for consumer in component.consumers:
            graph.add_edge(ensure(consumer), component.name, relationship="depends_on")
    return graph
