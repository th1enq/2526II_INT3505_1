from datetime import datetime, timezone
from typing import Dict, Any

from flask import Flask, jsonify, request, make_response, Response

app = Flask(__name__)

USERS_V1 = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]

USERS_V2 = [
    {"id": 1, "full_name": "Alice Nguyen", "email": "alice@example.com", "status": "active"},
    {"id": 2, "full_name": "Bob Tran", "email": "bob@example.com", "status": "inactive"},
]

OPENAPI_META: Dict[str, Dict[str, Any]] = {
    "health_check": {
        "summary": "Health check",
        "description": "Returns service status and UTC timestamp.",
        "responses": {
            "200": {
                "description": "Service is healthy",
                "content": {
                    "application/json": {
                        "example": {"status": "ok", "timestamp": "2026-04-23T12:00:00+00:00"}
                    }
                },
            }
        },
    },
    "users_by_url_version": {
        "summary": "Get users by URL version",
        "description": "Versioning by URL path: /api/v1/users or /api/v2/users.",
        "responses": {
            "200": {"description": "Users payload for selected version"},
            "400": {"description": "Unsupported API version"},
        },
    },
    "users_by_header_or_query_version": {
        "summary": "Get users by header/query version",
        "description": "Versioning by query param, X-API-Version, or Accept media type.",
        "parameters": [
            {
                "in": "query",
                "name": "version",
                "required": False,
                "schema": {"type": "integer", "enum": [1, 2]},
                "description": "API version by query parameter.",
            },
            {
                "in": "header",
                "name": "X-API-Version",
                "required": False,
                "schema": {"type": "string", "example": "v2"},
                "description": "API version header.",
            },
            {
                "in": "header",
                "name": "Accept",
                "required": False,
                "schema": {"type": "string", "example": "application/vnd.demo.v2+json"},
                "description": "Media type based versioning.",
            },
        ],
        "responses": {
            "200": {"description": "Users payload for selected version"},
            "400": {"description": "Unsupported API version"},
        },
    },
    "create_payment_v1": {
        "summary": "Create payment (v1, deprecated)",
        "description": "Legacy payment API. Deprecated and scheduled for sunset.",
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "example": {"amount": 100, "currency": "USD"}
                }
            },
        },
        "responses": {
            "201": {"description": "Legacy payment created"},
            "400": {"description": "Invalid request"},
        },
    },
    "create_payment_v2": {
        "summary": "Create payment (v2)",
        "description": "New payment API with required customer_id and richer lifecycle.",
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "example": {"amount": 100, "currency": "USD", "customer_id": "cus_123"}
                }
            },
        },
        "responses": {
            "201": {"description": "Payment authorized"},
            "400": {"description": "Missing required fields"},
        },
    },
}


def _deprecation_meta() -> Dict[str, str]:
    return {
        "deprecation": "true",
        "sunset": "Tue, 30 Sep 2026 00:00:00 GMT",
        "warning": '299 - "API v1 is deprecated and will be removed on 2026-09-30. Please migrate to v2."',
        "link": '</docs/migration-plan>; rel="deprecation"; type="text/markdown"',
    }


def _attach_deprecation_headers(response):
    meta = _deprecation_meta()
    response.headers["Deprecation"] = meta["deprecation"]
    response.headers["Sunset"] = meta["sunset"]
    response.headers["Warning"] = meta["warning"]
    response.headers["Link"] = meta["link"]
    return response


def _parse_version_from_header(value: str | None) -> int | None:
    if not value:
        return None
    normalized = value.strip().lower()
    if normalized in {"1", "v1"}:
        return 1
    if normalized in {"2", "v2"}:
        return 2
    if normalized.startswith("application/vnd.demo.v") and normalized.endswith("+json"):
        try:
            version_str = normalized.split(".v", maxsplit=1)[1].split("+", maxsplit=1)[0]
            return int(version_str)
        except (ValueError, IndexError):
            return None
    return None


def resolve_version() -> int:
    query_version = request.args.get("version")
    if query_version:
        try:
            return int(query_version)
        except ValueError:
            return -1

    accept_version = _parse_version_from_header(request.headers.get("Accept"))
    if accept_version is not None:
        return accept_version

    explicit_header_version = _parse_version_from_header(request.headers.get("X-API-Version"))
    if explicit_header_version is not None:
        return explicit_header_version

    return 1


def users_payload(version: int) -> Dict[str, Any]:
    if version == 1:
        return {
            "version": "v1",
            "users": USERS_V1,
            "schema": {"id": "int", "name": "string"},
        }
    if version == 2:
        return {
            "version": "v2",
            "users": USERS_V2,
            "schema": {
                "id": "int",
                "full_name": "string",
                "email": "string",
                "status": "string",
            },
        }
    return {"error": "Unsupported API version", "supported_versions": [1, 2]}


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


