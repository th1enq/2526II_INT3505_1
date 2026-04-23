from typing import Any

from api_demo.config import USERS_V1, USERS_V2, SUPPORTED_VERSIONS


def users_payload(version: int) -> dict[str, Any]:
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

    return {"error": "Unsupported API version", "supported_versions": list(SUPPORTED_VERSIONS)}
