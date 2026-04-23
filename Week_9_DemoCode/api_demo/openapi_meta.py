from typing import Any

OPENAPI_META: dict[str, dict[str, Any]] = {
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
    "openapi_spec": {
        "summary": "Get OpenAPI spec",
        "description": "Returns auto-generated OpenAPI 3.0.3 document.",
        "responses": {"200": {"description": "OpenAPI document"}},
    },
    "swagger_ui": {
        "summary": "Swagger UI",
        "description": "Interactive API docs powered by Swagger UI.",
        "responses": {"200": {"description": "Swagger UI HTML"}},
    },
}
