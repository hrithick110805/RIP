WORKFLOW_TESTS = {
    "Inventory Service": "Product availability validation",
    "Cart Service": "Cart update flow",
    "Order Service": "Order placement",
    "Customer Portal": "Checkout flow",
    "Invoice Service": "Invoice generation",
    "Operations Dashboard": "Reporting data refresh",
}


def _test_name(name: str, indirect: bool = False) -> str:
    if name in WORKFLOW_TESTS:
        return WORKFLOW_TESTS[name]
    prefix = "Validate indirect workflow through" if indirect else "Validate integration with"
    return f"{prefix} {name}"


def generate_test_scope(component: str, impact: dict, graph) -> list[dict]:
    direct = impact["direct_impact"]
    indirect = impact["indirect_impact"]
    return [
        {"priority": "P0 — Critical", "tests": [_test_name(component)] + (["Inventory stock change handling"] if component == "Inventory Service" else [])},
        {"priority": "P1 — High", "tests": [_test_name(name) for name in direct]},
        {"priority": "P2 — Medium", "tests": [_test_name(name, True) for name in indirect]},
    ]
