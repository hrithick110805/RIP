from typing import Any, Dict, List, Literal
from pydantic import BaseModel, Field

ComponentType = Literal["service", "application", "database", "external_system", "unresolved"]


class ComponentDefinition(BaseModel):
    name: str = Field(min_length=1)
    type: ComponentType = "service"
    dependencies: List[str] = Field(default_factory=list)
    consumers: List[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    components: List[Dict[str, Any]]
    graph: Dict[str, Any]
    metrics: Dict[str, Any]
    structural_analysis: Dict[str, Any]
    risk_analysis: List[Dict[str, Any]]
    cycles: List[List[str]]
    critical_paths: List[Dict[str, Any]]
    potential_spofs: List[Dict[str, Any]]
    architecture_health: Dict[str, Any]
    business_insights: List[str]
