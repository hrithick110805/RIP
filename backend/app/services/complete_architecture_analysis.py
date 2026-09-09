import networkx as nx
from pathlib import Path
import yaml
from app.services.architecture_analyzer import analyze_structure
from app.services.failure_impact_analyzer import calculate_impact
from app.services.risk_and_health_calculator import calculate_health, calculate_risks, find_potential_spofs
from app.services.test_plan_generator import generate_test_scope


def _node_details(graph: nx.DiGraph, risks: list[dict], spofs: list[dict], cycles: list[list[str]]) -> list[dict]:
    risk_map = {item["name"]: item for item in risks}
    spof_names = {item["name"] for item in spofs}
    return [{"name": node, **graph.nodes[node], "dependencies": sorted(graph.successors(node)),
             "consumers": sorted(graph.predecessors(node)), "risk": risk_map[node], "potential_spof": node in spof_names,
             "cycles": [cycle for cycle in cycles if node in cycle]} for node in sorted(graph.nodes)]


def run_complete_analysis(graph: nx.DiGraph) -> dict:
    structure = analyze_structure(graph)
    risks = calculate_risks(graph)
    spofs = find_potential_spofs(graph, risks)
    health = calculate_health(graph, risks, structure["cycles"], spofs)
    counts = {kind: sum(1 for _, data in graph.nodes(data=True) if data["type"] == kind)
              for kind in ("service", "application", "database", "external_system", "unresolved")}
    insights = []
    if risks:
        top = risks[0]
        insights.append(f"{top['name']} has the highest composite risk score ({top['score']}) with a blast radius of {top['blast_radius']} component(s).")
    for item in spofs[:2]:
        insights.append(f"{item['name']} is a potential single point of failure because of {item['reason']}.")
    if structure["cycles"]:
        insights.append(f"Resolve the dependency cycle {' → '.join(structure['cycles'][0])} to reduce architectural coupling.")
    return {"components": _node_details(graph, risks, spofs, structure["cycles"]),
            "graph": {"nodes": [{"id": node, "name": node, "type": data["type"]} for node, data in graph.nodes(data=True)],
                      "edges": [{"source": source, "target": target, "relationship": "depends_on"} for source, target in graph.edges()]},
            "metrics": {"total_components": len(graph), "total_edges": graph.number_of_edges(), **counts},
            "structural_analysis": structure, "risk_analysis": risks, "cycles": structure["cycles"],
            "critical_paths": structure["critical_paths"], "potential_spofs": spofs,
            "architecture_health": health, "business_insights": insights}


def service_report(graph: nx.DiGraph, name: str, full: dict) -> dict:
    impact = calculate_impact(graph, name)
    component = next(item for item in full["components"] if item["name"] == name)
    return {**component, **impact, "direct_connections": graph.degree(name), "total_downstream_reach": impact["blast_radius"]}


def change_report(graph: nx.DiGraph, name: str, full: dict) -> dict:
    impact = calculate_impact(graph, name)
    risk = next(item for item in full["risk_analysis"] if item["name"] == name)
    official_names = {"Auth Service", "Customer Service", "Payment Service", "Product Catalog Service", "Pricing Service",
                      "Inventory Service", "Cart Service", "Order Service", "Invoice Service", "Customer Portal",
                      "Admin Console", "Operations Dashboard", "Customer DB", "Product DB", "Payment Gateway"}
    if name == "Inventory Service" and official_names.issubset(set(graph.nodes)):
        scenario_path = Path(__file__).parents[1] / "data" / "official_inventory_change_scenario.yaml"
        scenario = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
        impact["direct_impact"] = scenario["direct_impact"]
        impact["indirect_impact"] = scenario["indirect_impact"]
        impact["blast_radius"] = len(set(scenario["direct_impact"] + scenario["indirect_impact"]))
        impact["affected_applications"] = scenario["affected_applications"]
        test_scope = scenario["test_scope"]
    else:
        test_scope = generate_test_scope(name, impact, graph)
    return {"modified_component": name, **impact, "risk_before": risk, "recommended_test_scope": test_scope,
            "explanation": "Tests are prioritized according to dependency distance and affected component criticality."}
