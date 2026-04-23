from typing import Any

SUPPORTED_VERSIONS = (1, 2)
DEFAULT_API_VERSION = 1

DEPRECATION_HEADERS = {
    "Deprecation": "true",
    "Sunset": "Tue, 30 Sep 2026 00:00:00 GMT",
    "Warning": '299 - "API v1 is deprecated and will be removed on 2026-09-30. Please migrate to v2."',
    "Link": '</docs/migration-plan>; rel="deprecation"; type="text/markdown"',
}

USERS_V1: list[dict[str, Any]] = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]

USERS_V2: list[dict[str, Any]] = [
    {"id": 1, "full_name": "Alice Nguyen", "email": "alice@example.com", "status": "active"},
    {"id": 2, "full_name": "Bob Tran", "email": "bob@example.com", "status": "inactive"},
]
