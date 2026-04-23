from typing import Any

from flask import Flask

from api_demo.openapi_meta import OPENAPI_META


HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
IGNORED_ENDPOINTS = {"static"}


def _endpoint_key(endpoint_name: str) -> str:
    return endpoint_name.split(".")[-1]


def _convert_flask_path_to_openapi(path: str) -> str:
    converted = path
    converters = ["int", "float", "path", "string", "uuid", "any"]

    for converter in converters:
        token = f"<{converter}:"
        while token in converted:
            start = converted.index(token)
            end = converted.index(">", start)
            param_name = converted[start + len(token): end]
            converted = converted[:start] + "{" + param_name + "}" + converted[end + 1:]

    while "<" in converted and ">" in converted:
        start = converted.index("<")
        end = converted.index(">", start)
        param_name = converted[start + 1: end]
        converted = converted[:start] + "{" + param_name + "}" + converted[end + 1:]

    return converted


def _extract_path_parameters(path: str) -> list[dict[str, Any]]:
    parameters: list[dict[str, Any]] = []
    segments = path.split("{")

    for segment in segments[1:]:
        name = segment.split("}", maxsplit=1)[0]
        if not name:
            continue
        parameters.append(
            {
                "name": name,
                "in": "path",
                "required": True,
                "schema": {"type": "integer" if name == "version" else "string"},
            }
        )

    return parameters


def generate_openapi_spec(app: Flask) -> dict[str, Any]:
    paths: dict[str, Any] = {}

    for rule in app.url_map.iter_rules():
        endpoint_name = rule.endpoint
        endpoint_key = _endpoint_key(endpoint_name)

        if endpoint_key in IGNORED_ENDPOINTS:
            continue

        methods = sorted(method for method in rule.methods if method in HTTP_METHODS)
        if not methods:
            continue

        openapi_path = _convert_flask_path_to_openapi(rule.rule)
        path_item = paths.setdefault(openapi_path, {})
        meta = OPENAPI_META.get(endpoint_key, {})
        path_parameters = _extract_path_parameters(openapi_path)

        for method in methods:
            operation: dict[str, Any] = {
                "operationId": f"{endpoint_key}_{method.lower()}",
                "summary": meta.get("summary", endpoint_key.replace("_", " ").title()),
                "description": meta.get("description", "Auto-generated from Flask routes."),
                "responses": meta.get("responses", {"200": {"description": "Success"}}),
            }

            parameters = [*path_parameters, *meta.get("parameters", [])]
            if parameters:
                operation["parameters"] = parameters

            if "requestBody" in meta and method in {"POST", "PUT", "PATCH"}:
                operation["requestBody"] = meta["requestBody"]

            if endpoint_key.endswith("_v1"):
                operation["deprecated"] = True

            path_item[method.lower()] = operation

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Flask API Versioning Demo",
            "version": "2.0.0",
            "description": "Auto-generated OpenAPI spec from Flask app code.",
        },
        "servers": [{"url": "http://127.0.0.1:5000"}],
        "paths": paths,
    }
