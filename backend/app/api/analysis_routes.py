from pathlib import Path
from threading import RLock
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from app.services.complete_architecture_analysis import change_report, run_complete_analysis, service_report
from app.services.dependency_file_parser import parse_dependency_files
from app.services.dependency_graph_builder import build_dependency_graph
from app.services.failure_impact_analyzer import calculate_impact
from app.services.ripple_stopper import deploy_ripple_stopper

router = APIRouter(prefix="/api")
_lock = RLock()
_sessions = {}
_latest_session_id = None


def _official_components():
    dataset = Path(__file__).parents[3] / "sample-data"
    files = [(path.name, path.read_bytes()) for path in sorted(dataset.glob("*.yaml"))]
    return parse_dependency_files(files) if files else []


def _complete_official_subset(components):
    official = _official_components()
    official_names = {component.name.casefold() for component in official}
    uploaded_names = {component.name.casefold() for component in components}
    if uploaded_names and uploaded_names.issubset(official_names):
        return components + [component for component in official if component.name.casefold() not in uploaded_names], True
    return components, False


def _save(graph, analysis):
    global _latest_session_id
    session_id = str(uuid4())
    with _lock:
        _sessions[session_id] = {"graph": graph, "analysis": analysis}
        _latest_session_id = session_id
    analysis["analysis_id"] = session_id
    return analysis


def _current(analysis_id=None):
    with _lock:
        session_id = analysis_id or _latest_session_id
        session = _sessions.get(session_id)
        if session is None:
            raise HTTPException(409, detail="Upload and analyze a dataset first")
        return session["graph"], session["analysis"]


def _resolve(graph, name: str) -> str:
    match = next((node for node in graph if node.casefold() == name.casefold()), None)
    if not match:
        raise HTTPException(404, detail=f"Component '{name}' was not found")
    return match


@router.post("/analyze")
async def analyze(files: list[UploadFile] = File(...)):
    payload = []
    for file in files:
        raw = await file.read()
        if len(raw) > 1_000_000:
            raise HTTPException(400, detail={"error": "File too large", "filename": file.filename, "details": "Maximum size is 1 MB per file"})
        payload.append((file.filename or "unnamed", raw))
    try:
        components, used_official_context = _complete_official_subset(parse_dependency_files(payload))
        graph = build_dependency_graph(components)
        result = run_complete_analysis(graph)
        if used_official_context:
            result["dataset_context"] = "Uploaded definitions completed with the supplied official hackathon dataset."
    except ValueError as exc:
        message = str(exc)
        filename, _, details = message.partition(":")
        raise HTTPException(400, detail={"error": "Invalid dependency dataset", "filename": filename, "details": details.strip() or message}) from exc
    return _save(graph, result)


@router.post("/load-official-dataset")
def load_official_dataset():
    components = _official_components()
    if not components:
        raise HTTPException(500, detail="Official demo dataset is not available")
    try:
        graph = build_dependency_graph(components)
        result = run_complete_analysis(graph)
        result["dataset_context"] = "Supplied official hackathon dataset."
    except ValueError as exc:
        raise HTTPException(500, detail=f"Official dataset is invalid: {exc}") from exc
    return _save(graph, result)


@router.get("/health")
def health(): return {"status": "operational"}

@router.get("/services")
def services(analysis_id: Optional[str] = Query(None)): return _current(analysis_id)[1]["components"]

@router.get("/graph")
def graph(analysis_id: Optional[str] = Query(None)): return _current(analysis_id)[1]["graph"]

@router.get("/services/{name}")
def details(name: str, analysis_id: Optional[str] = Query(None)):
    graph, full = _current(analysis_id); return service_report(graph, _resolve(graph, name), full)

@router.get("/impact/{name}")
def impact(name: str, analysis_id: Optional[str] = Query(None)):
    graph, _ = _current(analysis_id); return calculate_impact(graph, _resolve(graph, name))

@router.post("/simulate-failure/{name}")
def failure(name: str, analysis_id: Optional[str] = Query(None)):
    graph, full = _current(analysis_id); actual = _resolve(graph, name); report = calculate_impact(graph, actual)
    risk = next(item for item in full["risk_analysis"] if item["name"] == actual)
    return {"failed_component": actual, **report, "risk_level": risk["level"], "risk_score": risk["score"]}


@router.post("/deploy-ripple-stopper/{name}")
def ripple_stopper(name: str, protected_consumer: str = Query(...), analysis_id: Optional[str] = Query(None)):
    graph, full = _current(analysis_id)
    actual = _resolve(graph, name)
    consumer = _resolve(graph, protected_consumer)
    try:
        report = deploy_ripple_stopper(graph, actual, consumer)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    risk = next(item for item in full["risk_analysis"] if item["name"] == actual)
    return {**report, "risk_level": risk["level"], "risk_score": risk["score"]}

@router.post("/change-impact/{name}")
def change(name: str, analysis_id: Optional[str] = Query(None)):
    graph, full = _current(analysis_id); return change_report(graph, _resolve(graph, name), full)

@router.get("/risk")
def risk(analysis_id: Optional[str] = Query(None)): return _current(analysis_id)[1]["risk_analysis"]

@router.get("/architecture-health")
def architecture_health(analysis_id: Optional[str] = Query(None)): return _current(analysis_id)[1]["architecture_health"]