def _extract_path_parameters(path: str) -> list[Dict[str, Any]]:
    params: list[Dict[str, Any]] = []
    segments = path.split("{")
    for segment in segments[1:]:
        name = segment.split("}", maxsplit=1)[0]
        if name:
            params.append(
                {
                    "name": name,
                    "in": "path",
                    "required": True,
                    "schema": {"type": "integer" if name == "version" else "string"},
                }
            )
    return params


def generate_openapi_spec() -> Dict[str, Any]:
    paths: Dict[str, Any] = {}
    ignored_endpoints = {"static", "openapi_spec"}

    for rule in app.url_map.iter_rules():
        if rule.endpoint in ignored_endpoints:
            continue

        methods = sorted(method for method in rule.methods if method in {"GET", "POST", "PUT", "PATCH", "DELETE"})
        if not methods:
            continue

        openapi_path = _convert_flask_path_to_openapi(rule.rule)
        path_item = paths.setdefault(openapi_path, {})
        meta = OPENAPI_META.get(rule.endpoint, {})
        path_params = _extract_path_parameters(openapi_path)

        for method in methods:
            operation: Dict[str, Any] = {
                "operationId": f"{rule.endpoint}_{method.lower()}",
                "summary": meta.get("summary", rule.endpoint.replace("_", " ").title()),
                "description": meta.get("description", "Auto-generated from Flask routes."),
                "responses": meta.get("responses", {"200": {"description": "Success"}}),
            }

            parameters = list(path_params)
            for param in meta.get("parameters", []):
                parameters.append(param)
            if parameters:
                operation["parameters"] = parameters

            if "requestBody" in meta and method in {"POST", "PUT", "PATCH"}:
                operation["requestBody"] = meta["requestBody"]

            if rule.endpoint.endswith("_v1"):
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


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/v<int:version>/users")
def users_by_url_version(version: int):
    payload = users_payload(version)
    status_code = 200 if "error" not in payload else 400
    response = make_response(jsonify(payload), status_code)
    if version == 1 and status_code == 200:
        _attach_deprecation_headers(response)
    return response


@app.get("/api/users")
def users_by_header_or_query_version():
    version = resolve_version()
    payload = users_payload(version)
    status_code = 200 if "error" not in payload else 400
    response = make_response(jsonify(payload), status_code)
    if version == 1 and status_code == 200:
        _attach_deprecation_headers(response)
    return response


@app.post("/api/v1/payments")
def create_payment_v1():
    body = request.get_json(silent=True) or {}
    amount = body.get("amount")
    if amount is None:
        response = make_response(jsonify({"error": "amount is required"}), 400)
        return _attach_deprecation_headers(response)

    response = make_response(
        jsonify(
            {
                "version": "v1",
                "payment_id": "pay_legacy_001",
                "amount": amount,
                "currency": body.get("currency", "USD"),
                "status": "created",
            }
        ),
        201,
    )
    return _attach_deprecation_headers(response)


@app.post("/api/v2/payments")
def create_payment_v2():
    body = request.get_json(silent=True) or {}
    amount = body.get("amount")
    currency = body.get("currency")
    customer_id = body.get("customer_id")

    missing = [field for field in ("amount", "currency", "customer_id") if body.get(field) is None]
    if missing:
        return jsonify({"error": "missing required fields", "fields": missing}), 400

    return (
        jsonify(
            {
                "version": "v2",
                "id": "pay_2026_001",
                "amount": amount,
                "currency": currency,
                "customer_id": customer_id,
                "status": "authorized",
                "links": {
                    "self": "/api/v2/payments/pay_2026_001",
                    "capture": "/api/v2/payments/pay_2026_001/capture",
                },
            }
        ),
        201,
    )


@app.get("/openapi.json")
def openapi_spec():
    return jsonify(generate_openapi_spec())


@app.get("/docs")
def swagger_ui():
        html = """
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Flask API Docs</title>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
        <style>
            html { box-sizing: border-box; overflow-y: scroll; }
            *, *:before, *:after { box-sizing: inherit; }
            body { margin: 0; background: #fafafa; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js" crossorigin></script>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js" crossorigin></script>
        <script>
            window.onload = function () {
                window.ui = SwaggerUIBundle({
                    url: '/openapi.json',
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
                    layout: 'BaseLayout'
                });
            };
        </script>
    </body>
</html>
"""
        return Response(html, mimetype="text/html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
