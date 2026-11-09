"""Minimal JSON Schema validator for the foundation's own contracts. Part of the project foundation. Stdlib only.

Supports exactly the subset the schemas in .foundation/schemas use: type (incl. lists), const, enum, required,
properties, additionalProperties: false, items, minLength, minimum, pattern. Anything else in a schema is an
error, so a schema can't silently ask for checks this validator doesn't do.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

SUPPORTED = {"$schema", "$id", "title", "description", "type", "const", "enum", "required", "properties",
             "additionalProperties", "items", "minLength", "minimum", "pattern"}
TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool, "null": type(None),
    "integer": int, "number": (int, float),
}


def _is_type(value, name: str) -> bool:
    if name in ("integer", "number") and isinstance(value, bool):
        return False
    return isinstance(value, TYPES[name])


def validate(value, schema: dict, path: str = "$") -> list[str]:
    unknown = set(schema) - SUPPORTED
    if unknown:
        return [f"{path}: schema uses unsupported keywords {sorted(unknown)}"]
    errors: list[str] = []
    if "type" in schema:
        allowed = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(value, t) for t in allowed):
            return [f"{path}: expected {'/'.join(allowed)}, got {type(value).__name__}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must be {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: shorter than {schema['minLength']} characters")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: doesn't match {schema['pattern']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool) and "minimum" in schema:
        if value < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required '{key}'")
        props = schema.get("properties", {})
        for key, sub in value.items():
            if key in props:
                errors += validate(sub, props[key], f"{path}.{key}")
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected property '{key}'")
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errors += validate(item, schema["items"], f"{path}[{i}]")
    return errors


def load_schema(root: Path, name: str) -> dict:
    return json.loads((root / ".foundation" / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))


def extract_block(text: str, tag: str) -> tuple[object | None, str | None]:
    """Find a ```<tag> fenced JSON block. Returns (data, error)."""
    m = re.search(rf"```{re.escape(tag)}[ \t]*\r?\n(.*?)\r?\n[ \t]*```", text or "", flags=re.S)
    if not m:
        return None, f"no ```{tag} block found"
    try:
        return json.loads(m.group(1)), None
    except json.JSONDecodeError as e:
        return None, f"```{tag} block isn't valid JSON: {e}"
