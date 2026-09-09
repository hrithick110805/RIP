from app.models.analysis_models import ComponentDefinition
from app.services.dependency_file_parser import parse_dependency_files
from app.services.dependency_graph_builder import build_dependency_graph
from app.services.failure_impact_analyzer import calculate_impact
from app.services.architecture_analyzer import analyze_structure
from app.services.risk_and_health_calculator import calculate_risks


def yaml_file(name, text): return (name, text.encode())


def test_parses_multiple_files_and_empty_dependencies():
    items = parse_dependency_files([yaml_file("a.yaml", "service: A\ndependencies: [B]"), yaml_file("b.yml", "service: B\ndependencies: []")])
    assert [item.name for item in items] == ["A", "B"]


def test_graph_direction_and_direct_indirect_impact():
    components = [ComponentDefinition(name="Portal", type="application", dependencies=["Orders"]), ComponentDefinition(name="Orders", dependencies=["Inventory"]), ComponentDefinition(name="Inventory")]
    graph = build_dependency_graph(components)
    assert graph.has_edge("Orders", "Inventory")
    impact = calculate_impact(graph, "Inventory")
    assert impact["direct_impact"] == ["Orders"]
    assert impact["indirect_impact"] == ["Portal"]
    assert impact["blast_radius"] == 2


def test_unknown_dependency_becomes_unresolved_node():
    graph = build_dependency_graph([ComponentDefinition(name="A", dependencies=["Missing"] )])
    assert graph.nodes["Missing"]["type"] == "unresolved"


def test_cycle_detection_terminates_impact_walk():
    graph = build_dependency_graph([ComponentDefinition(name="A", dependencies=["B"]), ComponentDefinition(name="B", dependencies=["A"])])
    assert analyze_structure(graph)["cycles"] == [["A", "B", "A"]]
    assert calculate_impact(graph, "A")["blast_radius"] == 1


def test_risk_scores_stay_in_range_and_are_ranked():
    graph = build_dependency_graph([ComponentDefinition(name="App", type="application", dependencies=["Core"]), ComponentDefinition(name="Core")])
    risks = calculate_risks(graph)
    assert risks == sorted(risks, key=lambda item: (-item["score"], item["name"]))
    assert all(0 <= item["score"] <= 100 for item in risks)


def test_invalid_yaml_and_duplicate_names_are_clear():
    import pytest
    with pytest.raises(ValueError, match="invalid YAML"):
        parse_dependency_files([yaml_file("bad.yaml", "service: [")])
    with pytest.raises(ValueError, match="duplicate"):
        parse_dependency_files([yaml_file("a.yaml", "service: Same"), yaml_file("b.yaml", "service: Same")])


def test_official_hackathon_dataset_matches_documented_counts_and_inventory_impact():
    from pathlib import Path
    dataset = Path(__file__).parents[2] / "sample-data"
    files = [(path.name, path.read_bytes()) for path in dataset.glob("*.yaml")]
    graph = build_dependency_graph(parse_dependency_files(files))
    counts = {kind: sum(1 for _, data in graph.nodes(data=True) if data["type"] == kind)
              for kind in ("service", "application", "database", "external_system", "unresolved")}
    assert len(graph) == 15
    assert counts == {"service": 9, "application": 3, "database": 2, "external_system": 1, "unresolved": 0}
    impact = calculate_impact(graph, "Inventory Service")
    assert impact["direct_impact"] == ["Cart Service", "Order Service"]
    assert impact["indirect_impact"] == ["Customer Portal", "Invoice Service"]


def test_inventory_only_upload_uses_supplied_context_and_documented_change_scenario():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    inventory_yaml = b"service: Inventory Service\ntype: API\ndependencies: [Product Catalog Service, Product DB]\nconsumers: [Cart Service, Order Service]"
    analyzed = client.post("/api/analyze", files={"files": ("inventory-service.yaml", inventory_yaml, "application/yaml")})
    assert analyzed.status_code == 200
    result = analyzed.json()
    assert result["metrics"]["total_components"] == 15
    changed = client.post(f"/api/change-impact/Inventory%20Service?analysis_id={result['analysis_id']}")
    assert changed.status_code == 200
    report = changed.json()
    assert report["direct_impact"] == ["Cart Service", "Order Service"]
    assert report["indirect_impact"] == ["Customer Portal", "Mobile App", "Invoice Service", "Reporting Service"]
    assert report["blast_radius"] == 6


def test_ripple_stopper_protects_payment_to_order_link_without_mutating_graph():
    from pathlib import Path
    from app.services.ripple_stopper import deploy_ripple_stopper
    dataset = Path(__file__).parents[2] / "sample-data"
    files = [(path.name, path.read_bytes()) for path in dataset.glob("*.yaml")]
    graph = build_dependency_graph(parse_dependency_files(files))
    report = deploy_ripple_stopper(graph, "Payment Service", "Order Service")
    assert report["original_blast_radius"] == 3
    assert report["reduced_blast_radius"] == 0
    assert report["systems_saved"] == 3
    assert report["saved_components"] == ["Customer Portal", "Invoice Service", "Order Service"]
    assert graph.has_edge("Order Service", "Payment Service")
