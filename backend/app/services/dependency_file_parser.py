from pathlib import Path
from typing import Iterable, Tuple
import yaml
from pydantic import ValidationError
from app.models.analysis_models import ComponentDefinition

ALLOWED_EXTENSIONS = {".yaml", ".yml"}
TYPE_ALIASES = {
    "api": "service",
    "service/api": "service",
    "external": "external_system",
    "external system": "external_system",
    "app": "application",
    "db": "database",
}


def parse_dependency_files(files: Iterable[Tuple[str, bytes]]) -> list[ComponentDefinition]:
    components: list[ComponentDefinition] = []
    seen: set[str] = set()
    for filename, raw in files:
        if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
            raise ValueError(f"{filename}: only .yaml and .yml files are accepted")
        try:
            data = yaml.safe_load(raw.decode("utf-8"))
        except (yaml.YAMLError, UnicodeDecodeError) as exc:
            raise ValueError(f"{filename}: invalid YAML - {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"{filename}: YAML root must be an object")
        if "service" not in data and "name" not in data:
            raise ValueError(f"{filename}: required field 'service' is missing")
        name = str(data.get("service", data.get("name", ""))).strip()
        key = name.casefold()
        if key in seen:
            raise ValueError(f"{filename}: duplicate component definition '{name}'")
        seen.add(key)
        kind = TYPE_ALIASES.get(str(data.get("type", "service")).lower(), str(data.get("type", "service")).lower())
        payload = {"name": name, "type": kind, "dependencies": data.get("dependencies") or [], "consumers": data.get("consumers") or []}
        if not isinstance(payload["dependencies"], list) or not isinstance(payload["consumers"], list):
            raise ValueError(f"{filename}: dependencies and consumers must be lists")
        try:
            components.append(ComponentDefinition.model_validate(payload))
        except ValidationError as exc:
            raise ValueError(f"{filename}: {exc.errors()[0]['msg']}") from exc
    if not components:
        raise ValueError("No dependency files were uploaded")
    return components
