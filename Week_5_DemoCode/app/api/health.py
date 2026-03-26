from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health() -> Any:
    """Simple health check
    ---
    tags:
      - System
    responses:
      200:
        description: API is healthy
    """
    return jsonify({"status": "ok"})
