# Simple File Guide for the Panel

## Start here

- `README.md` — explains the problem, solution, architecture, setup, algorithms, and APIs.
- `docker-compose.yml` — starts the complete frontend and backend together.
- `sample-data/` — contains ready-to-upload example dependency files.

## Backend: where the calculations happen

- `dependency_file_parser.py` — reads and validates the uploaded YAML files.
- `dependency_graph_builder.py` — connects components in a NetworkX dependency graph.
- `architecture_analyzer.py` — finds connected components, depth, cycles, and critical paths.
- `failure_impact_analyzer.py` — calculates direct impact, indirect impact, and blast radius.
- `risk_and_health_calculator.py` — calculates risk, potential SPOFs, and architecture health.
- `test_plan_generator.py` — recommends what to test after a failure or change.
- `complete_architecture_analysis.py` — combines all calculations into the dashboard result.
- `analysis_routes.py` — provides the backend API endpoints used by the dashboard.
- `main.py` — starts the FastAPI backend.
- `test_dependency_analysis.py` — proves that parsing and graph calculations work correctly.

## Frontend: what the user sees

- `RipDashboard.jsx` — assembles the complete React dashboard and user workflow.
- `BrandHeader.jsx` — displays RIP branding and navigation.
- `DatasetUploadPanel.jsx` — lets users select and analyze YAML files.
- `RequirementGraphViewer.jsx` — shows the dependency graph and Ripple Stopper.
- `ServiceDetailsPanel.jsx` — explains the selected component and its risk.
- `RiskAnalysisTable.jsx` — ranks all components by calculated risk.
- `dependencyAnalysisApi.js` — sends frontend requests to the FastAPI backend.
- `styles.css` — provides the brown, gold, and cream visual design.

## One-line presentation

“The YAML parser reads architecture facts, the graph builder connects them, the analyzers calculate propagation and risk, and the React dashboard turns those calculations into actionable engineering decisions.”
