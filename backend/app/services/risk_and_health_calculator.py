import networkx as nx
from app.services.failure_impact_analyzer import calculate_impact


def risk_level(score: int) -> str:
    return "CRITICAL" if score >= 81 else "HIGH" if score >= 61 else "MEDIUM" if score >= 31 else "LOW"


def calculate_risks(graph: nx.DiGraph) -> list[dict]:
    total = max(1, len(graph) - 1)
    centrality = nx.betweenness_centrality(graph)
    app_count = max(1, sum(1 for _, d in graph.nodes(data=True) if d.get("type") == "application"))
    results = []
    for node in graph:
        impact = calculate_impact(graph, node)
        app_impact = len(impact["affected_applications"])
        depth = max(impact["distances"].values(), default=0)
        depth_norm = min(depth / max(1, len(graph) - 1), 1)
        score = round(100 * (.40 * impact["blast_radius"] / total + .25 * app_impact / app_count + .20 * centrality[node] + .15 * depth_norm))
        reasons = []
        if impact["blast_radius"] / total >= .35: reasons.append("Large downstream blast radius")
        if centrality[node] >= .1: reasons.append("High centrality")
        if app_impact: reasons.append(f"Can affect {app_impact} application(s)")
        results.append({"name": node, "type": graph.nodes[node]["type"], "score": score, "level": risk_level(score),
                        "blast_radius": impact["blast_radius"], "applications_affected": app_impact, "reasons": reasons or ["Limited graph impact"]})
    results.sort(key=lambda item: (-item["score"], item["name"]))
    return results


def find_potential_spofs(graph: nx.DiGraph, risks: list[dict]) -> list[dict]:
    articulation = set(nx.articulation_points(graph.to_undirected())) if len(graph) > 1 else set()
    threshold = max(2, round((len(graph) - 1) * .3))
    candidates = []
    for risk in risks:
        reasons = []
        if risk["blast_radius"] >= threshold: reasons.append("high downstream reach")
        if risk["name"] in articulation: reasons.append("central graph articulation point")
        if reasons:
            candidates.append({"name": risk["name"], "blast_radius": risk["blast_radius"], "reason": " + ".join(reasons), "label": "Potential SPOF"})
    return candidates


def calculate_health(graph: nx.DiGraph, risks: list[dict], cycles: list, spofs: list) -> dict:
    high = sum(1 for risk in risks if risk["level"] in {"HIGH", "CRITICAL"})
    score = max(0, round(100 - min(25, len(cycles) * 10) - min(30, len(spofs) * 6) - min(25, high * 5)))
    positives, warnings = [], []
    (positives if not cycles else warnings).append("No circular dependencies" if not cycles else f"{len(cycles)} circular dependency cycle(s)")
    (positives if not spofs else warnings).append("No potential single points of failure" if not spofs else f"{len(spofs)} potential single point(s) of failure")
    (positives if not high else warnings).append("No high-risk components" if not high else f"{high} high or critical-risk component(s)")
    return {"score": score, "label": "RIP Architecture Health Score", "positive_findings": positives, "warnings": warnings,
            "disclaimer": "A deterministic project metric, not a universal industry standard."}
